import dash
import os
import base64
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django_plotly_dash import DjangoDash
from ..models import Data
import dash_bootstrap_components as dbc
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import visdcc
import time


# ------------------------------------------------------------------------------

app = DjangoDash(name='NumTAD', external_stylesheets=[dbc.themes.SPACELAB], add_bootstrap_links=True) 

# ------------------------------------------------------------------------------
image_filename = '/var/www/html/TADMaster/Site/manyTAD/static/image/nlogo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
image_example = '/var/www/html/TADMaster/Site/manyTAD/static/image/Example_BED_File.png'
encoded_example = base64.b64encode(open(image_example, 'rb').read())
color_scales = px.colors.named_colorscales()
color_scales.append('TADMaster')
colors = ["Aqua", "Blue", "Chartreuse", "Gold", "DeepPink", "DarkViolet",
          "Gray", "DarkSeaGreen", "DarkGreen", "Orchid", "Olive", "Tan", "Yellow", 
	  "Khaki", "DarkBlue", "Chocolate", "SandyBrown", "Violet", "PowderBlue"]


app.layout = html.Div([
        dcc.Input(id='target_id', type='hidden', value='filler text'),
	dcc.Location(id='url', refresh=False),

   	html.Div(
        [
            dbc.Row(
                dbc.Col(
                    style = {"marginTop": "100px", "backgroundColor": "#f2f2f2", "paddingTop": "25px", "paddingBottom": "15px", "borderRadius": "10px"},
                    children = html.Div([

    # ------------------------------------------------------------------------------
    # Number of TADs
    # ------------------------------------------------------------------------------
    html.Div([
        dbc.Button(
            html.H4(children="Number of TADs", className="header_text", 
                style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
            id="collapse-button-number tad",
            size='lg',
            color="light",
            block=True,
        ),
        dbc.Collapse(
            [
                html.Div([
                    html.H2(children="Select Normalization", className="header_text", 
                            style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),

                    dbc.FormGroup(
                        [
                            dbc.RadioItems(
                                id="Normalization",
                                inline=True,
                            ),
                        ]
                    ),
                ], style={"text-align": "center", "margin-top": "25px"}),

                html.Div(
                    [
                        dbc.Row(
                            dbc.Col(

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                        dbc.Checklist(
                                            id="Number TADs Options",
                                            inline=True,
                                            style={"textAlign": "center"}
                                        ),
                                        dbc.Label("Plot Width Slider", html_for="slider"),
                                        dcc.Slider(id='num-TAD-slider', min=5, max=100, step=5, value=50,),
                                    ]
                                
                                ),
                                width={"size": 10, "offset": 1},
                            )
                        ),
                    ]
                ),

                html.Hr(),
		dcc.Loading(id = "loading-icon",
		children=[
                html.Div(
                    [
                        dbc.Card(
                            dbc.CardBody(children = html.Div([
                                dcc.Graph(id="Number TADs Plot", style = {}),], 
                                style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
                            className="mb-3",
                        )
                    ]
                )])

            ],

            id="collapse-number tad",
            is_open=True
        )
    ]),
    ]),

     width={"size": 8, "offset": 2},
                )
            ),
        ]
    )
])

# ------------------------------------------------------------------------------
# Collapse Callbacks
# ------------------------------------------------------------------------------
@app.callback(
    Output("collapse-number tad", "is_open"),
    [Input("collapse-button-number tad", "n_clicks"),
        State("collapse-number tad", "is_open")]
)
def toggle_collapse_number_tad(n, is_open):
    if n:
        return not is_open
    return is_open


# ------------------------------------------------------------------------------
# Dynamic Option Callbacks
# -----------------------------------------------------------------------------

@app.callback(
    Output('Normalization', 'options'),
    [Input('target_id', 'value')])
def available_normalizations_options(id):
    data = Data.objects.get(pk=id)
    job_id = str(data.job_id)
    available_normalizations = []
    path = '/var/www/html/TADMaster/Site/storage/data/job_'+ job_id+'/output/'
    for directory in os.listdir(path):
        available_normalizations.append(os.path.join(path, directory))
    available_options=[{'label': i[78:], 'value': i} for i in available_normalizations]
    return available_options

@app.callback(
    Output('Normalization', 'value'),
    [Input('Normalization', 'options')])
def set_available_normalizations_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('Number TADs Options', 'options'),
    [Input('Normalization', 'value')])
def set_num_tads_options(norm):
    return [{'label': i[:-4], 'value': i} for i in sorted(os.listdir(norm))]

@app.callback(
    Output('Number TADs Plot', 'style'),
    [Input('num-TAD-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style

# ------------------------------------------------------------------------------
# Plot Generators
# -----------------------------------------------------------------------------

@app.callback(
    Output("Number TADs Plot", "figure"),
    [Input('Normalization', 'value'),
    Input('Number TADs Options', 'value')])
def set_display_num_TADs_map(norm_path, number_tads_options):
    print("Construct TAD Size Comparison")
    color_itt = 0
    color_dict = {}
    for file in os.listdir(norm_path):
        color_dict[file[:-4]] = colors[color_itt]
        color_itt += 1
        number_tads = []
    if number_tads_options:
        for filename in os.listdir(norm_path):
            if filename in number_tads_options:
                with open(os.path.join(norm_path, filename), 'r') as file:
                    bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                    number_tads.append([filename[:-4], len(bed)])
        df = pd.DataFrame(data=number_tads, columns=["Callers", "Number of TADs"])
        size_plot = px.bar(df, x="Callers", y="Number of TADs", color="Callers", color_discrete_map=color_dict, template='simple_white')
    else:
        size_plot = px.bar()
    return size_plot
