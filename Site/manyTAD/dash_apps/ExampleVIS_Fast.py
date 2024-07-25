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
from collections import OrderedDict
from sklearn.decomposition import PCA
import visdcc
import time

# ------------------------------------------------------------------------------

app = DjangoDash(name='ExampleVIS_Fast', external_stylesheets=[dbc.themes.SPACELAB], add_bootstrap_links=True)

# ------------------------------------------------------------------------------
image_filename = '/var/www/html/TADMaster/Site/manyTAD/static/image/nlogo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
image_example = '/var/www/html/TADMaster/Site/manyTAD/static/image/Example_BED_File.png'
encoded_example = base64.b64encode(open(image_example, 'rb').read())
color_scales = px.colors.named_colorscales()
color_scales.append('TADMaster')
colors = ["Aqua", "Blue", "Chartreuse", "Gold", "DeepPink", "DarkViolet",
          "Gray", "Brown", "DarkGreen", "Orchid", "Olive", "Tan", "Yellow",
          "Khaki", "DarkBlue", "Crimson", "SandyBrown", "Violet", "PowderBlue"]

app.layout = html.Div([
    dcc.Input(id='target_id', type='hidden', value='filler text'),
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='resolution'),
    dcc.Store(id='TAD dict'),
    dcc.Store(id='TAD dict binned'),
    dcc.Store(id='Color dict'),
    dcc.Store(id='MoC data'),
    html.Div(
        [
            dbc.Row(
                dbc.Col(
                    style={"marginTop": "100px", "backgroundColor": "#f2f2f2", "paddingTop": "25px",
                           "paddingBottom": "15px", "borderRadius": "10px"},
                    children=html.Div([

                        # ------------------------------------------------------------------------------
                        # Normalizations
                        # ------------------------------------------------------------------------------
                        html.Div(
                            [
                                html.A([
                                    html.Div(
                                        [
                                            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                                     style={'height': '75%', 'width': '75%'}),

                                        ], style={"width": "150px","height": "150px",   "text-align": "center", 'display': 'inline-block'}),
                                ], href="/TADMaster/", target="_top"),
                                html.Div(
                                    [
                                        html.H2("TADMaster"),
                                    ], style={"width": "150px","height": "150px",   "text-align": "center", 'display': 'inline-block'}),

                            ], style={"text-align": "center", "margin-bottom": "25px"}),

                        html.Div(
                            [
                                dbc.Row([
                                    dbc.Col(
                                        html.Div([
                                            dbc.Button("Upload TAD Bed",
                                                       id="collapse-button-upload",
                                                       ),
                                            dbc.Collapse(
                                                dbc.Card([dbc.CardBody(
                                                    "Uploads are disabled on the example visualizations. If you wish to upload a bed, then please download this example and reupload the job. This will create a duplicate that can be altered."),
                                                          ]),
                                                id="collapse-upload",

                                            ),

                                        ]),

                                    ),
                                    dbc.Col(
                                        html.Div([
                                            dbc.Button("Disclaimer", id='open_disclaimer'),
                                            dbc.Modal(
                                                [
                                                    dbc.ModalHeader("General Disclaimer"),
                                                    dbc.ModalBody(
                                                        "TADMaster is a general purpose HiC data processing tool for identifying and visualizing topographic associated domains. As a result, we use the recommended parameters for the methods that identify these regions in order to achive good results for a variety of input datasets. Occasionally datasets, normalization methods, and/or TAD callers can affect the results. The latter can result in methods not displaying on the visualization screen. We encourage users to run these methods independently in these circumstances. If you have any additional questions or feedback, please reach out to us via email or our github. Thank you for using TADMaster!"
                                                    ),
                                                    dbc.ModalFooter(
                                                        dbc.Button("Close", id="close_disclaimer", className="ml-auto")
                                                    ),
                                                ],
                                                id="modal_disclaimer",
                                            ),
                                        ], style={"align-items": "center", "justify-content": "center",
                                                  "display": "flex"}),
                                    ),
                                    dbc.Col(
                                        dbc.Button("Download Data", id='download button', href="", external_link=True,
                                                   style={"float": "right"})
                                    ),
                                ]),
                            ]),
                        html.H2(children="Title", className="header_text",
                                style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),
                        html.Div(id='page_title', style={"text-align": "center", "margin-top": "5px"}),

                        html.H2(children="Description", className="header_text",
                                style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),
                        html.Div(id='page_description', style={"text-align": "center", "margin-top": "5px"}),

			html.Div([
                        html.H2(children="Resolution", className="header_text",
                                style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),
                        html.Div(id='page_resolution', style={"text-align": "center", "margin-top": "5px"}),
			],style={'width': '49%', 'display': 'inline-block'}),
			html.Div([
                        html.H2(children="Chromosome", className="header_text",
                                style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),
                        html.Div(id='page_chromosome', style={"text-align": "center", "margin-top": "5px"}),
			],style={'width': '49%', 'display': 'inline-block'}),

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

                        ], style={"text-align": "center", "margin-top": "5px"}),
                        # ------------------------------------------------------------------------------
                        # Heat Map
                        # ------------------------------------------------------------------------------
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
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                                            dbc.Checklist(
                                                                id="Number TADs Options",
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),
                                                            dbc.Label("Plot Width Slider", html_for="slider"),
                                                            dcc.Slider(id='num-TAD-slider', min=5, max=100, step=5,
                                                                       value=50, ),
                                                        ]

                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="Number TADs Plot", style={}), ],
                                                                    style={'display': 'flex', 'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-number tad",
                                is_open=True
                            )
                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # Size of TADs
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="Size of TADs", className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-size tad",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                                            dbc.Checklist(
                                                                id="Whisker Options",
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),
                                                            dbc.Label("Plot Width Slider", html_for="slider"),
                                                            dcc.Slider(id='size-TAD-slider', min=5, max=100, step=5,
                                                                       value=50, ),

                                                        ]
                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="Whisker Plot", style={}), ],
                                                                    style={'display': 'flex', 'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-size tad",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # Shared Boundaries
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="Number of Shared Boundaries", className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-shared bound",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                                            dbc.RadioItems(
                                                                id="Boundary Options",
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),
                                                            dbc.Label("Plot Width Slider", html_for="slider"),
                                                            dcc.Slider(id='shared-boundaries-slider', min=5, max=100,
                                                                       step=5, value=100, ),

                                                        ]
                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="Boundary Plot", style={}), ],
                                                                    style={'display': 'flex', 'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-shared bound",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # Stacked Boundaries
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="Stacked Shared Boundaries", className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-stacked bound",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Tolerance:", style={"marginTop": "10px"}),
                                                            dbc.RadioItems(
                                                                id="Stacked Boundary Options",
                                                                options=[{'label': 'Zero', 'value': '0'},
                                                                         {'label': 'One', 'value': '1'},
                                                                         {'label': 'Two', 'value': '2'},
                                                                         {'label': 'Three', 'value': '3'}],
                                                                value='1',
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),
                                                            dbc.Label("Plot Width Slider", html_for="slider"),
                                                            dcc.Slider(id='stacked-boundary-slider', min=5, max=100,
                                                                       step=5, value=50, ),

                                                        ],
                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="Stacked Boundary Plot", style={}), ],
                                                                    style={'display': 'flex', 'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-stacked bound",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # Stacked Domains
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="Stacked Shared Domains", className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-stacked domain",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Tolerance:", style={"marginTop": "10px"}),
                                                            dbc.RadioItems(
                                                                id="Stacked Domain Options",
                                                                options=[{'label': 'Zero', 'value': '0'},
                                                                         {'label': 'One', 'value': '1'},
                                                                         {'label': 'Two', 'value': '2'},
                                                                         {'label': 'Three', 'value': '3'}],
                                                                value='1',
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),
                                                            dbc.Label("Plot Width Slider", html_for="slider"),
                                                            dcc.Slider(id='stacked-domain-slider', min=5, max=100,
                                                                       step=5, value=50, ),

                                                        ]
                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="Stacked Domain Plot", style={}), ],
                                                                    style={'width': '100%', 'display': 'flex',
                                                                           'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-stacked domain",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # MoC Compare
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="Comparison of Domain Overlap (Measure of Concordance)",
                                        className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-MoC compare",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Method:", style={"marginTop": "10px"}),
                                                            dbc.RadioItems(
                                                                id="MoC Options",
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),
                                                            dbc.Label("Plot Width Slider", html_for="slider"),
                                                            dcc.Slider(id='moc-compare-slider', min=5, max=100, step=5,
                                                                       value=50, ),

                                                        ]
                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="MoC Comparison Plot", style={}), ],
                                                                    style={'width': '100%', 'display': 'flex',
                                                                           'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-MoC compare",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # MoC Average
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="Comparison of Average Domain Overlap (Measure of Concordance)",
                                        className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-MoC average",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Plot Width Slider", style={"marginTop": "10px"}),
                                                            dcc.Slider(id='moc-average-slider', min=5, max=100, step=5,
                                                                       value=50, ),
                                                        ]
                                                    ),
                                                    width={"size": 10, "offset": 1},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="MoC Plot", style={}), ],
                                                                    style={'width': '100%', 'display': 'flex',
                                                                           'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",

                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-MoC average",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # TNSE
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="TSNE Comparison", className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-TSNE",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Perplexity:",
                                                                      style={"marginTop": "10px"}),
                                                            dcc.Slider(id='TSNE Slider',
                                                                       min=1,
                                                                       max=15,
                                                                       step=1,
                                                                       marks={1: '1',
                                                                              3: '3',
                                                                              5: '5',
                                                                              7: '7',
                                                                              9: '9',
                                                                              11: '11',
                                                                              13: '13',
                                                                              15: '15'},
                                                                       value=3,
                                                                       className="text-center"
                                                                       ),
                                                            dbc.Label("Marker Size Slider", html_for="slider"),
                                                            dcc.Slider(id='tnse-marker-slider', min=1, max=20, step=1,
                                                                       value=10, ),
                                                        ], style={'width': '100%', 'display': 'inline-block'}
                                                    ),
                                                    width={"size": 6, "offset": 3},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="TSNE Plot", style={'width': '100%',
                                                                                                     'height': '100%'}), ],
                                                                    style={'width': '100%', 'height': '100%',
                                                                           'display': 'flex', 'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                                style={'height': '63vw'})
                                                        ], style={'height': '63vw'})]),

                                ],

                                id="collapse-TSNE",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),
                        # ------------------------------------------------------------------------------
                        # PCA
                        # -----------------------------------------------------------------------------
                        html.Div([
                            dbc.Button(
                                html.H4(children="PCA Comparison", className="header_text",
                                        style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                                id="collapse-button-PCA",
                                size='lg',
                                color="light",
                                block=True,
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    children=dbc.FormGroup(
                                                        [
                                                            dbc.Label("Marker Size Slider",
                                                                      style={"marginTop": "10px"}),
                                                            dcc.Slider(id='pca-marker-slider', min=1, max=20, step=1,
                                                                       value=10, ),
                                                        ], style={'width': '100%', 'display': 'inline-block'}
                                                    ),
                                                    width={"size": 6, "offset": 3},
                                                )
                                            ),
                                        ]
                                    ),

                                    html.Hr(),
                                    dcc.Loading(id="loading-icon",
                                                children=[
                                                    html.Div(
                                                        [
                                                            dbc.Card(
                                                                dbc.CardBody(children=html.Div([
                                                                    dcc.Graph(id="PCA Plot", style={'width': '100%',
                                                                                                    'height': '100%'}), ],
                                                                    style={'width': '100%', 'display': 'flex',
                                                                           'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                            )
                                                        ]
                                                    )])

                                ],

                                id="collapse-PCA",
                                is_open=True
                            )

                        ], style={'marginTop': 20}),

                    ]),

                    width={"size": 8, "offset": 2},
                )
            ),
        ]
    )
])


