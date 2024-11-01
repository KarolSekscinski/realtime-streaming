# Initial Assumptions of the Project

The system will process financial data in the form of real-time streaming data. It will consist of several modules: Apache Kafka, Apache Spark, a NoSQL database, and a data visualization tool (Power BI or Grafana). The data source will be the Finnhub.io WebSocket. 

## Overall Scheme of the Data Processing Pipeline

![dyplomowy drawio](https://github.com/user-attachments/assets/f9168ab6-f0ee-4084-89d9-304a3a234ed3)

All components, except for Finnhub.io, have been containerized to simplify project development and enhance its reliability. Below is a description of each container from left to right in the diagram:

1. **Finnhub.io**  
   Data source, a free API providing financial data.

2. **Data-Producer Container**  
   Responsible for connecting via WebSocket to the Finnhub.io API, serializing the data, and sending it to the Apache Kafka broker.

3. **Zookeeper Container**  
   ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.

4. **Kafdrop Container**  
   Used for monitoring the operation of the Apache Kafka broker.

5. **Apache Kafka Container**  
   A message broker receiving data from the Data-Producer and storing it until it is retrieved by Apache Spark.

6. **Apache Spark Cluster**  
   Consists of four containers:
   - **Main-Processor**: The main container executing jobs to receive data from Apache Kafka, process it into Spark DataFrame, perform necessary data aggregations using PySpark, and save the results to the Apache Cassandra container.
   - **Spark-Master**: The container managing Spark-Worker-1 and Spark-Worker-2, which perform the actual distributed data processing.

7. **CassandraDB Container**  
   NoSQL database Apache Cassandra consisting of one cluster (one instance) where processed data from the Apache Spark cluster is stored.

8. **Grafana Container**  
   Responsible for fetching data from CassandraDB and displaying it on the charts shown below.
