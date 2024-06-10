from datetime import datetime, timedelta

import pandas as pd
from cassandra.cluster import Cluster
from Settings import Settings
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy


class CassandraGateway:
    def __init__(self):
        self.settings = Settings()
        self.host = self.settings.cassandra['host']
        self.port = self.settings.cassandra['port']
        self.username = self.settings.cassandra['username']
        self.password = self.settings.cassandra['password']
        self.keyspace = self.settings.cassandra['keyspace']

    def db_session(self):
        plain_auth = PlainTextAuthProvider(username=self.username, password=self.password)
        cluster = Cluster([self.host], port=self.port, protocol_version=5, auth_provider=plain_auth,
                          load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="DataCenter1"))

        session = cluster.connect()
        session.set_keyspace(self.keyspace)
        return session

    @staticmethod
    def close_session(session):
        session.close()

    def test_connection(self):
        session = self.db_session()
        test_result = session.execute("SELECT now() FROM system.local")
        self.close_session(session)
        return test_result

    def query(self, session, table_name: str, symbol_name: str, wait_time: int) -> pd.DataFrame:
        one_minute_ago = (datetime.now() - timedelta(minutes=wait_time)).strftime('%Y-%m-%d %H:%M:%S')
        query = f"SELECT * FROM market.{table_name} WHERE symbol = '{symbol_name}' AND trade_ts >= '{one_minute_ago}'"
        query_result = session.execute(query)
        if table_name == "trades":
            columns = ['symbol', 'trade_ts', 'ingestion_ts', 'price', 'trade_conditions', 'type', 'uuid', 'volume']
        else:
            columns = ['uuid', 'ingestion_ts', 'avg_price_x_volume', 'symbol']
        df = pd.DataFrame(query_result, columns=columns)
        self.close_session(session)
        return df
