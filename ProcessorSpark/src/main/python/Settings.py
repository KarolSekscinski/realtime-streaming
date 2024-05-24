class Settings:
    def __init__(self):
        self.cassandra = {
            "host": "cassandra",
            "keyspace": "market",
            "username": "cassandra",
            "password": "cassandra",
            "tables": [
                {
                    "trades": "trades",
                    "aggregates": "run_10_s_avg"
                }
            ]
        }

        self.kafka = {
            "server_address": "kafka-broker:29092",
            "topic": [
                {
                    "market": "market"
                }
            ],
            "min_partitions": [
                {
                    "MainProcessor": "1"
                }
            ]
        }

        self.spark = {
            "master": "spark://spark-master:7077",
            "appName": [
                {
                    "MainProcessor": "Main ProcessorSpark"
                }
            ],
            "max_offsets_per_trigger": [
                {
                    "MainProcessor": "1000"
                }
            ],
            "shuffle_partitions": [
                {
                    "MainProcessor": "2"
                }
            ],
            "deprecated_offsets": [
                {
                    "MainProcessor": "false"
                }
            ]
        }
# This could be incorrect
        self.schemas = {
            "trades": "./resources/schemas/trades.avsc"
        }
