import time
import logging
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy
from dash import Dash, html, dcc, Input, Output, State
from cassandra.cluster import Cluster, ConnectionException
import pandas as pd
from datetime import datetime, timedelta
from Settings import Settings
import dash_bootstrap_components as dbc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Settings()
available_symbols = config.tickers['list'][0]


def connect_to_cassandra(settings_dict: dict):
    """Connect to the Cassandra based on settings dictionary"""
    auth_provider = PlainTextAuthProvider(settings_dict['username'], settings_dict['password'])
    cluster, session = None, None
    for i in range(5):
        try:
            logger.info(f"Connecting to Cassandra at {settings_dict['host']}:{settings_dict['port']} using keyspace '{settings_dict['keyspace']}'")
            cluster = Cluster([settings_dict['host']], port=settings_dict['port'], protocol_version=5
                              load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="DataCenter1"))
            session = cluster.connect(settings_dict["keyspace"])
            logger.info("Successfully connected to Cassandra")
            return session
        except ConnectionException as e:
            logger.error(f"Connection attempt {i+1} failed: {e}")
            time.sleep(5)
    logger.error("All connection attempts to Cassandra failed.")
    return None


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create a simple navbar with a dropdown menu - symbol selection
navbar = dbc.NavbarSimple(
    children=[
        html.Div(
            [
                dcc.Dropdown(
                    id="ticker-dropdown",
                    options=available_symbols,
                    placeholder="Select a trade symbol",
                    value='BINANCE:BTCUSDT',
                    style={'min-width': "300px"}
                )
            ], className="d-flex align-items-center justify-content-between"
        )
    ],
    brand="Realtime Streaming",
    brand_href="#",
    sticky="top"
)

# TODO add slider to change time interval
main_content = dbc.Container(
    [
        dcc.Store(id='symbol_name', storage_type='session'),
        dcc.Store(id="plotting_state", data=True),
        dcc.Interval(id="normal_interval", interval=1 * 1000, n_intervals=0),
        dcc.Interval(id="agg_interval", interval=10 * 1000, n_intervals=0),
        dbc.Col(
            [
                html.Button('ON/OFF Plotting', id='stop-button', n_clicks=0, className='btn btn-danger mt-3'),
                html.H3("Live data from Finnhub.io", className="text-center"),
                dcc.Graph(id="live-data"),
                html.Hr(),
                html.H3("Aggregated data price x volume average of live data", className="text-center"),
                dcc.Graph(id="aggregated")
            ], className="border shadow pt-5"
        )
    ]
)


app.layout = html.Div(children=[
    navbar, main_content
])


@app.callback(
    Output("symbol_name", "data"),
    Input("ticker-dropdown", "value")
)
def change_symbol(value):
    """Changes symbol of stock in the app"""
    for symbol in config.tickers['list']:
        print(symbol)
        # if key == value:
        #     return {value: full_name}
    return {value: "BINANCE:BTCUSDT"}

@app.callback(
    Output('plotting_state', 'data'),
    Input('stop-button', 'n_clicks'),
    State('plotting_state', 'data')
)
def toggle_plotting(n_clicks, plotting_state):
    """Toggles the plotting state"""
    if n_clicks % 2 == 1:  # Stop plotting on odd clicks
        return False
    return True

@app.callback(
    Output("live-data", "figure"),
    Input("ticker-dropdown", "data"),
    Input("normal_interval", "n_intervals"),
    State("plotting_state", "data")
)
def update_normal_graph(symbol_data, n, plotting_state):
    """Updates the normal graph in realtime"""
    if not plotting_state:
        return {}
    data = fetch_data_from_cassandra("trades", symbol_data, 1)
    figure_data = generate_graph(symbol_data, data, type_of_graph=False)
    return figure_data


@app.callback(
    Output("aggregated", "figure"),
    Input("ticker-dropdown", "data"),
    Input("agg_interval", "n_intervals"),
    State("plotting_state", "data")
)
def update_aggregated_graph(symbol_data, n, plotting_state):
    """Updates the aggregated graph in 10 seconds batches"""
    if not plotting_state:
        return {}
    data = fetch_data_from_cassandra("run_10_s_avg", symbol_data, 1)
    figure_data = generate_graph(symbol_data, data, type_of_graph=True)
    return figure_data


def generate_graph(symbol_name: str, data: pd.DataFrame, type_of_graph: bool):
    if type_of_graph: # So we are generating aggregated graph
        # columns of data = ['uuid', 'ingestion_ts', 'avg_price_x_volume', 'symbol']
        trace = {
            "x": data["ingestion_ts"],
            "y": data["avg_price_x_volume"],
            "type": "scatter",
            "mode": "lines+markers",
            "name": f"{symbol_name} Aggregated"
        }

    else:
        # columns of data = ['symbol', 'trade_ts', 'ingestion_ts', 'price', 'trade_conditions', 'type', 'uuid', 'volume']
        price_trace = {
            "x": data['trade_ts'],
            "y": data['price'],
            "type": "scatter",
            "mode": "lines+markers",
            "name": f"{symbol_name} Live"
        }
        volume_trace = {
            "x": data['trade_ts'],
            "y": data['volume'],
            "type": "bar",
            "name": f"{symbol_name} Volume",
            "yaxis": "y2"
        }
        layout = {
            "title": f"Live Aggregated Data for {symbol_name}",
            "yaxis": {"title": "Price"},
            "yaxis2": {
                "title": "Volume",
                "overlaying": "y",
                "side": "right"
            }
        }
        return {"data": [price_trace, volume_trace], "layout": layout}
    layout = {"title": f"Live Raw Data for {symbol_name}"}
    return {"data": [trace], "layout": layout}


def query_cassandra_based_on_symbol(session, table, symbol, wait_time: int) -> pd.DataFrame:
    """This function queries the Cassandra for single trade values"""
    one_minute_ago = (datetime.now() - timedelta(minutes=wait_time)).strftime('%Y-%m-%d %H:%M:%S')
    query = f"SELECT * FROM {table} WHERE symbol = '{symbol}' AND trade_ts >= '{one_minute_ago}'"
    rows = session.execute(query)
    if table == "trades":
        columns = ['symbol', 'trade_ts', 'ingestion_ts', 'price', 'trade_conditions', 'type', 'uuid', 'volume']
    else:
        columns = ['uuid', 'ingestion_ts', 'avg_price_x_volume', 'symbol']
    df = pd.DataFrame(rows, columns=columns)
    session.shutdown()
    return df


def fetch_data_from_cassandra(table: str, symbol: str, wait_time: int) -> pd.DataFrame:
    return query_cassandra_based_on_symbol(cassandra_session, table, symbol, wait_time)


if __name__ == '__main__':
    cassandra_session = connect_to_cassandra(config.cassandra)
    if cassandra_session is None:
        logger.error("Failed to establish Cassandra session. Exiting application.")
        exit(1)
    app.run(debug=True, host="0.0.0.0")
