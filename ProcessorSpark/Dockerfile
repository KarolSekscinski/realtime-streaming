FROM bde2020/spark-python-template:3.2.0-hadoop3.2

# Copy requirements.txt to the Docker image
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install -r ./requirements.txt

# Download Spark packages
COPY spark/target/dependency /spark/jars

COPY ./src/main /app/

ENV SPARK_APPLICATION_ARGS "--packages org.apache.spark:spark-sql-kafka-0-10_2.12-3.2.0,org.apache.spark:spark-avro_2.12:3.2.0, \
                            spark-cassandra-connector_2.12-3.2.0,java-driver-core-4.0.0"

ENV SPARK_APPLICATION_PYTHON_LOCATION /app/python/MainProcessor.py
#CMD [ "spark-submit", "--jars", "/spark/jars/*", "/app/python/MainProcessor.py" ]
#CMD ["bash", "template.sh"]