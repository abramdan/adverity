import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Outlier Detection'

orange = '#EC6A2D'
purple = '#8E71B2'

app.layout = html.Div(children=[
    html.Div([
        html.H2(children='Outlier Detection'),

        html.Div(children='''
            This demo uses data from a Kaggle competition (https://www.kaggle.com/c/avazu-ctr-prediction)
            to demonstrate how one can use moving averages
            for a simple outlier detection system
        ''')], style={'padding': 20}),

    html.Div([
        # Moving average type
        html.Div([
            html.H4(children='Moving average type'),
            dcc.RadioItems(
                id='ma_type',
                options=[
                    {'label': 'SMA - Simple Moving Average', 'value': 'sma'},
                    {'label': 'EMA - Exponential Moving Average', 'value': 'ema'},
                ],
                value='sma',
            )], className="three columns"),

        # Outlier threshold - relative to the standard deviation
        html.Div([
            html.H4(children='Outlier Threshold'),
            dcc.Input(
                id='threshold',
                type='number',
                min=1,
                max=3,
                step=0.1,
                value=1.5
            )], className="three columns"),

        # Show/hide outer bounds
        html.Div([
            html.H4(children='Outer Bounds'),
            dcc.RadioItems(
                id='show_bounds',
                options=[
                    {'label': 'Show', 'value': 1},
                    {'label': 'Hide', 'value': 0},
                ],
                value=1,
                labelStyle={'display': 'inline-block'}
            )], className="three columns"),

        # Outlier highlighting
        html.Div([
            html.H4(children='Highlight Outliers'),
            dcc.RadioItems(
                id='highlight_outliers',
                options=[
                    {'label': 'True', 'value': 1},
                    {'label': 'False', 'value': 0},
                ],
                value=1,
                labelStyle={'display': 'inline-block'}
            )], className="three columns")
        ], style={'padding': 20}),

    # Moving average window size
    html.Div([      
        html.H4(children='Moving Average Window Size'),

        dcc.Slider(
            id='ma_window',
            min=1,
            max=24,
            step=1.0,
            value=12,
            marks={i: f"{i}" for i in range(1, 25)},
            updatemode='drag'
        )], style={'padding': 20, 'marginTop': 100}),

    # Chart
    html.Div([ 
        dcc.Graph(
            id='click_through_rates'
        )], style={'padding': 20}),
])


@app.callback(
    Output('click_through_rates', 'figure'),
    [Input('ma_type', 'value'),
     Input('ma_window', 'value'),
     Input('threshold', 'value'),
     Input('show_bounds', 'value'),
     Input('highlight_outliers', 'value')],
)
def draw_graph(ma_type, ma_window, threshold, show_bounds, highlight_outliers):
    
    # Read the prepared dataframe
    file_path = os.path.dirname(os.path.abspath(__file__))
    input_path = file_path + '/ctr.csv'
    ctr = pd.read_csv(input_path)

    # Prepare the moving averages and standard deviations
    if ma_type == 'sma':
        ctr['ma_mean'] = ctr['click'].rolling(window=ma_window).mean()
        ctr['ma_std'] = ctr['click'].rolling(window=ma_window).std()
    else:
        ctr['ma_mean'] = ctr['click'].ewm(span=ma_window).mean()
        ctr['ma_std'] = ctr['click'].ewm(span=ma_window).std()

    # Compute the upper and lower bounds
    ctr['upper_bound'] = ctr['ma_mean'] + ctr['ma_std'] * threshold
    ctr['lower_bound'] = ctr['ma_mean'] - ctr['ma_std'] * threshold

    # Base plot with the click-through rates
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ctr['date'],
                             y=ctr['click'],
                             mode='lines+markers',
                             marker=dict(color=purple),
                             name='Click-through rates'))

    # Draw upper and lower boundaries
    if show_bounds:
        fig.add_trace(go.Scatter(x=ctr['date'],
                                 y=ctr['upper_bound'],
                                 mode='lines',
                                 line=dict(color='#DFE0DF'),
                                 name='Upper threshold'))
        fig.add_trace(go.Scatter(x=ctr['date'],
                                 y=ctr['lower_bound'],
                                 mode='lines',
                                 line=dict(color='#DFE0DF'),
                                 name='Lower threshold'))

    # Highlight the outliers
    if highlight_outliers:
        ctr['upper_outlier'] = ctr.apply(lambda x: x['click'] > x['upper_bound'], axis=1)
        df_upper = ctr[ctr['upper_outlier']]

        fig.add_trace(go.Scatter(x=df_upper['date'],
                                 y=df_upper['click'],
                                 mode='markers',
                                 name='Upper Outliers',
                                 marker=dict(
                                     color=orange,
                                     symbol='triangle-up',
                                     size=10
                                 )))

        ctr['lower_outlier'] = ctr.apply(lambda x: x['click'] < x['lower_bound'], axis=1)
        df_lower = ctr[ctr['lower_outlier']]

        fig.add_trace(go.Scatter(x=df_lower['date'],
                                 y=df_lower['click'],
                                 mode='markers',
                                 name='Lower Outliers',
                                 marker=dict(
                                     color=orange,
                                     symbol='triangle-down',
                                     size=10
                                 )))

    fig.update_layout(
        title='Click-Through Rates',
        title_x=0.5,
        legend=dict(
            x=1,
            y=0.5,
            font_size=12
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        hovermode='closest',
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True) #debug=True, dev_tools_props_check=False