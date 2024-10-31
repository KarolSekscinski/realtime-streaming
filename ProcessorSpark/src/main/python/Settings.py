import configparser


class Settings:
    def __init__(self, config_file='/app/src/main/resources/application.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.cassandra = {
            "host": self.config.get('cassandra', 'host'),
            "port": self.config.get('cassandra', 'port'),
            "keyspace": self.config.get('cassandra', 'keyspace'),
            "username": self.config.get('cassandra', 'username'),
            "password": self.config.get('cassandra', 'password'),
            "tables": [
                {
                    "trades": self.config.get('cassandra.tables', 'trades'),
                    "aggregates": self.config.get('cassandra.tables', 'aggregates')
                }
            ]
        }

        self.kafka = {
            "server_address": self.config.get('kafka', 'server_address'),
            "topic": [
                {
                    "market": self.config.get('kafka.topics', 'market')
                }
            ],
            "min_partitions": [
                {
                    "StreamProcessor": self.config.get('kafka.min_partitions', 'StreamProcessor')
                }
            ]
        }

        self.spark = {
            "master": self.config.get('spark', 'master'),
            "appName": [
                {
                    "StreamProcessor": self.config.get('spark.appName', 'StreamProcessor')
                }
            ],
            "max_offsets_per_trigger": [
                {
                    "StreamProcessor": self.config.get('spark.max_offsets_per_trigger', 'StreamProcessor')
                }
            ],
            "shuffle_partitions": [
                {
                    "StreamProcessor": self.config.get('spark.shuffle_partitions', 'StreamProcessor')
                }
            ],
            "deprecated_offsets": [
                {
                    "StreamProcessor": self.config.get('spark.deprecated_offsets', 'StreamProcessor')
                }
            ]
        }

        self.schemas = {
            "trades": self.config.get('schemas', 'trades')
        }
