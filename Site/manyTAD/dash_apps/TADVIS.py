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

app = DjangoDash(name='TADVIS', external_stylesheets=[dbc.themes.SPACELAB], add_bootstrap_links=True) 

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

   	html.Div(
        [
            dbc.Row(
                dbc.Col(
                    style = {"marginTop": "100px", "backgroundColor": "#f2f2f2", "paddingTop": "25px", "paddingBottom": "15px", "borderRadius": "10px"},
                    children = html.Div([

    # ------------------------------------------------------------------------------
    # Normalizations
    # ------------------------------------------------------------------------------
        html.Div(
        [
	html.A([
        html.Div(
        [
    		html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height':'75%', 'width':'75%'}),

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
                dbc.Card([dbc.CardBody("Please provide your TAD .bed File. Click below to see an example Bed File."),
                dbc.Button("Example .bed file", id="open_example"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Example Bed File"),
                        dbc.ModalBody(
                            html.Img(src='data:image/png;base64,{}'.format(encoded_example.decode()), style={'height':'75%', 'width':'75%'})
                        ),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="close_example", className="ml-auto")
                        ),
                    ],
                    id="modal_example",
                ),
                html.H4("Title:"),
                dbc.Input(id="upload-title", placeholder="Title", type="text"),
                dcc.Upload(
                id="upload-data",
                children=html.Div(
                    ["Drag and drop or click to upload a file."]
                ),
                style={
                    "width": "90%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
            
                multiple=False,
                ),
                dbc.Button("Upload", id='upload button', href="", external_link=True , style = dict(display='none')),
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
            ], style={"align-items": "center", "justify-content": "center", "display": "flex"}),
            ),
            dbc.Col(
                dbc.Button("Download Data", id='download button', href="", external_link=True , style={"float": "right"})
            ),
        ]),
        ]),
    html.H2(children="Title", className="header_text", style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),
    html.Div(id='page_title', style={"text-align": "center", "margin-top": "5px"}),

    html.H2(children="Description", className="header_text", style={"textAlign": "center", "color": "#708090", "fontWeight": "600"}),
    html.Div(id='page_description', style={"text-align": "center", "margin-top": "5px"}),

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
    # ------------------------------------------------------------------------------
    # Heat Map
    # ------------------------------------------------------------------------------
    html.Div([
        dbc.Button(
            html.H4(children="TAD Heat Map", className="header_text", 
                style={"textAlign": "center", "fontWeight": "600", "marginBottom": "0px"}),
                id="collapse-button-heatmap",
                size='lg',
                color="light",
                block=True,
                style = {"marginTop": "50px"}
            ),

        dbc.Collapse(
            [
                dbc.Card([dbc.CardBody("Please click below to view the heatmap for your results."),
                dbc.Button("View Heatmap", id='heatmap button', href="", external_link=True, target="_blank", style={"align-self": "center", "margin-bottom": "20px"}),
            ], style={'marginTop': 20}),

              
            ],

            id="collapse-heatmap",
            is_open=True
        )

    ], style={'marginTop': 20}),

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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                        dbc.Checklist(
                                            id="Whisker Options",
                                            inline=True,
                                            style={"textAlign": "center"}
                                        ),
                                        dbc.Label("Plot Width Slider", html_for="slider"),
                                        dcc.Slider(id='size-TAD-slider', min=5, max=100, step=5, value=50,),

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
                                dcc.Graph(id="Whisker Plot", style = {}),], 
                                style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                        dbc.RadioItems(
                                            id="Boundary Options",
                                            inline=True,
                                            style={"textAlign": "center"}
                                        ),
                                        dbc.Label("Plot Width Slider", html_for="slider"),
                                        dcc.Slider(id='shared-boundaries-slider', min=5, max=100, step=5, value=100,),

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
                                dcc.Graph(id="Boundary Plot", style = {}),], 
                                style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Tolerance:", style={"marginTop": "10px"}),
                                        dbc.RadioItems(
                                            id="Stacked Boundary Options",
                                            options=[{'label': 'Zero', 'value': '0'},
                                                    {'label': 'One', 'value': '1'},
                                                    {'label': 'Two', 'value': '2'},
                                                    {'label': 'Three', 'value': '3'}],
                                            value = '1',
                                            inline=True,
                                            style={"textAlign": "center"}
                                        ),
                                        dbc.Label("Plot Width Slider", html_for="slider"),
                                        dcc.Slider(id='stacked-boundary-slider', min=5, max=100, step=5, value=50,),

                                    ],
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
                                dcc.Graph(id="Stacked Boundary Plot", style = {}),], 
                                style={ 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Tolerance:", style={"marginTop": "10px"}),
                                        dbc.RadioItems(
                                            id="Stacked Domain Options",
                                            options=[{'label': 'Zero', 'value': '0'},
                                                    {'label': 'One', 'value': '1'},
                                                    {'label': 'Two', 'value': '2'},
                                                    {'label': 'Three', 'value': '3'}],
                                            value = '1',
                                            inline=True,
                                            style={"textAlign": "center"}
                                        ),
                                        dbc.Label("Plot Width Slider", html_for="slider"),
                                        dcc.Slider(id='stacked-domain-slider', min=5, max=100, step=5, value=50,),

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
                                dcc.Graph(id="Stacked Domain Plot", style = {}),], 
                                style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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
            html.H4(children="Comparison of Domain Overlap (Measure of Concordance)", className="header_text", 
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Method:", style={"marginTop": "10px"}),
                                        dbc.RadioItems(
                                            id="MoC Options",
                                            inline=True,
                                            style={"textAlign": "center"}
                                        ),
                                        dbc.Label("Plot Width Slider", html_for="slider"),
                                        dcc.Slider(id='moc-compare-slider', min=5, max=100, step=5, value=50,),

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
                                dcc.Graph(id="MoC Comparison Plot", style = {}),], 
                                style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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
            html.H4(children="Comparison of Average Domain Overlap (Measure of Concordance)", className="header_text", 
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Plot Width Slider", style={"marginTop": "10px"}),
                                        dcc.Slider(id='moc-average-slider', min=5, max=100, step=5, value=50,),
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
                                dcc.Graph(id="MoC Plot", style = {}),], 
                                style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Select Perplexity:", style={"marginTop": "10px"}),
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
                                        dcc.Slider(id='tnse-marker-slider', min=1, max=20, step=1, value=10,),
                                    ], style={'width': '100%', 'display': 'inline-block'}
                                ),
                                width={"size": 6, "offset": 3},
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
                                dcc.Graph(id="TSNE Plot", style = {'width': '100%', 'height': '100%'}),], 
                                style={'width': '100%', 'height': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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

                                children = dbc.FormGroup(
                                    [
                                        dbc.Label("Marker Size Slider", style={"marginTop": "10px"}),
                                        dcc.Slider(id='pca-marker-slider', min=1, max=20, step=1, value=10,),
                                    ], style={'width': '100%', 'display': 'inline-block'}
                                ),
                                width={"size": 6, "offset": 3},
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
                                dcc.Graph(id="PCA Plot", style = {'width': '100%', 'height': '100%'}),], 
                                style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})),
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
    Output('page_title', 'children'),
    [Input('target_id', 'value')])
