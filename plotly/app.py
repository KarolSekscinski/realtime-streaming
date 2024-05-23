from dash import Dash, html, dcc, Input, Output
import plotly.express as px
from cassandra.cluster import Cluster
import pandas as pd
from datetime import datetime, timedelta

# Connection to Cassandra cluster
cluster = Cluster(['localhost:9042'])
session = cluster.connect('market')


# Define Dash app
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Hello world'),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    )
])


# Define an app callback to update graph each second
@app.callback(Output('live-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n_intervals):
    one_minute_ago = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    query = f"SELECT * FROM market WHERE trade_ts >= '{one_minute_ago}'"
    rows = session.execute(query)
    df = pd.DataFrame(list(rows))

    fig = px.line(df, x='trade_ts', y='price', title='Real-Time Data')
    return fig


if __name__ == '__main__':
    app.run_server()
