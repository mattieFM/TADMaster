import dash
import csv
import os
import base64
from PIL import Image
import matplotlib
from matplotlib import cm
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from PIL import Image
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

app = DjangoDash(name='HeatMap', external_stylesheets=[dbc.themes.SPACELAB], add_bootstrap_links=True)

# ------------------------------------------------------------------------------
image_filename = '/var/www/html/TADMaster/Site/manyTAD/static/image/nlogo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
image_example = '/var/www/html/TADMaster/Site/manyTAD/static/image/Example_BED_File.png'
encoded_example = base64.b64encode(open(image_example, 'rb').read())
color_scales = list(set(plt.colormaps()).intersection(px.colors.named_colorscales()))
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
                        html.Div(id='page_warning', style={"text-align": "center", "margin-top": "5px", "color": "#FF0000"}),
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
    Output('page_warning', 'children'),
    [Input('target_id', 'value'),
     Input('Normalization', 'value')])
def set_warning(id, norm_path):
    message = ''
    data = Data.objects.get(pk=id)
    job_id = str(data.job_id)
    heat_matrix_path = '/var/www/html/TADMaster/Site/storage/data/job_' + job_id + '/normalizations'
    for topdir, dirs, files in os.walk(heat_matrix_path):
        display_file = ""
        for file in files:
            if os.path.splitext(file)[0] == os.path.basename(norm_path):
                display_file = file
        if display_file == "":
            display_file = "Raw.txt"
        displayed_matrix = os.path.join(topdir, display_file)
    if os.path.getsize(displayed_matrix) >200000000:
        message = "Warning: The matrix provided is larger than the expected file size; matrix load times maybe unpredictable."
    else:
        message = "Please Note: In order to provide a detailed visualization experience heatmaps are loaded at full resolution; matrix load times are proportional to the size of the provided matrix."
    return message

@app.callback(
    [Output('page_description', 'children'),
     Output('page_resolution', 'children'),
     Output('page_chromosome', 'children')],
    [Input('target_id', 'value')])
def set_description(id):
    data = Data.objects.get(pk=id)
    return data.description, str(data.resolution), str(data.chromosome)


@app.callback(
    Output('Heat Map Options', 'options'),
    [Input('Normalization', 'value'),
     Input('target_id', 'value')])
def set_heat_map_options(norm_path, id):
    data = Data.objects.get(pk=id)
    relsolution = data.resolution
    chromosome = data.chromosome
    options = []
    for filename in os.listdir(norm_path):
        with open(os.path.join(norm_path, filename), 'r') as file:
            spamreader = csv.reader(file)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(file.read(1024))
            file.seek(0)
            tad_data = [[digit for digit in line.strip().split(sep=dialect.delimiter)] for line in file]
            if len(tad_data[0]) == 2:
                tad_data = np.asarray(tad_data, dtype='float')
            elif len(tad_data[0]) == 3:
                temp_data = []
                for i in range(len(tad_data)):
                    if tad_data[i][0] == str(chromosome) or tad_data[i][0] == 'chr' + str(chromosome):
                        temp_data.append(tad_data[i][1:])
                tad_data = np.asarray(temp_data, dtype='float')
            if tad_data.size != 0:
                options.append({'label': filename[:-4], 'value': filename})
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
     Input("Heat Map Scale", "value"),
     Input('Heat Map Options', 'options')])
