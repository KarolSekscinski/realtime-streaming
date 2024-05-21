import json
import avro.schema
import avro.io
import finnhub
from kafka import KafkaProducer
import io


def load_config(config_file):
    # This function loads config file for Producer class. The config should include
    # e.g. Finnhub API Key
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config


def load_avro_schema(path_to_avro_schema):
    # This function parses avro schema based on response from
    # sample response https://finnhub.io/docs/api/websocket-trades
    return avro.schema.parse(open(path_to_avro_schema).read())


def load_client(api_key):
    # This function sets up Finnhub client
    return finnhub.Client(api_key=api_key)


def load_kafka_producer(kafka_server):
    # This function returns Kafka Producer to later produce data from
    # Finnhub.io into Kafka
    return KafkaProducer(bootstrap_servers=kafka_server)


def encode_avro_message(data, schema):
    # This function produces an Avro-encoded binary message based on schema
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    datum_writer = avro.io.DatumWriter(schema)

    datum_writer.write(data, encoder)
    return bytes_writer.getvalue()


def ticker_validator(finnhub_client, ticker):
    # This function uses finnhub symbol lookup to search for best-matching
    # symbols based on ticker
    def symbol_lookup():
        return finnhub_client.symbol_lookup(ticker)
    for symbol in symbol_lookup()['result']:
        if symbol['symbol'] == ticker:
            return True
    return False
