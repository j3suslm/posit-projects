# Import libraries
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd
import polars as pl
import duckdb as db
import plotly.express as px
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv('.env')


# Create app
# Added suppress_callback_exceptions=True to allow elements to be updated
# even if they are not present on the initial page load.
app = Dash(__name__, suppress_callback_exceptions=True)

# Database connection
try:
    # database connection
    # motherduck
    token = os.getenv('MD_TOKEN')
    conn = db.connect(f"md:?motherduck_token={token}")   
    weights = conn.sql('select Fecha, Nombre, Categoria, Peso from family_lm.peso').pl()
    conn.close()
except Exception as e:
    print(f"Error connecting to database or fetching data: {e}")
    # Initialize an empty Polars DataFrame if there's a DB issue
    weights = pl.DataFrame({"Fecha": [], "Nombre": [], "Categoria": [], "Peso": []})

# Layout
app.layout = html.Div([
    # Title
    html.H1('LM Family Pets', className='app-title', style={'color':' #2e4053',
        'font-size':'300%'}),
    # Paragraph
    dcc.Markdown('''
        *In this report we will show the last events about diseases, vaccines, surgeries,
        weight and grooming for family pets*.
    ''', className='app-intro'),
    html.Br(),
    # Dropdown menu
    html.Div([html.Label(html.P('Pick a pet', className='dropdown-label')),
    dcc.Dropdown(
        options=[{'label': name, 'value': name} for name in weights['Nombre'].unique().to_list()],
        value='Reyna', # Default value
        id='pets-dropdown',
        clearable=False, # Prevents the user from clearing the selection
    )], style={'width':'30%',}),
    html.Br(),
    # table
    html.H3(id='pets-output', className='section-title'),
    dcc.Graph(id="graph"),
    html.Br(),
    html.Div([html.H3(id='table-title', className='section-title'),
    html.Div(id='pets-table', className='table-container'), # Wrap DataTable in a Div
    ], style={'width': '90%', 
            #'display': 'flex', <- to make table narrower
            'align-items': 'center', 'justify-content': 'center'}),
    # Footer
    html.H1('Contact', className='contact-title', style={'color':' #2e4053', 'font-size':'200%'}),
    html.P('Jesus L. Monroy', className='contact-name', style={'color':'#4d5656', 'font-size':'110%'}),
    html.I('Economist & Data Scientist', className='contact-role', style={'color':'#4d5656', 'font-size':'110%'})
], className='main-container',
    style={'backgroundColor':'#f8f8f8',}) # Add a class to the main container

# Callback to update graph and table
@app.callback(
    Output("pets-output", "children"),
    Output("graph", "figure"),
    Output("table-title", "children"),
    Output("pets-table", "children"),
    Input("pets-dropdown", "value"),
)

def update_pets_data(pet):
    if not pet:
        raise PreventUpdate
    # Filter data for the selected pet
    filtered_weights = weights.filter(pl.col('Nombre') == pet)
    # Generate graph
    fig = px.line(
        filtered_weights,
        x='Fecha',
        y='Peso',
        hover_data=['Fecha', 'Peso'],
        height=500,
        title=f"Evolution of Weight for {pet.title()}"
    )
    fig.update_layout(
        xaxis=dict(title=dict(text='')),
        yaxis=dict(title=dict(text='Weight')),
        plot_bgcolor='#f4f4f4',
        paper_bgcolor='#f8f8f8',
        title_x=0.5 # Center the title
    )
    fig.update_traces(line_color=' #2e4053', line={'width': 3})

    # Prepare data for the table
    # Convert filtered Polars DataFrame to Pandas for Dash DataTable
    table_df = filtered_weights.to_pandas()

    table_component = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in table_df.columns],
        data=table_df.to_dict("records"),
        export_format="csv",
        style_table={'overflowX': 'auto'}, # Allow horizontal scrolling for large tables
        #fill_width=False,
        style_header={
            'backgroundColor': '#2e4053',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_cell={
            'padding-right': '10px',
            'padding-left': '10px',
            'text-align': 'center',
            'marginLeft': 'auto',
            'marginRight': 'auto'
            },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f4f4f4'
            }
        ]
    )

    return f"", fig, f"", table_component

# Run app
if __name__ == "__main__":
    app.run_server(debug=True) # Set debug=True for development