# ------------------------------------------------------------------------------
# Collapse Callbacks
# -----------------------------------------------------------------------------

@app.callback(
    Output("modal_example", "is_open"),
    [Input("open_example", "n_clicks"), Input("close_example", "n_clicks")],
    [State("modal_example", "is_open")],
)
def toggle_modal_example(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal_disclaimer", "is_open"),
    [Input("open_disclaimer", "n_clicks"), Input("close_disclaimer", "n_clicks")],
    [State("modal_disclaimer", "is_open")],
)
def toggle_modal_disclaimer(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-upload", "is_open"),
    [Input("collapse-button-upload", "n_clicks"),
     State("collapse-upload", "is_open")]
)
def toggle_collapse_upload(n, is_open):
    if n:
        return not is_open
    return is_open


# ----------------------------------------------------------------------------

@app.callback(
    Output("collapse-heatmap", "is_open"),
    [Input("collapse-button-heatmap", "n_clicks"),
     State("collapse-heatmap", "is_open")]
)
def toggle_collapse_heatmap(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-number tad", "is_open"),
    [Input("collapse-button-number tad", "n_clicks"),
     State("collapse-number tad", "is_open")]
)
def toggle_collapse_number_tad(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-size tad", "is_open"),
    [Input("collapse-button-size tad", "n_clicks"),
     State("collapse-size tad", "is_open")]
)
def toggle_collapse_size_tad(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-shared bound", "is_open"),
    [Input("collapse-button-shared bound", "n_clicks"),
     State("collapse-shared bound", "is_open")]
)
def toggle_collapse_shared_bound(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-stacked bound", "is_open"),
    [Input("collapse-button-stacked bound", "n_clicks"),
     State("collapse-stacked bound", "is_open")]
)
def toggle_collapse_stacked_bound(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-stacked domain", "is_open"),
    [Input("collapse-button-stacked domain", "n_clicks"),
     State("collapse-stacked domain", "is_open")]
)
def toggle_collapse_stacked_domain(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-MoC compare", "is_open"),
    [Input("collapse-button-MoC compare", "n_clicks"),
     State("collapse-MoC compare", "is_open")]
)
def toggle_collapse_moc_compare(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-MoC average", "is_open"),
    [Input("collapse-button-MoC average", "n_clicks"),
     State("collapse-MoC average", "is_open")]
)
def toggle_collapse_moc_average(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-TSNE", "is_open"),
    [Input("collapse-button-TSNE", "n_clicks"),
     State("collapse-TSNE", "is_open")]
)
def toggle_collapse_tsne(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-PCA", "is_open"),
    [Input("collapse-button-PCA", "n_clicks"),
     State("collapse-PCA", "is_open")]
)
def toggle_collapse_pca(n, is_open):
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
    path = '/var/www/html/TADMaster/Site/storage/data/job_' + job_id + '/output/'
    for directory in os.listdir(path):
        available_normalizations.append(os.path.join(path, directory))
    available_options = [{'label': i[78:], 'value': i} for i in available_normalizations]
    return available_options


