import websocket
from utils.producer_funtions import *


class Producer:
    def __init__(self):
        self.config = load_config('config.json')
        self.client = load_client(self.config['FINNHUB_API_TOKEN'])
        self.kafka_producer = load_kafka_producer(self.config['KAFKA_SERVER'])
        self.avro_schema = load_avro_schema('schemas/trades.avsc')
        self.validate = self.config['FINNHUB_VALIDATE_TICKERS']

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={self.config['FINNHUB_API_TOKEN']}",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, ws, message):
        message = json.loads(message)
        data = {
            "data": message['data'],
            "type": message['type']
        }
        avro_message = encode_avro_message(data, self.avro_schema)
        self.kafka_producer.send(self.config['KAFKA_TOPIC'], avro_message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        for ticker in self.config['FINNHUB_STOCKS_TICKERS']:
            if self.validate == 1:
                if ticker_validator(self.client, ticker):
                    self.ws.send(f'{{"type":"subscribe","symbol":"{ticker}"}}')
                    print(f"Subscribed to {ticker}, Success!")
                else:
                    print(f"Invalid ticker {ticker}")
            else:
                self.ws.send(f'{{"type":"subscribe","symbol":"{ticker}"}}')
                print(f"Subscribed to {ticker}, but ticker is not valid")


if __name__ == "__main__":
    Producer()