def set_title(id):
    data = Data.objects.get(pk=id)
    return data.title

@app.callback(
    Output('page_description', 'children'),
    [Input('target_id', 'value')])
def set_description(id):
    data = Data.objects.get(pk=id)
    return data.description


@app.callback(
    Output('Heat Map Options', 'options'),
    [Input('Normalization', 'value')])
def set_heat_map_options(norm):
    return [{'label': i[:-4], 'value': i} for i in os.listdir(norm)]


@app.callback(
    Output('Number TADs Options', 'options'),
    [Input('Normalization', 'value')])
def set_num_tads_options(norm):
    return [{'label': i[:-4], 'value': i} for i in os.listdir(norm)]

@app.callback(
    Output('Number TADs Plot', 'style'),
    [Input('num-TAD-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style

@app.callback(
    Output('Whisker Options', 'options'),
    [Input('Normalization', 'value')])
def set_whisker_options(norm):
    return [{'label': i[:-4], 'value': i} for i in os.listdir(norm)]

@app.callback(
    Output('Whisker Plot', 'style'),
    [Input('size-TAD-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style


@app.callback(
    Output('Boundary Options', 'options'),
    [Input('Normalization', 'value')])
def set_boundary_options(norm):
    return [{'label': i[:-4], 'value': i} for i in os.listdir(norm)]


@app.callback(
    Output('Boundary Plot', 'style'),
    [Input('shared-boundaries-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style


@app.callback(
    Output('Stacked Boundary Plot', 'style'),
    [Input('stacked-boundary-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style


@app.callback(
    Output('Stacked Domain Plot', 'style'),
    [Input('stacked-domain-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style


@app.callback(
    Output('MoC Comparison Plot', 'style'),
    [Input('moc-compare-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style


@app.callback(
    Output('MoC Plot', 'style'),
    [Input('moc-average-slider', 'value')])
def set_num_tads_options(size):
    style = {}
    style['width'] = str(size)+'%'
    style['height'] = str(size)+'%'
    return style


@app.callback(
    Output('MoC Options', 'options'),
    [Input('Normalization', 'value')])
def set_MoC_options(norm):
    return [{'label': i[:-4], 'value': i} for i in os.listdir(norm)]


@app.callback(
    Output('Heat Map Options', 'value'),
    [Input('Heat Map Options', 'options')])
def set_heat_map_value(available_options):
    return [available_options[0]['value']]


@app.callback(
    Output('Number TADs Options', 'value'),
    [Input('Number TADs Options', 'options')])
def set_num_tads_value(available_options):
    return [available_options[0]['value']]


@app.callback(
    Output('Whisker Options', 'value'),
    [Input('Whisker Options', 'options')])
def set_whisker_value(available_options):
    return [available_options[0]['value']]


@app.callback(
    Output('Boundary Options', 'value'),
    [Input('Boundary Options', 'options')])
def set_boundary_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('MoC Options', 'value'),
    [Input('MoC Options', 'options')])
def set_MoC_value(available_options):
    return available_options[0]['value']
# ------------------------------------------------------------------------------
# Plot Generators
# -----------------------------------------------------------------------------

@app.callback(
    Output("Heat Map", "figure"),
    [Input('Normalization', 'value'),
    Input('Heat Map Options', 'value'),
    Input("colorscale", "value"),
    Input("target_id", "value"),
    Input("Heat Map Scale", "value")])
def set_display_heat_map(norm_path, heat_map_options, heat_map_colorscale, id, scale):
    start = time.process_time()    
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    job_id = str(data.job_id)
    start = time.process_time()
# ------------------------------------------------------------------------------
# Construct Heat Map
# ------------------------------------------------------------------------------
    if heat_map_colorscale == 'TADMaster':
        heat_map_color = [[0.0, "rgb(255,255,255)"],
                                  [0.1111111111111111, "rgb(255,230,230)"],
                                  [0.2222222222222222, "rgb(255,153,153)"],
                                  [0.3333333333333333, "rgb(255,77,77)"],
                                  [0.4444444444444444, "rgb(255,0,0)"],
                                  [0.5555555555555556, "rgb(255,42,0)"],
                                  [0.6666666666666666, "rgb(255,85,0)"],
                                  [0.7777777777777778, "rgb(255,173,0)"],
                                  [0.8888888888888888, "rgb(255,213,0)"],
                                  [1.0, "rgb(255,255,0)"]]
    else:
        heat_map_color = heat_map_colorscale
    heat_matrix_path='/var/www/html/TADMaster/Site/storage/data/job_'+ job_id+'/normalizations'
    for topdir, dirs, files in os.walk(heat_matrix_path):
        firstfile = sorted(files)[0]
        displayed_matrix = os.path.join(topdir, firstfile)
    with open(displayed_matrix, 'r') as file:
        contact_matrix = [[float(digit) for digit in line.split()] for line in file]
    if scale == 'Log':
        contact_matrix = np.asarray(contact_matrix)
        contact_matrix = contact_matrix + 1
        contact_matrix = np.log(contact_matrix)
    #px_heat = px.imshow(data, color_continuous_scale=heat_map_color)
    print(time.process_time() - start)
    max_len = 0
    if heat_map_options:
        for filename in os.listdir(norm_path):
            if filename in heat_map_options:
                with open(os.path.join(norm_path, filename), 'r') as file:
                    bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                    bed = np.asarray(bed)
                    bed = bed / resolution
                    for line in bed:
                        if max_len < (line[1] - line[0]):
                            max_len = (line[1] - line[0])
    mod_contact_matrix = [[None for i in range(len(contact_matrix))] for j in range(int(max_len))]
    for j in range(int(max_len)):
        for i in range(len(contact_matrix)):

            if i < j or i >= len(contact_matrix) - j:
                mod_contact_matrix[j][i] = 0
            else:
                mod_contact_matrix[j][i] = contact_matrix[i-j][i+j]
    print(time.process_time() - start)    
    print("Construct Heat Map")
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.25,
                          subplot_titles=('Contact Heat Map', 'TADS'),
                          row_width=[0.1, 0.5])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(title_text="Region Number", row=1, col=1)
    fig.update_yaxes(title_text="Region Number", row=1, col=1)
    fig.update_xaxes(title_text="Region Number", visible=True, color='#444', row=2, col=1)
    fig.update_yaxes(title_text="TAD Span", row=2, col=1)

    test = go.Heatmap(z=contact_matrix, colorbar=dict(lenmode='fraction', len=0.75, y=0.63),
                      colorscale=heat_map_color)
    test2 = go.Heatmap(z=mod_contact_matrix, showscale=False, colorscale=heat_map_color)

    fig.append_trace(test, 1, 1)
    fig.append_trace(test2,2,1)
    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
    print(time.process_time() - start)
    color_itt = 0

    if heat_map_options:
        for filename in os.listdir(norm_path):
            if filename in heat_map_options:
                with open(os.path.join(norm_path, filename), 'r') as file:
                    bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                    bed = np.asarray(bed)
                    bed = bed / resolution
                    top_line_x =[]
                    top_line_y =[]
                    bot_line_x =[]
                    bot_line_y =[]
                    tri_line_x =[]
                    tri_line_y =[]
                    for line in bed:
                        top_line_x.append(line[0])
                        top_line_y.append(line[0])
                        top_line_x.append(line[0])
                        top_line_y.append(line[1])
                        top_line_x.append(line[1])
                        top_line_y.append(line[1])

                        bot_line_x.append(line[0])
                        bot_line_y.append(line[0])
                        bot_line_x.append(line[1])
                        bot_line_y.append(line[0])
                        bot_line_x.append(line[1])
                        bot_line_y.append(line[1])

                        tri_line_x.append(line[0])
                        tri_line_y.append(0)
                        tri_line_x.append(line[0] + (line[1] - line[0])/2)
                        tri_line_y.append((line[1] - line[0])/math.sqrt(2))
                        tri_line_x.append(line[1])
                        tri_line_y.append(0)                 
                    fig.add_trace(go.Scatter(x=top_line_x, y=top_line_y, mode="lines", name=filename[:-4], line=dict(color=colors[color_itt])), row=1, col=1)                 
                    fig.add_trace(go.Scatter(x=bot_line_x, y=bot_line_y, mode="lines", line=dict(color=colors[color_itt]), showlegend=False), row=1, col=1)
                    fig.add_trace(go.Scatter(x=tri_line_x, y=tri_line_y, mode="lines", line=dict(color=colors[color_itt]), showlegend=False), row=2, col=1)
            color_itt += 1
    print(time.process_time() - start)
    fig.update_xaxes(matches='x')
    fig.update_xaxes(showline=True, linewidth=1, ticks="inside", linecolor='black', row=2, col=1)
    fig.update_yaxes(showline=True, linewidth=1, ticks="inside", linecolor='black', row=2, col=1)
    fig.update_layout(showlegend=True)
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.15
    ))
    fig.update_coloraxes()
    print(time.process_time() - start)
    return fig


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


@app.callback(
    Output("Whisker Plot", "figure"),
    [Input('Normalization', 'value'),
    Input("target_id", "value"),
    Input('Whisker Options', 'value')])
def set_display_whisker_map(norm_path, id, whisker_options):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    print("Construct Whisker Plot")
    size_tads = []
    color_itt = 0
    color_dict = {}
    for file in os.listdir(norm_path):
        color_dict[file[:-4]] = colors[color_itt]
        color_itt += 1
        number_tads = []
    if whisker_options:
        for filename in os.listdir(norm_path):
            if filename in whisker_options:
                with open(os.path.join(norm_path, filename), 'r') as file:
                    bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                    bed = np.asarray(bed)
                    bed = bed / resolution
                    for row in bed:
                        size_tads.append([filename[:-4], row[1] - row[0]])
        box_df = pd.DataFrame(data=size_tads, columns=["Callers", "Size of TADs"])
        whisker_plot = px.box(box_df, x="Callers", y="Size of TADs", color="Callers", color_discrete_map=color_dict, template='simple_white')
    else:
        whisker_plot = px.box()
    return whisker_plot


@app.callback(
    Output("Boundary Plot", "figure"),
    [Input('Normalization', 'value'),
    Input("target_id", "value"),
    Input('Boundary Options', 'value')])
def set_display_boundary_map(norm_path, id, boundary_option):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    color_itt = 0
    color_dict = {}
    for file in os.listdir(norm_path):
        color_dict[file[:-4]] = colors[color_itt]
        color_itt += 1
        number_tads = []
    boundaries = []
    if boundary_option:
        with open(os.path.join(norm_path, boundary_option), 'r') as check_file:
            check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check_file]
        check_bed = np.asarray(check_bed)
        check_bed = check_bed / resolution
        for tolerance in range(10):
            for filename in os.listdir(norm_path):
                if filename not in boundary_option:
                    shared_boundaries = 0
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for row in bed:
                        for check in check_bed:
                            if math.isclose(row[0], check[0], abs_tol=tolerance):
                                shared_boundaries += 1
                            if math.isclose(row[1], check[1], abs_tol=tolerance):
                                shared_boundaries += 1
                    boundaries.append([filename[:-4], tolerance, shared_boundaries])
        shared_boundaries_df = pd.DataFrame(data=boundaries, columns=["Callers", "Tolerance", "Shared Boundaries"])
        boundary_plot = px.bar(shared_boundaries_df, x="Tolerance", y="Shared Boundaries", color="Callers", barmode='group',
                       color_discrete_map=color_dict, template='simple_white')
    else:
        boundary_plot = px.bar()
    return boundary_plot

@app.callback(
    Output("Stacked Boundary Plot", "figure"),
    [Input('Normalization', 'value'),
    Input("target_id", "value"),
    Input('Stacked Boundary Options', 'value')])
def set_display_stacked_boundary_map(norm_path, id, stacked_boundary_option):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    tolerance = int(stacked_boundary_option)
    itt = 0

    if len(os.listdir(norm_path)) > 1:
        stack = [[0 for x in range(len(os.listdir(norm_path)))] for y in range(len(os.listdir(norm_path)))]
        names = []
        for file in os.listdir(norm_path):
            names.append(file[:-4])
        for check_file in os.listdir(norm_path):
            with open(os.path.join(norm_path, check_file), 'r') as check:
                check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check]
            check_bed = np.asarray(check_bed)
            check_bed = check_bed / resolution
            check_boundaries = [[0 for x in range(2)] for y in range(len(check_bed)*2)]
            for i in range(0, 2*len(check_bed), 2):
                test = math.floor(i/2)
                check_boundaries[i][0] = check_bed[test][0]
                check_boundaries[i][1] = 1
                check_boundaries[i+1][0] = check_bed[test][1]
                check_boundaries[i+1][1] = 1
            count_cap = 2
            for filename in os.listdir(norm_path):
                if filename != check_file:
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for row in bed:
                        for i in range(len(check_boundaries)):
                            if math.isclose(row[0], check_boundaries[i][0], abs_tol=tolerance) and check_boundaries[i][1] < count_cap:
                                check_boundaries[i][1] += 1
                            if math.isclose(row[1], check_boundaries[i][0], abs_tol=tolerance) and check_boundaries[i][1] < count_cap:
                                check_boundaries[i][1] += 1

                    for i in range(1, len(os.listdir(norm_path))+1):
                        count = 0
                        for j in range(len(check_boundaries)):
                            if check_boundaries[j][1] == i:
                                count += 1
                        count = count / len(check_boundaries)
                        stack[itt][i-1] = count
                    count_cap += 1
            itt += 1
        stack = np.asarray(stack)
        stacked_boundary_plot = go.Figure(data=[
            go.Bar(name='Unique',color_discret_map=colors, x=names, y=stack[:,0])])
        for i in range(1, len(stack)):
            title = str(i) + " methods"
            stacked_boundary_plot.add_bar(name=title, x=names, y=stack[:,i])
        stacked_boundary_plot.update_layout(barmode='stack', template='simple_white')
        stacked_boundary_plot.update_layout(legend_title_text='Boundaries found in:')
    else:
        stacked_boundary_plot = px.bar()
    return stacked_boundary_plot


@app.callback(
    Output("Stacked Domain Plot", "figure"),
    [Input('Normalization', 'value'),
    Input("target_id", "value"),
    Input('Stacked Domain Options', 'value')])
def set_display_stacked_Domain_map(norm_path, id, stacked_domain_option):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    tolerance = int(stacked_domain_option)
    itt = 0

    if len(os.listdir(norm_path)) > 1:
        stack = [[0 for x in range(len(os.listdir(norm_path)))] for y in range(len(os.listdir(norm_path)))]
        names = []
        for file in os.listdir(norm_path):
            names.append(file[:-4])
        for check_file in os.listdir(norm_path):
            with open(os.path.join(norm_path, check_file), 'r') as check:
                check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check]
            check_bed = np.asarray(check_bed)
            check_bed = check_bed / resolution
            check_boundaries = [[0 for x in range(2)] for y in range(len(check_bed)*2)]
            for i in range(0, 2*len(check_bed), 2):
                test = math.floor(i/2)
                check_boundaries[i][0] = check_bed[test][0]
                check_boundaries[i][1] = 1
                check_boundaries[i+1][0] = check_bed[test][1]
                check_boundaries[i+1][1] = 1
            count_cap = 2
            for filename in os.listdir(norm_path):
                if filename != check_file:
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for row in bed:
                        for i in range(0, len(check_boundaries), 2):
                            if math.isclose(row[0], check_boundaries[i][0], abs_tol=tolerance) and \
                                math.isclose(row[1], check_boundaries[i+1][0], abs_tol=tolerance) and \
                                check_boundaries[i][1] < count_cap:
                                check_boundaries[i][1] += 1
                                check_boundaries[i+1][1] += 1

                    for i in range(1, len(os.listdir(norm_path))+1):
                        count = 0
                        for j in range(len(check_boundaries)):
                            if check_boundaries[j][1] == i:
                                count += 1
                        count = count / len(check_boundaries)
                        stack[itt][i-1] = count
                    count_cap += 1
            itt += 1
        stack = np.asarray(stack)
        stacked_domain_plot = go.Figure(data=[
            go.Bar(name='Unique', x=names, y=stack[:,0])])
        for i in range(1, len(stack)):
            title = str(i) + " methods"
            stacked_domain_plot.add_bar(name=title, x=names, y=stack[:,i])
        stacked_domain_plot.update_layout(barmode='stack', template='simple_white')
        stacked_domain_plot.update_layout(legend_title_text='Domains found in:')
    else:
        stacked_domain_plot = px.bar()
    return stacked_domain_plot

@app.callback(
    Output("MoC Comparison Plot", "figure"),
    [Input('Normalization', 'value'),
    Input("target_id", "value"),
    Input('MoC Options', 'value')])
def set_MoC_Comparison(norm_path, id, MoC_option):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    MoC_Comparison_plot = px.bar()
    itt = 0
    if len(os.listdir(norm_path)) > 1:
        names = []
        MoC = [[None for i in range(len(os.listdir(norm_path)))] for j in range(len(os.listdir(norm_path)))]
        for file in os.listdir(norm_path):
            names.append(file[:-4])
        for check_file in os.listdir(norm_path):
            with open(os.path.join(norm_path, check_file), 'r') as check:
                check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check]
            check_bed = np.asarray(check_bed)
            check_bed = check_bed / resolution
            file_count = 0
            for filename in os.listdir(norm_path):
                if filename == check_file:
                    MoC[itt][file_count] = 1
                else:
                    avg_MoC = []
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for check_row in check_bed:
                        for row in bed:
                            if check_row[0] < row[1] and check_row[1] > row[0]:
                                if check_row[1] <= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] <= row[1] and check_row[0] <= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] >= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                else:
                                    avg_MoC.append(math.pow(row[1] - row[0], 2)/((check_row[1] - check_row[0])*(row[1]- row[0])))
                            else:
                                avg_MoC.append(0)
                    if len(avg_MoC) == 1:
                        MoC[itt][file_count] = avg_MoC[0]
                    else:
                        MoC[itt][file_count] = sum(avg_MoC)/(math.sqrt(len(avg_MoC))-1)
                file_count += 1

            itt += 1
        MoC = np.asarray(MoC)
        row_select = 0
        i = 0
        for filename in os.listdir(norm_path):
            if filename in MoC_option:
                row_select = i
            i += 1
        MoC_Comparison_plot.add_bar(x=names, y=MoC[row_select])
        MoC_Comparison_plot.update_layout(template='simple_white')
        MoC_Comparison_plot.update_yaxes(title_text="Measure of Concordance")
        
    else:
        MoC_Comparison_plot = px.bar()
    return MoC_Comparison_plot


@app.callback(
    Output("MoC Plot", "figure"),
    [Input("target_id", "value"),
    Input('Normalization', 'value')])
def set_MoC(id, norm_path):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    MoC_plot = px.bar()
    itt = 0
    if len(os.listdir(norm_path)) > 1:
        names = []
        MoC = [[None for i in range(len(os.listdir(norm_path)))] for j in range(len(os.listdir(norm_path)))]
        for file in os.listdir(norm_path):
            names.append(file[:-4])
        for check_file in os.listdir(norm_path):
            with open(os.path.join(norm_path, check_file), 'r') as check:
                check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check]
            check_bed = np.asarray(check_bed)
            check_bed = check_bed / resolution
            file_count = 0
            for filename in os.listdir(norm_path):
                if filename == check_file:
                    MoC[itt][file_count] = 1
                else:
                    avg_MoC = []
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for check_row in check_bed:
                        for row in bed:
                            if check_row[0] < row[1] and check_row[1] > row[0]:
                                if check_row[1] <= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] <= row[1] and check_row[0] <= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] >= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                else:
                                    avg_MoC.append(math.pow(row[1] - row[0], 2)/((check_row[1] - check_row[0])*(row[1]- row[0])))
                            else:
                                avg_MoC.append(0)

                    if len(avg_MoC) == 1:
                        MoC[itt][file_count] = avg_MoC[0]
                    else:
                        MoC[itt][file_count] = sum(avg_MoC)/(math.sqrt(len(avg_MoC))-1)

                file_count += 1

            itt += 1
        MoC = np.asarray(MoC)
        average = []
        for row in MoC:
            average.append(sum(row)/len(row))

        MoC_plot.add_bar(x=names, y=average)
        MoC_plot.update_layout(template='simple_white')
        MoC_plot.update_yaxes(title_text="Average Measure of Concordance")
    else:
        MoC_plot = px.bar()
    return MoC_plot

@app.callback(
    Output("TSNE Plot", "figure"),
    [Input('Normalization', 'value'),
    Input("target_id", "value"),
    Input("tnse-marker-slider", "value"),
    Input('TSNE Slider', 'value')])
def set_TNSE(norm_path, id, markersize, slider):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    itt = 0
    if len(os.listdir(norm_path)) > 1:
        names = []
        MoC = [[None for i in range(len(os.listdir(norm_path)))] for j in range(len(os.listdir(norm_path)))]
        for file in os.listdir(norm_path):
            names.append(file[:-4])
        for check_file in os.listdir(norm_path):
            with open(os.path.join(norm_path, check_file), 'r') as check:
                check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check]
            check_bed = np.asarray(check_bed)
            check_bed = check_bed / resolution
            file_count = 0
            for filename in os.listdir(norm_path):
                if filename == check_file:
                    MoC[itt][file_count] = 1
                else:
                    avg_MoC = []
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for check_row in check_bed:
                        for row in bed:
                            if check_row[0] < row[1] and check_row[1] > row[0]:
                                if check_row[1] <= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] <= row[1] and check_row[0] <= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] >= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                else:
                                    avg_MoC.append(math.pow(row[1] - row[0], 2)/((check_row[1] - check_row[0])*(row[1]- row[0])))
                            else:
                                avg_MoC.append(0)

                    if len(avg_MoC) == 1 and avg_MoC[0] > 0:
                        MoC[itt][file_count] = avg_MoC[0]
                    elif sum(avg_MoC) <= 0:
                        MoC[itt][file_count] = .000001
                    else:
                        MoC[itt][file_count] = sum(avg_MoC)/(math.sqrt(len(avg_MoC))-1)

                file_count += 1

            itt += 1
        MoC = np.asarray(MoC)
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
    [Input("target_id", "value"),
    Input("pca-marker-slider", "value"),
    Input('Normalization', 'value')])
def set_PCA(id, markersize, norm_path):
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    itt = 0
    if len(os.listdir(norm_path)) > 1:
        names = []
        MoC = [[None for i in range(len(os.listdir(norm_path)))] for j in range(len(os.listdir(norm_path)))]
        for file in os.listdir(norm_path):
            names.append(file[:-4])
        for check_file in os.listdir(norm_path):
            with open(os.path.join(norm_path, check_file), 'r') as check:
                check_bed = [[float(digit) for digit in line.split(sep=',')] for line in check]
            check_bed = np.asarray(check_bed)
            check_bed = check_bed / resolution
            file_count = 0
            for filename in os.listdir(norm_path):
                if filename == check_file:
                    MoC[itt][file_count] = 1
                else:
                    avg_MoC = []
                    with open(os.path.join(norm_path, filename), 'r') as file:
                        bed = [[float(digit) for digit in line.split(sep=',')] for line in file]
                        bed = np.asarray(bed)
                        bed = bed / resolution
                    for check_row in check_bed:
                        for row in bed:
                            if check_row[0] < row[1] and check_row[1] > row[0]:
                                if check_row[1] <= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] <= row[1] and check_row[0] <= row[0]:
                                    avg_MoC.append(math.pow(check_row[1] - row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                elif check_row[1] >= row[1] and check_row[0] >= row[0]:
                                    avg_MoC.append(math.pow(row[1] - check_row[0], 2) / (
                                                (check_row[1] - check_row[0]) * (row[1] - row[0])))
                                else:
                                    avg_MoC.append(math.pow(row[1] - row[0], 2)/((check_row[1] - check_row[0])*(row[1]- row[0])))
                            else:
                                avg_MoC.append(0)

                    if len(avg_MoC) == 1 and avg_MoC[0] > 0:
                        MoC[itt][file_count] = avg_MoC[0]
                    elif sum(avg_MoC) <= 0:
                        MoC[itt][file_count] = .000001
                    else:
                        MoC[itt][file_count] = sum(avg_MoC)/(math.sqrt(len(avg_MoC))-1)

                file_count += 1

            itt += 1
        MoC = np.asarray(MoC)
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
