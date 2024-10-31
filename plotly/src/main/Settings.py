import configparser


class Settings:
    def __init__(self, config_file='/app/resources/application.conf'):
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
        self.tickers = {
            "list": [
                {
                    "BTC": self.config.get('tickers.list', 'BTC'),
                    "ETH": self.config.get('tickers.list', 'ETH'),
                    "XRP": self.config.get('tickers.list', 'XRP'),
                    "DOGE": self.config.get('tickers.list', 'DOGE'),

                }
            ]
        }
