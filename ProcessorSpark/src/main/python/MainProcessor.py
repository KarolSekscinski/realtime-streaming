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
        # This line creates spark session
        spark = SparkSession.builder \
            .appName("Main Streaming ProcessorSpark") \
            .getOrCreate()

        # This line reads configuration class
        settings_for_spark = Settings()

        # This line load trades schema
        trades_schema = spark.read.text(settings_for_spark.schemas['trades']).first().value

        # This line creates UDF for generating UUIDs
        make_uuid = udf(lambda: str(uuid.uuid4()), StringType())

        # This line reads streams from Kafka broker and creates df with columns based on avro schema
        input_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", settings_for_spark.kafka['server_address']) \
            .option("subscribe", settings_for_spark.kafka['topic'][0]['market']) \
            .option("minPartitions", settings_for_spark.kafka['min_partitions'][0]['MainProcessor']) \
            .option("maxOffsetsPerTrigger", settings_for_spark.spark['max_offsets_per_trigger'][0]['MainProcessor']) \
            .option("useDeprecatedOffsetFetching", settings_for_spark.spark['deprecated_offsets'][0]['MainProcessor']) \
            .load()

        # Explode the data from JSON?
        expanded_df = input_df \
            .withColumn("avroData", from_avro(col("value"), trades_schema)) \
            .selectExpr("avroData.*")
        # .selectExpr("avroData", "explode(data) as col", "type")

        # Rename columns to match their names in Cassandra db
        final_df = expanded_df \
            .withColumn("uuid", make_uuid()) \
            .withColumnRenamed("c", "trades_conditions") \
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
            .withWatermark("trade_ts", "15 seconds") \
            .groupby("symbol") \
            .agg(avg("price_x_volume").alias("price_x_volume"))

        # Rename columns in dataframe and add UUIDs before inserting to Cassandra db
        final_summary_df = summary_df \
            .withColumn("uuid", make_uuid()) \
            .withColumn("ingestion_ts", current_timestamp()) \
            .withColumnRenamed("price_x_volume", "avg_price_x_volume")

        # Write second query to Cassandra - this could also lead to bugs
        query2 = final_summary_df \
            .writeStream \
            .trigger(processingTime="5 seconds") \
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
