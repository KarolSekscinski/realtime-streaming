FROM bitnami/spark:3.5

# Switch to root to install dependencies
USER root

# Install Python and pip
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt to the Docker image
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install -r ./requirements.txt

# Set Spark version and Hadoop version
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3.2

# Download Spark packages using curl
RUN mkdir -p /opt/spark/jars && \
    curl -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.2.1.jar \
         https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.2.1/spark-sql-kafka-0-10_2.12-3.2.1.jar && \
    curl -o /opt/spark/jars/spark-avro_2.12-3.2.1.jar \
         https://repo1.maven.org/maven2/org/apache/spark/spark-avro_2.12/3.2.1/spark-avro_2.12-3.2.1.jar && \
    curl -o /opt/spark/jars/spark-cassandra-connector_2.12-3.2.0.jar \
         https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.2.0/spark-cassandra-connector_2.12-3.2.0.jar && \
    curl -o /opt/spark/jars/cassandra-driver-core-3.11.3.jar \
         https://repo1.maven.org/maven2/com/datastax/cassandra/cassandra-driver-core/3.11.3/cassandra-driver-core-3.11.3.jar

# Set appropriate permissions
RUN chown -R 1001:1001 /opt/spark/jars

# Switch back to the non-root user
USER 1001

# Set the environment variable to include the jars
ENV SPARK_CLASSPATH="/opt/spark/jars/*"

# Ensure the entrypoint and CMD are still set correctly
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "spark-shell" ]
