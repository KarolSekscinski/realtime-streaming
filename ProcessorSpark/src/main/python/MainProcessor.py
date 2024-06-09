import logging
import time
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import current_timestamp
from Settings import Settings

import uuid
from pyspark.sql.functions import udf


class MainProcessor:
    @staticmethod
    def main():
        # This line reads configuration class
        settings_for_spark = Settings()



        # This line creates spark session
        spark = SparkSession.builder \
            .appName(settings_for_spark.spark['appName'][0]['StreamProcessor']) \
            .config("spark.cassandra.connection.host", settings_for_spark.cassandra['host']) \
            .config("spark.cassandra.connection.port", settings_for_spark.cassandra['port']) \
            .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.2.0,"
                                           "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,"
                                           "org.apache.spark:spark-avro_2.12:3.2.0,"
                                           "com.datastax.oss:java-driver-core:4.13.0") \
            .getOrCreate()


        # trades_schema = spark.read.format("avro").load(settings_for_spark.schemas['trades'])
        json_format_schema = open(settings_for_spark.schemas['trades'], "r").read()

        # This line creates UDF for generating UUIDs
        make_uuid = udf(lambda: str(uuid.uuid4()), StringType())

        # This line reads streams from Kafka broker and creates df with columns based on avro schema
        input_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", settings_for_spark.kafka['server_address']) \
            .option("subscribe", settings_for_spark.kafka['topic'][0]['market']) \
            .option("minPartitions", settings_for_spark.kafka['min_partitions'][0]['StreamProcessor']) \
            .option("maxOffsetsPerTrigger", settings_for_spark.spark['max_offsets_per_trigger'][0]['StreamProcessor']) \
            .option("useDeprecatedOffsetFetching", settings_for_spark.spark['deprecated_offsets'][0]['StreamProcessor']) \
            .load()

        # Explode the data from JSON?
        expanded_df = input_df \
            .withColumn("avroData", from_avro(col("value"), json_format_schema).alias("trades")) \
            .selectExpr("avroData.*")
        # .selectExpr("avroData", "explode(data) as col", "type")
        expanded_df.printSchema()

        # Explode the nested data array
        exploded_df = expanded_df \
            .withColumn("trade", explode(col("data"))) \
            .select("trade.*", "type")


        # Rename columns to match their names in Cassandra db
        final_df = exploded_df \
            .withColumn("uuid", make_uuid()) \
            .withColumnRenamed("c", "trade_conditions") \
            .withColumnRenamed("p", "price") \
            .withColumnRenamed("s", "symbol") \
            .withColumnRenamed("t", "trade_ts") \
            .withColumnRenamed("v", "volume") \
            .withColumn("trade_ts", (col("trade_ts") / 1000).cast("timestamp")) \
            .withColumn("ingestion_ts", current_timestamp())

        # Write raw query to Cassandra db - this part could cause bugs
        query = final_df \
            .writeStream \
            .trigger(processingTime='5 seconds') \
            .foreachBatch(lambda batch_df, batch_id:
                          batch_df.write
                          .format("org.apache.spark.sql.cassandra")
                          .options(table=settings_for_spark.cassandra['tables'][0]['trades'],
                                   keyspace=settings_for_spark.cassandra['keyspace'])
                          .mode("append")
                          .save()
                          ) \
            .outputMode("update") \
            .start()

        # Another df with aggregated data - running every 10 seconds
        summary_df = final_df \
            .withColumn("price_x_volume", col("price") * col("volume")) \
            .withWatermark("trade_ts", "10 seconds") \
            .groupby("symbol") \
            .agg(avg("price_x_volume").alias("avg_price_x_volume"))

        # Rename columns in dataframe and add UUIDs before inserting to Cassandra db
        final_summary_df = summary_df \
            .withColumn("uuid", make_uuid()) \
            .withColumn("ingestion_ts", current_timestamp()) \

        # Write second query to Cassandra - this could also lead to bugs
        query2 = final_summary_df \
            .writeStream \
            .trigger(processingTime="10 seconds") \
            .foreachBatch(lambda batch_df, batch_id:
                          batch_df.write
                          .format("org.apache.spark.sql.cassandra")
                          .options(table=settings_for_spark.cassandra['tables'][0]['aggregates'],
                                   keyspace=settings_for_spark.cassandra['keyspace'])
                          .mode("append")
                          .save()
                          ) \
            .outputMode("update") \
            .start()

        # Let query await termination
        spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    MainProcessor().main()
