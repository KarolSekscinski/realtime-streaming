

class Settings:
    def __init__(self, config: Config):
        self.cassandra = {
            "host": config.get_string("cassandra.host"),
            "keyspace": config.get_string("cassandra.keyspace"),
            "username": config.get_string("cassandra.username"),
            "password": config.get_string("cassandra.password"),
            "trades": config.get_string("cassandra.tables.trades"),
            "aggregates": config.get_string("cassandra.tables.aggregates")
        }

        self.kafka = {
            "server_address": config.get_string("kafka.server_address"),
            "topic_market": config.get_string("kafka.topics.market"),
            "min_partitions": config.get_string("kafka.min_partitions.StreamProcessor")
        }

        self.spark = {
            "master": config.get_string("spark.master"),
            "appName": config.get_string("spark.appName.StreamProcessor"),
            "max_offsets_per_trigger": config.get_string("spark.max_offsets_per_trigger.StreamProcessor"),
            "shuffle_partitions": config.get_string("spark.shuffle_partitions.StreamProcessor"),
            "deprecated_offsets": config.get_string("spark.deprecated_offsets.StreamProcessor")
        }

        self.schemas = {
            "trades": config.get_string("schemas.trades")
        }
