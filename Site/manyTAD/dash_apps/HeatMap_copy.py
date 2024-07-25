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

from plotly.data import iris

# ------------------------------------------------------------------------------

app = DjangoDash(name='HeatMap_copy', external_stylesheets=[dbc.themes.SPACELAB], add_bootstrap_links=True)

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
tad_master_color = [[0.0, "rgb(255,255,255)"],
                    [0.1111111111111111, "rgb(255,230,230)"],
                    [0.2222222222222222, "rgb(255,153,153)"],
                    [0.3333333333333333, "rgb(255,77,77)"],
                    [0.4444444444444444, "rgb(255,0,0)"],
                    [0.5555555555555556, "rgb(255,42,0)"],
                    [0.6666666666666666, "rgb(255,85,0)"],
                    [0.7777777777777778, "rgb(255,173,0)"],
                    [0.8888888888888888, "rgb(255,213,0)"],
                    [1.0, "rgb(255,255,0)"]]

app.layout = html.Div([
    dcc.Input(id='target_id', type='hidden', value='filler text'),
    dcc.Location(id='url', refresh=False),

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
                        html.P(
                            "Please Note: In order to provide a detailed visualization experience heatmaps are loaded at full resolution; matrix load times are proportional to the size of the provided matrix.",
                            style={"color": "#FF0000"}),
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
                                style={"marginTop": "50px"}
                            ),

                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                dbc.Col(

                                                    [dbc.FormGroup(
                                                        [
                                                            dbc.Label("Select Methods:", style={"marginTop": "10px"}),
                                                            dbc.Checklist(
                                                                id="Heat Map Options",
                                                                inline=True,
                                                                style={"textAlign": "center"}
                                                            ),

                                                        ]
                                                    ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(html.Div([
                                                                    dbc.FormGroup(
                                                                        [
                                                                            dbc.Label("Select Scaling:",
                                                                                      style={"marginTop": "10px"}),
                                                                            dbc.RadioItems(
                                                                                options=[
                                                                                    {"value": 'Log', "label": 'Log'},
                                                                                    {"value": 'Raw', "label": 'Raw'}],
                                                                                value='Log',
                                                                                id="Heat Map Scale",
                                                                                inline=True,
                                                                            ),

                                                                        ]
                                                                    )
                                                                ]), width=4),

                                                                dbc.Col(html.Div([
                                                                    dbc.FormGroup(
                                                                        [
                                                                            dbc.Label("Select Color Scale:",
                                                                                      style={"marginTop": "10px"}),
                                                                            dcc.Dropdown(
                                                                                id='colorscale',
                                                                                options=[{"value": x, "label": x}
                                                                                         for x in color_scales],
                                                                                value='TADMaster'
                                                                            ),
                                                                        ]
                                                                    )
                                                                ]), width=4),
                                                            ], justify="center", )

                                                    ], width={"size": 10, "offset": 1},

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
                                                                    dcc.Graph(id="Heat Map", style={'width': '100%',
                                                                                                    'height': '100%'}), ],
                                                                    style={'width': '100%', 'height': '100%',
                                                                           'display': 'flex', 'align-items': 'center',
                                                                           'justify-content': 'center'})),
                                                                className="mb-3",
                                                                style={'height': '63vw'})
                                                        ], style={'height': '63vw'})]),

                                ],

                                id="collapse-heatmap",
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
# ------------------------------------------------------------------------------


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
    available_options = [{'label': os.path.basename(i), 'value': i} for i in available_normalizations]
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
    options = [{'label': os.path.splitext(i)[0], 'value': i} for i in os.listdir(norm)]
    return options


@app.callback(
    Output('Heat Map Options', 'value'),
    [Input('Heat Map Options', 'options')])
def set_heat_map_value(available_options):
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
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    job_id = str(data.job_id)
    start = time.process_time()
    if heat_map_colorscale == 'TADMaster':
        heat_map_color = tad_master_color
    else:
        heat_map_color = heat_map_colorscale
    heat_matrix_path = '/var/www/html/TADMaster/Site/storage/data/job_' + job_id + '/normalizations'
    for topdir, dirs, files in os.walk(heat_matrix_path):
        display_file = ""
        for file in files:
            if os.path.splitext(file)[0] == os.path.basename(norm_path):
                display_file = file
        print(os.path.splitext(display_file))
        displayed_matrix = os.path.join(topdir, display_file)
    with open(displayed_matrix, 'r') as file:
        contact_matrix = [[float(digit) for digit in line.split()] for line in file]
    if scale == 'Log':
        contact_matrix = np.asarray(contact_matrix)
        contact_matrix = contact_matrix + 1
        contact_matrix = np.log(contact_matrix)

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
                mod_contact_matrix[j][i] = contact_matrix[i - j][i + j]
    print(time.process_time() - start)
    print("Construct Heat Map")
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.25,
                        subplot_titles=('Contact Heat Map', 'TADS'),
                        row_width=[0.1, 0.5])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(title_text="Region Number", row=1, col=1)
    fig.update_yaxes(title_text="Region Number", row=1, col=1)
    fig.update_xaxes(title_text="Region Number", visible=True, color='#444', row=2, col=1)

    test = go.Heatmap(z=contact_matrix, colorbar=dict(lenmode='fraction', len=0.75, y=0.63),
                      colorscale=heat_map_color)
    test2 = go.Heatmap(z=mod_contact_matrix, showscale=False, colorscale=heat_map_color)

    fig.append_trace(test, 1, 1)
    fig.append_trace(test2, 2, 1)
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
                    top_line_x = []
                    top_line_y = []
                    bot_line_x = []
                    bot_line_y = []
                    tri_line_x = []
                    tri_line_y = []
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
                        tri_line_x.append(line[0] + (line[1] - line[0]) / 2)
                        tri_line_y.append((line[1] - line[0]) / math.sqrt(2))
                        tri_line_x.append(line[1])
                        tri_line_y.append(0)
                    fig.add_trace(go.Scatter(x=top_line_x, y=top_line_y, mode="lines", name=filename[:-4],
                                             line=dict(color=colors[color_itt])), row=1, col=1)
                    fig.add_trace(
                        go.Scatter(x=bot_line_x, y=bot_line_y, mode="lines", line=dict(color=colors[color_itt]),
                                   showlegend=False), row=1, col=1)
                    fig.add_trace(
                        go.Scatter(x=tri_line_x, y=tri_line_y, mode="lines", line=dict(color=colors[color_itt]),
                                   showlegend=False), row=2, col=1)
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