@app.callback(
    Output('Normalization', 'value'),
    [Input('Normalization', 'options')])
def set_available_normalizations_value(available_options):
    return available_options[0]['value']


@app.callback(
    [Output('page_title', 'children'),
     Output('page_description', 'children'),
     Output('page_resolution', 'children'),
     Output('page_chromosome', 'children'),
     Output('resolution', 'data')],
    [Input('target_id', 'value')])
def set_title(id):
    print("Getting Title")
    data = Data.objects.get(pk=id)
    return data.title, data.description, str(data.resolution), str(data.chromosome), data.resolution


@app.callback(
    [Output('Number TADs Options', 'options'),
     Output('Whisker Options', 'options'),
     Output('Boundary Options', 'options'),
     Output('MoC Options', 'options')],
    [Input('Normalization', 'value')])
def set_options(norm):
    options = [{'label': i[:-4], 'value': i} for i in os.listdir(norm)]
    return [options, options, options, options]


@app.callback(
    [Output('Number TADs Options', 'value'),
     Output('Whisker Options', 'value'),
     Output('Boundary Options', 'value'),
     Output('MoC Options', 'value')],
    [Input('Number TADs Options', 'options')])
def set_start_value(available_options):
    return [[available_options[0]['value']], [available_options[0]['value']], available_options[0]['value']
            , available_options[0]['value']]


