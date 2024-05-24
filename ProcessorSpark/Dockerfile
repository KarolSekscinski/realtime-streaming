FROM bde2020/spark-python-template:3.2.0-hadoop3.2

# Copy and install Python dependencies
COPY ./src/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./spark/target/dependency /spark/jars

# Copy the MainProcessor and Settings classes to the container
COPY ./src/main/ /opt/spark/app/

ENV SPARK_APPLICATION_MAIN_CLASS MainProcessor
ENV SPARK_APPLICATION_ARGS "--packages org.apache.spark:spark-sql-kafka-0-10_2.12-3.2.0,org.apache.spark:spark-avro_2.12:3.2.0, \
                            spark-cassandra-connector_2.12-3.2.0,java-driver-core-4.0.0"

CMD [ "spark-submit", "--verbose", "--jars", "/opt/spark/jars/*", "/opt/spark/app/src/main/python/MainProcessor.py" ]