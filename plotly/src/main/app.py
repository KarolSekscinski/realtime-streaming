import time
import logging
from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
from Settings import Settings
from cassandra_gateway import CassandraGateway
import dash_bootstrap_components as dbc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Settings()
available_symbols = config.tickers['list'][0]


def fetch_data_from_cassandra(table_name, symbol_name, wait_time):
    """Connect to the Cassandra and fetch data"""
    test_result, session = None, None
    gateway = CassandraGateway()
    for i in range(5):
        try:
            session = gateway.db_session()
            test_result = gateway.test_connection()
        except Exception as e:
            logger.error(f"{i+1}: Cannot connect to cassandra {e}")
            time.sleep(5)
    results = pd.DataFrame()
    if test_result is None and session is not None:
        logger.error("All connection attempts to Cassandra failed.")
    else:
        results = gateway.query(session, table_name, symbol_name, wait_time)
    return results


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
                dcc.Slider(id="live-data-slider", min=1, max=10, step=1, value=1,
                           marks={i: f'{i}s' for i in range(1, 11)}, className="mt-3 mb-3"),
                dcc.Graph(id="live-data"),
                html.Hr(),
                html.H3("Aggregated data price x volume average of live data", className="text-center"),
                dcc.Slider(id="aggregated-slider", min=10, max=60, step=10, value=10,
                           marks={i: f'{i}s' for i in range(10, 61, 10)}, className="mt-3 mb-3"),
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
    Output("normal_interval", "interval"),
    Input("live-data-slider", "value")
)
def update_normal_interval(value):
    """Updates the normal interval based on slider value"""
    return value * 1000


@app.callback(
    Output("agg_interval", "interval"),
    Input("aggregated-slider", "value")
)
def update_agg_interval(value):
    """Updates the aggregated interval based on slider value"""
    return value * 1000


@app.callback(
    Output("live-data", "figure"),
    Input("ticker-dropdown", "value"),
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
    Input("ticker-dropdown", "value"),
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
    if type_of_graph:  # So we are generating aggregated graph
        # columns of data = ['uuid', 'ingestion_ts', 'avg_price_x_volume', 'symbol']
        trace = {
            "x": data["ingestion_ts"],
            "y": data["avg_price_x_volume"],
            "type": "scatter",
            "mode": "lines+markers",
            "name": f"{symbol_name} Aggregated"
        }

    else:
        # columns of data =
        # ['symbol', 'trade_ts', 'ingestion_ts', 'price', 'trade_conditions', 'type', 'uuid', 'volume']
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


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
