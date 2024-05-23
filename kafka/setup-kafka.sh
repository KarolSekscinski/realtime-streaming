# This line attempts to list all topics on kafka broker
# if the broker is not reachable, this command will fail and subsequent commands will not execute
kafka-topics --bootstrap-server kafka-broker:29092 --list

# Those lines creates kafka if it does not exist
echo -e 'Creating Kafka topics'
kafka-topics --bootstrap-server kafka-broker:29092 --create --if-not-exists --topic market --replication-factor 1 --partitions 1

# Those lines lists all topics on the kafka broker to confirm the creation of the market topic
echo -e 'Successfully created topics:'
kafka-topics --bootstrap-server kafka-broker:29092 --list