@app.callback(
    Output('Number TADs Plot', 'style'),
    [Input('num-TAD-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


@app.callback(
    Output('Whisker Plot', 'style'),
    [Input('size-TAD-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


@app.callback(
    Output('Boundary Plot', 'style'),
    [Input('shared-boundaries-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


@app.callback(
    Output('Stacked Boundary Plot', 'style'),
    [Input('stacked-boundary-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


@app.callback(
    Output('Stacked Domain Plot', 'style'),
    [Input('stacked-domain-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


@app.callback(
    Output('MoC Comparison Plot', 'style'),
    [Input('moc-compare-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


@app.callback(
    Output('MoC Plot', 'style'),
    [Input('moc-average-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size) + '%'
    style['height'] = str(size) + '%'
    return style


# ------------------------------------------------------------------------------
# Plot Generators
# -----------------------------------------------------------------------------


@app.callback(
    [Output("TAD dict", "data"),
     Output("TAD dict binned", "data"),
     Output("Color dict", "data")],
    [Input('Normalization', 'value'),
     Input("resolution", "data")])
def data_extract(norm_path, resolution):
    print("Extracting Data")
    color_itt = 0
    color_dict = OrderedDict()
    tad_dict = OrderedDict()
    tad_dict_binned = OrderedDict()
    for filename in os.listdir(norm_path):
        with open(os.path.join(norm_path, filename), 'r') as file:
            tad_data = [[float(digit) for digit in line.split(sep=',')] for line in file]
        color_dict[filename[:-4]] = colors[color_itt]
        tad_dict[filename[:-4]] = tad_data
        tad_data = np.asarray(tad_data)
        tad_dict_binned[filename[:-4]] = tad_data / resolution
        color_itt += 1
    return [tad_dict, tad_dict_binned, color_dict]

@app.callback(
    Output("MoC data", "data"),
    [Input('TAD dict binned', 'data')])
def extract_MoC(tad_dict_binned):
    itt = 0
    num_methods = len(tad_dict_binned.keys())
    names = tad_dict_binned.keys()
    if num_methods > 1:
        MoC = [[None for i in range(num_methods)] for j in range(num_methods)]
        for check_file in names:
            check_bed = tad_dict_binned[check_file]
            file_count = 0
            for filename in names:
                if filename == check_file:
                    MoC[itt][file_count] = 1
                else:
                    avg_MoC = []
                    bed = tad_dict_binned[filename]
                    for check_row in check_bed:
                        for row in bed:
                            if check_row[0] < row[1] and check_row[1] > row[0]:
                                if check_row[1] <= row[1] and check_row[0] >= row[0]:
                                    try:
                                        avg_MoC.append(math.pow(check_row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                    except ZeroDivisionError:
                                        avg_MoC.append(0)
                                elif check_row[1] <= row[1] and check_row[0] <= row[0]:
                                    try:
                                        avg_MoC.append(math.pow(check_row[1] - row[0], 2) / (
                                            (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                    except ZeroDivisionError:
                                        avg_MoC.append(0)
                                elif check_row[1] >= row[1] and check_row[0] >= row[0]:
                                    try:
                                        avg_MoC.append(math.pow(row[1] - check_row[0], 2) / (
                                            (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                    except ZeroDivisionError:
                                        avg_MoC.append(0)
                                else:
                                    try:
                                        avg_MoC.append(math.pow(row[1] - row[0], 2) / (
                                            (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                    except ZeroDivisionError:
                                        avg_MoC.append(0)
                            else:
                                avg_MoC.append(0)
                    if len(avg_MoC) == 1 and avg_MoC[0] > 0:
                        MoC[itt][file_count] = avg_MoC[0]
                    elif sum(avg_MoC) <= 0:
                        MoC[itt][file_count] = .000001
                    else:
                        MoC[itt][file_count] = sum(avg_MoC) / (math.sqrt(len(avg_MoC)) - 1)
                file_count += 1
            itt += 1
        MoC = np.asarray(MoC)
        print(MoC)
    return MoC



@app.callback(
    Output("Number TADs Plot", "figure"),
    [Input('TAD dict', 'data'),
     Input('Color dict', 'data'),
     Input('Number TADs Options', 'value')])
def set_display_num_TADs_map(tad_dict, color_dict, number_tads_options):
    print("Construct TAD Size Comparison")
    if number_tads_options:
        number_tads = []
        for filename in number_tads_options:
            bed = tad_dict[filename[:-4]]
            number_tads.append([filename[:-4], len(bed)])
        df = pd.DataFrame(data=number_tads, columns=["Callers", "Number of TADs"])
        size_plot = px.bar(df, x="Callers", y="Number of TADs", color="Callers", color_discrete_map=color_dict,
                           template='simple_white')
    else:
        size_plot = px.bar()
    return size_plot


@app.callback(
    Output("Whisker Plot", "figure"),
    [Input('TAD dict binned', 'data'),
     Input('Color dict', 'data'),
     Input('Whisker Options', 'value')])
def set_display_whisker_map(tad_dict_binned, color_dict, whisker_options):
    print("Construct Whisker Plot")
    size_tads = []
    if whisker_options:
        for filename in whisker_options:
            bed = tad_dict_binned[filename[:-4]]
            for row in bed:
                size_tads.append([filename[:-4], row[1] - row[0]])
        box_df = pd.DataFrame(data=size_tads, columns=["Callers", "Size of TADs"])
        whisker_plot = px.box(box_df, x="Callers", y="Size of TADs", color="Callers", color_discrete_map=color_dict,
                              template='simple_white')
    else:
        whisker_plot = px.box()
    return whisker_plot


@app.callback(
    Output("Boundary Plot", "figure"),
    [Input('TAD dict binned', 'data'),
     Input('Color dict', 'data'),
     Input('Boundary Options', 'value')])
def set_display_boundary_map(tad_dict_binned, color_dict, boundary_option):
    boundaries = []
    if boundary_option:
        selected_option = boundary_option[:-4]
        check_bed = tad_dict_binned[selected_option]
        for tolerance in range(10):
            for key in tad_dict_binned.keys():
                if key not in selected_option:
                    check_boundaries = [True for y in range(len(check_bed) * 2)]
                    shared_boundaries = 0
                    bed = tad_dict_binned[key]
                    for row in bed:
                        itt = 0
                        for check in check_bed:
                            if check_boundaries[itt] and math.isclose(row[0], check[0], abs_tol=tolerance):
                                shared_boundaries += 1
                                check_boundaries[itt] = False
                            if check_boundaries[itt + 1] and math.isclose(row[1], check[1], abs_tol=tolerance):
                                shared_boundaries += 1
                                check_boundaries[itt + 1] = False
                            itt += 2
                    boundaries.append([key, tolerance, shared_boundaries])
        shared_boundaries_df = pd.DataFrame(data=boundaries, columns=["Callers", "Tolerance", "Shared Boundaries"])
        boundary_plot = px.bar(shared_boundaries_df, x="Tolerance", y="Shared Boundaries", color="Callers",
                               barmode='group',
                               color_discrete_map=color_dict, template='simple_white')
    else:
        boundary_plot = px.bar()
    return boundary_plot


@app.callback(
    Output("Stacked Boundary Plot", "figure"),
    [Input('TAD dict binned', 'data'),
     Input('Stacked Boundary Options', 'value')])
def set_display_stacked_boundary_map(tad_dict_binned, stacked_boundary_option):
    tolerance = int(stacked_boundary_option)
    itt = 0
    num_methods = len(tad_dict_binned.keys())
    names = list(tad_dict_binned.keys())
    if num_methods > 1:
        stack = [[0 for x in range(num_methods)] for y in range(num_methods)]
        for check_key in names:
            check_bed = tad_dict_binned[check_key]
            check_boundaries = [[0 for x in range(3)] for y in range(len(check_bed) * 2)]
            for i in range(0, 2 * len(check_bed), 2):
                test = math.floor(i / 2)
                check_boundaries[i][0] = check_bed[test][0]
                check_boundaries[i][1] = 0
                check_boundaries[i][2] = True
                check_boundaries[i + 1][0] = check_bed[test][1]
                check_boundaries[i + 1][1] = 0
                check_boundaries[i+1][2] = True
            for key in names:
                if key != check_key:
                    bed = tad_dict_binned[key]
                    for row in bed:
                        for i in range(0, len(check_boundaries), 2):
                            if check_boundaries[i][2] and \
                                    math.isclose(row[0], check_boundaries[i][0], abs_tol=tolerance):
                                check_boundaries[i][1] += 1
                                check_boundaries[i][2] = False
                            if check_boundaries[i+1][2] and \
                                    math.isclose(row[1], check_boundaries[i+1][0], abs_tol=tolerance):
                                check_boundaries[i+1][1] += 1
                                check_boundaries[i+1][2] = False
                    for i in range(len(check_boundaries)):
                        check_boundaries[i][2] = True
            for i in range(num_methods):
                count = 0
                for j in range(len(check_boundaries)):
                    if check_boundaries[j][1] == i:
                        count += 1
                count = count / len(check_boundaries)
                stack[itt][i] = count
            itt += 1
        stack = np.asarray(stack)
        stacked_boundary_plot = go.Figure(data=[
            go.Bar(name='Unique', x=names, y=stack[:, 0])])
        for i in range(1, len(stack)):
            title = str(i) + " methods"
            stacked_boundary_plot.add_bar(name=title, x=names, y=stack[:, i])
        stacked_boundary_plot.update_layout(barmode='stack', template='simple_white')
        stacked_boundary_plot.update_layout(legend_title_text='Boundaries found in:', xaxis_title='Callers', yaxis_title='Percent of Shared Boundaries')
    else:
        stacked_boundary_plot = px.bar()
    return stacked_boundary_plot


@app.callback(
    Output("Stacked Domain Plot", "figure"),
    [Input('TAD dict binned', 'data'),
     Input('Stacked Domain Options', 'value')])
def set_display_stacked_Domain_map(tad_dict_binned, stacked_domain_option):
    tolerance = int(stacked_domain_option)
    itt = 0
    num_methods = len(tad_dict_binned.keys())
    names = list(tad_dict_binned.keys())
    if num_methods > 1:
        stack = [[0 for x in range(num_methods)] for y in range(num_methods)]
        for check_key in names:
            check_bed = tad_dict_binned[check_key]
            check_boundaries = [[0 for x in range(3)] for y in range(len(check_bed) * 2)]
            for i in range(0, 2 * len(check_bed), 2):
                test = math.floor(i / 2)
                check_boundaries[i][0] = check_bed[test][0]
                check_boundaries[i][1] = 0
                check_boundaries[i][2] = True
                check_boundaries[i + 1][0] = check_bed[test][1]
                check_boundaries[i + 1][1] = 0
                check_boundaries[i + 1][2] = True
            for key in names:
                if key != check_key:
                    bed = tad_dict_binned[key]
                    for row in bed:
                        for i in range(0, len(check_boundaries), 2):
                            if check_boundaries[i][2] and \
                                    math.isclose(row[0], check_boundaries[i][0], abs_tol=tolerance) and \
                                    math.isclose(row[1], check_boundaries[i + 1][0], abs_tol=tolerance):
                                check_boundaries[i][1] += 1
                                check_boundaries[i + 1][1] += 1
                                check_boundaries[i][2] = False
                    for i in range(len(check_boundaries)):
                        check_boundaries[i][2] = True
            for i in range(num_methods):
                count = 0
                for j in range(len(check_boundaries)):
                    if check_boundaries[j][1] == i:
                        count += 1
                count = count / len(check_boundaries)
                stack[itt][i] = count
            itt += 1
        stack = np.asarray(stack)
        stacked_domain_plot = go.Figure(data=[
            go.Bar(name='Unique', x=names, y=stack[:, 0])])
        for i in range(1, len(stack)):
            title = str(i) + " methods"
            stacked_domain_plot.add_bar(name=title, x=names, y=stack[:, i])
        stacked_domain_plot.update_layout(barmode='stack', template='simple_white')
        stacked_domain_plot.update_layout(legend_title_text='Domains found in:', xaxis_title='Callers', yaxis_title='Percent of Shared Domains')
    else:
        stacked_domain_plot = px.bar()
    return stacked_domain_plot


@app.callback(
    Output("MoC Comparison Plot", "figure"),
    [Input('MoC data', 'data'),
     Input('TAD dict binned', 'data'),
     Input('MoC Options', 'value')])
def set_MoC_Comparison(MoC, tad_dict_binned, MoC_option):
    print("Construct MoC_Comparison")
    print(MoC)
    MoC_Comparison_plot = px.bar()
    names = list(tad_dict_binned.keys())
    if len(MoC) > 1:
        row_select = 0
        i = 0
        for filename in names:
            if filename in MoC_option:
                row_select = i
            i += 1
        MoC_Comparison_plot.add_bar(x=names, y=MoC[row_select])
        MoC_Comparison_plot.update_layout(template='simple_white')
        MoC_Comparison_plot.update_yaxes(title_text="Measure of Concordance")
        MoC_Comparison_plot.update_xaxes(title_text="Callers")
    else:
        MoC_Comparison_plot = px.bar()
    return MoC_Comparison_plot


@app.callback(
    Output("MoC Plot", "figure"),
    [Input('MoC data', 'data'),
     Input('TAD dict binned', 'data')])
def set_MoC(MoC, tad_dict_binned):
    names = list(tad_dict_binned.keys())
    MoC_plot = px.bar()
    if len(MoC) > 1:
        average = []
        for row in MoC:
            average.append(sum(row) / len(row))
        MoC_plot.add_bar(x=names, y=average)
        MoC_plot.update_layout(template='simple_white')
        MoC_plot.update_yaxes(title_text="Average Measure of Concordance")
        MoC_plot.update_xaxes(title_text="Callers")
    else:
        MoC_plot = px.bar()
    return MoC_plot


@app.callback(
    Output("TSNE Plot", "figure"),
    [Input('MoC data', 'data'),
     Input('TAD dict binned', 'data'),
     Input("tnse-marker-slider", "value"),
     Input('TSNE Slider', 'value')])
def set_TNSE(MoC, tad_dict_binned, markersize, slider):
    names = list(tad_dict_binned.keys())
    if len(MoC) > 1:
        person_matrix = np.corrcoef(MoC)
        tsne_pca = TSNE(n_components=2, perplexity=slider, method='exact', init='pca')
        tsne_random = TSNE(n_components=2, perplexity=slider, method='exact', init='random')
        projections_pca = tsne_pca.fit_transform(person_matrix)
        projections_random = tsne_random.fit_transform(person_matrix)
        TNSE_plot = make_subplots(rows=2, cols=1, vertical_spacing=0.25,
                                  subplot_titles=('Initial Embedding: PCA', 'Initial Embedding: Random'))
        for i in range(len(names)):
            TNSE_plot.add_trace(go.Scatter(
                x=[projections_pca[i][0]], y=[projections_pca[i][1]], mode='markers',
                marker_color=colors[i], marker_size=markersize, text=names[i], name=names[i]
            ), row=1, col=1)
            TNSE_plot.add_trace(go.Scatter(
                x=[projections_random[i][0]], y=[projections_random[i][1]], mode='markers',
                marker_color=colors[i], marker_size=markersize, text=names[i], name=names[i], showlegend=False
            ), row=2, col=1)
        TNSE_plot.update_layout(template='simple_white')
    else:
        TNSE_plot = px.bar()
    return TNSE_plot


@app.callback(
    Output("PCA Plot", "figure"),
    [Input('MoC data', 'data'),
     Input('TAD dict binned', 'data'),
     Input("pca-marker-slider", "value"),
     Input('Normalization', 'value')])
def set_PCA(MoC, tad_dict_binned, markersize, norm_path):
    names = list(tad_dict_binned.keys())
    if len(os.listdir(norm_path)) > 1:
        person_matrix = np.corrcoef(MoC)
        pca = PCA(n_components=2, random_state=0)
        projections = pca.fit_transform(person_matrix)
        PCA_plot = px.scatter(
            projections, x=0, y=1,
            color=names, labels={'color': 'Methods'},
            color_discrete_sequence=colors
        )
        PCA_plot.update_traces(marker=dict(size=markersize))
        PCA_plot.update_layout(template='simple_white')
        PCA_plot.update_layout(xaxis_title='Principal Component 1', yaxis_title='Principal Component 2')
    else:
        PCA_plot = px.bar()
    return PCA_plot


def save_file(name, content, norm):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(norm, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


@app.callback(
    [Output("upload button", "style"),
     Output("upload button", "href")],
    [Input("upload-data", "filename"),
     Input("upload-data", "contents"),
     Input("upload-title", "value"),
     Input("target_id", "value"),
     Input('Normalization', 'value')],
)
def update_output(uploaded_filename, uploaded_file_content, optional_title, id, norm):
    if uploaded_filename is not None and uploaded_file_content is not None:
        if optional_title is not None:
            uploaded_filename = optional_title + ".bed"
        ref = "/TADMaster/visualize/" + str(id)
        save_file(uploaded_filename, uploaded_file_content, norm)
        return [dict(), ref]
    else:
        return [dict(display='none'), '']


@app.callback(
    [Output("download button", "href")],
    [Input("target_id", "value")],
)
def update_output(id):
    ref = "/TADMaster/download/" + str(id)
    return [ref]


@app.callback(
    [Output("heatmap button", "href")],
    [Input("target_id", "value")],
)
def update_output(id):
    ref = "/TADMaster/heatmap/" + str(id)
    return [ref]

@app.callback(
    [Output("heatmap button", 'disabled')],
    [Input("target_id", "value")],
)
def disable_heat_map_button(id):
    data = Data.objects.get(pk=id)
    if str(data.document):
        return [False]
    else:
        return [True]