def set_display_heat_map(norm_path, heat_map_options, heat_map_colorscale, id, scale, opt_list):
    callback_context = [dic['prop_id'].split('.')[0] for dic in dash.callback_context.triggered]
    print(callback_context)
    data = Data.objects.get(pk=id)
    resolution = int(data.resolution)
    chromosome = int(data.chromosome)
    job_id = str(data.job_id)
    options = []
    for iteam in opt_list:
        options.append(iteam['label'])
    #start = time.process_time()
    if heat_map_colorscale == 'TADMaster':
        heat_map_color = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "tomato", "red", "orange", "yellow"])
        legend_color = tad_master_color
    else:
        heat_map_color = heat_map_colorscale
        legend_color = heat_map_color
    heat_matrix_path = '/var/www/html/TADMaster/Site/storage/data/job_' + job_id + '/normalizations'
    for topdir, dirs, files in os.walk(heat_matrix_path):
        display_file = ""
        for file in files:
            if os.path.splitext(file)[0] == os.path.basename(norm_path):
                display_file = file
        if display_file == "":
            display_file = "Raw.txt"
        displayed_matrix = os.path.join(topdir, display_file)
    with open(displayed_matrix, 'r') as file:
        contact_matrix = [[float(digit) for digit in line.split()] for line in file]
    if scale == 'Log':
        contact_matrix = np.asarray(contact_matrix)
        contact_matrix = contact_matrix + 1
        contact_matrix = np.log(contact_matrix)

    xmin = 0
    xmax = len(contact_matrix)
    ymin = 0
    ymax = len(contact_matrix)
    amin = np.amin(contact_matrix)
    amax = np.amax(contact_matrix)
    cNorm = Normalize(vmin=amin, vmax=amax)
    scalarMap = cm.ScalarMappable(norm=cNorm, cmap=heat_map_color)
    seg_colors = scalarMap.to_rgba(contact_matrix)
    raw_img = Image.fromarray(np.uint8(seg_colors * 255))
    raw_copy = raw_img
    matrix_img = raw_img.rotate(90)
    #print(time.process_time() - start)
    max_len = 0
    if heat_map_options:
        for filename in os.listdir(norm_path):
            if filename in heat_map_options:
                with open(os.path.join(norm_path, filename), 'r') as file:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(file.read(1024))
                    file.seek(0)
                    tad_data = [[digit for digit in line.strip().split(sep=dialect.delimiter)] for line in file]
                    if len(tad_data[0]) == 2:
                        tad_data = np.asarray(tad_data, dtype='float')
                    elif len(tad_data[0]) == 3:
                        temp_data = []
                        for i in range(len(tad_data)):
                            if tad_data[i][0] == str(chromosome) or tad_data[i][0] == 'chr' + str(chromosome):
                                temp_data.append(tad_data[i][1:])
                        tad_data = np.asarray(temp_data, dtype='float')
                    if tad_data.size != 0:
                        tad_data = np.asarray(tad_data)
                        tad_data = tad_data/resolution
                        for line in tad_data:
                            if max_len < (line[1] - line[0]):
                                max_len = (line[1] - line[0])

    rotated_img = raw_copy.rotate(45, expand=True)
    width, height = rotated_img.size
    left = 0
    rotated_y_buffer = max_len * math.sqrt(3)/2
    top = height / 2 - rotated_y_buffer
    right = width
    bottom = height / 2
    scaling_factor = (xmax-xmin)/width
    rotated_img = rotated_img.crop((left, top, right, bottom))

    #print(time.process_time() - start)
    #print("Construct Heat Map")
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.25,
                        subplot_titles=('Contact Heatmap', 'Triangular Heatmap Projection'),
                        row_width=[0.1, 0.5])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(title_text="Region Number", row=1, col=1)
    fig.update_yaxes(title_text="Region Number", row=1, col=1)
    fig.update_xaxes(title_text="Region Number", visible=True, color='#444', row=2, col=1)
    fig.update_yaxes(showticklabels=False,  row=2, col=1)
    fig.append_trace(
        go.Scatter(
            x=[xmin, xmax],
            y=[ymin, ymax],
            mode="markers",
            showlegend=False,
            marker={"color": [np.amin(contact_matrix), np.amax(contact_matrix)],
                    "colorscale": legend_color,
                    "showscale": True,
                    "colorbar": {"title": "Counts",
                                 "titleside": "right"},
                    "opacity": 0
                    }
        )
        , 1, 1
    )

    # Add image
    fig.update_layout(
        images=[dict(
            x=xmin,
            sizex=xmax - xmin,
            y=ymax,
            sizey=ymax - ymin,
            xref="x",
            yref="y",
            layer="below",
            source=matrix_img),
        ]
    )
    fig.add_layout_image(
        x=0,
        row=2,
        col=1,
        sizex=xmax - xmin,
        y=0,
        xanchor="left",
        yanchor="bottom",
        sizey=rotated_y_buffer,
        sizing="stretch",
        xref="x",
        yref="y",
        opacity=1.0,
        layer="below",
        source=rotated_img,
    )
    # Configure other layout
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, range=[xmin, xmax]),
        yaxis=dict(showgrid=False, zeroline=False, range=[ymin, ymax]),
    )

    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
    #print(time.process_time() - start)
    color_itt = 0

    if heat_map_options:
        for filename in os.listdir(norm_path):
            if filename in heat_map_options:
                with open(os.path.join(norm_path, filename), 'r') as file:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(file.read(1024))
                    file.seek(0)
                    tad_data = [[digit for digit in line.strip().split(sep=dialect.delimiter)] for line in file]
                    if len(tad_data[0]) == 2:
                        tad_data = np.asarray(tad_data, dtype='float')
                    elif len(tad_data[0]) == 3:
                        temp_data = []
                        for i in range(len(tad_data)):
                            if tad_data[i][0] == str(chromosome) or tad_data[i][0] == 'chr' + str(chromosome):
                                temp_data.append(tad_data[i][1:])
                        tad_data = np.asarray(temp_data, dtype='float')
                    if tad_data.size != 0:
                        tad_data = np.asarray(tad_data)
                        bed = tad_data/resolution
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
                            tri_line_y.append((line[1] - line[0]) * math.sqrt(3)/2 * scaling_factor)
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
            if filename[:-4] in options:
                color_itt += 1
    #print(time.process_time() - start)
    fig.update_xaxes(matches='x')
    fig.update_xaxes(showline=True, linewidth=1, ticks="inside", linecolor='black', row=2, col=1)
    fig.update_layout(showlegend=True)
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.15
    ))
    fig.update_coloraxes()
    #print(time.process_time() - start)
    return fig


