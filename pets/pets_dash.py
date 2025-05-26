#!/usr/bin/env python
# coding: utf-8

# import libraries
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd
import polars as pl
import duckdb as db
import os
from dotenv import load_dotenv
import plotly.express as px
from pathlib import Path
load_dotenv('../.env')

# create app
app = Dash()

# database connection
# motherduck
token = os.getenv('MD_TOKEN')
conn = db.connect(f"md:?motherduck_token={token}")
weights = conn.sql('select * from family_lm.main.peso').pl()
conn.close()

app.layout = html.Div([
    html.H1('LM Family Pets Dashboard', style={"font-family":"Open Sans", "color":"#3F5661",}),
    dcc.Markdown('''
        *In this report we will show the last events about diseases, vaccines, surgeries,
        weight and grooming for family pets*.
    '''),
    html.Br(),
    'Pick a name',
    dcc.Dropdown(
        options=weights['Nombre'].unique().to_list(),
        value='Reyna',
        id='pets-dropdown'
    ),
    html.H3(id='pets-output'),
    dcc.Graph(id="graph"),
    html.H1('Contact', style={"font-family":"Open Sans", "color": "#3F5661"}),     
    html.P('Jesus L. Monroy', style={"font-family":"Open Sans", 
                                     'font-weight':'bold'}), 
    html.I('Economist & Data Scientist', style={"font-family":"Open Sans"})
])

@app.callback(
    Output("pets-output", "children"),
    Output("graph", "figure"),
    Input("pets-dropdown", "value")
)

def plot_pets(pet):
    if not pet:
        raise PreventUpdate
    filtered = weights.filter(pl.col('Nombre')==pet)
    fig = px.line(
        filtered,
        x='Fecha',
        y='Peso',
        hover_data=['Fecha','Peso',],
        height=500,
    )
    fig.update_layout(
        xaxis=dict(title=dict(text='')),
        yaxis=dict(title=dict(text='Peso')),
        #yaxis_range=[0, 80],
        plot_bgcolor='#ececec',
    )
    fig.update_traces(line_color='#9A607F', line={'width':3})

    title = f"Evolucion del Peso de {pet.title()}"
    return title, fig

# run app
if __name__ == "__main__":
    app.run_server()

