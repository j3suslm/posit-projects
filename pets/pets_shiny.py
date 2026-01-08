import os
import polars as pl
import duckdb as db
import plotly.express as px
from dotenv import load_dotenv
from pathlib import Path

from shiny import reactive, render
from shiny.express import input, ui
from shinywidgets import render_plotly

_ = load_dotenv('.env')


# Link the CSS file
# 1. Get the directory where your current script (e.g., app.py) is located
dir = Path('__file__').parent

# 2. Join that directory with your filename
css_path = dir / "pets/www/custom.css"

# 3. Use the path in your code
ui.include_css(css_path)

# --- 1. Data Connection ---
try:
    token = os.getenv('MD_TOKEN')
    conn = db.connect(f"md:?motherduck_token={token}")   
    weights = conn.sql('select Fecha, Nombre, Categoria, Peso from family_lm.peso').pl()
    conn.close()
except Exception as e:
    print(f"Error connecting to database or fetching data: {e}")

pet_names = weights['Nombre'].unique().to_list() if not weights.is_empty() else []

# --- 2. Simplified UI ---
ui.page_opts(title="LM Family Pets", fillable=True)


# Sidebar: All inputs and contact info go here
with ui.sidebar(width=270, fillable=True):
    with ui.card(style="height: 80%; border: none; box-shadow: none;"):
        ui.input_select(
            "pets_dropdown", 
            "Pick a name", 
            choices=pet_names
        )
    with ui.card(style="height: 20%; border: none; box-shadow: none;"):
        ui.markdown("**Contact** <br> Jesus LM <br> *Economist & Data Scientist*")

    @reactive.calc
    def filtered_df():
        if not input.pets_dropdown():
            return pl.DataFrame()
        return weights.filter(pl.col('Nombre') == input.pets_dropdown())

# Use a Card to automatically group and style the graph
with ui.card(height="55%", full_screen=True):
    ui.card_header("Weight Evolution Chart")
    @render_plotly
    def weight_graph():
        df = filtered_df()
        if df.is_empty(): return None
            
        fig = px.line(
            df,
            x='Fecha',
            y='Peso',
            hover_data=['Fecha', 'Peso'],
            title=f"Evolution of Weight for {input.pets_dropdown()}"
        )

        fig.update_layout(
            xaxis=dict(title=dict(text='')),
            yaxis=dict(title=dict(text='Weight')),
            plot_bgcolor='#f4f4f4',
            paper_bgcolor='#f8f8f8',
            title_x=0.5, # Center the title
            autosize=True,
            margin=dict(l=0, r=0, t=35, b=20),
        )

        fig.update_traces(line_color=' #2e4053', line={'width': 3})

        return fig

# Use a Card for the table
with ui.card(height="45%", full_screen=True):
    ui.card_header("History of Weight Logs")
    @render.data_frame
    def pets_table():
    # DataGrid is natively scrollable and maintains header alignment
        return render.DataGrid(
            filtered_df().sort(by='Fecha', descending=True),
            width="100%",
            height="95%", 
            summary=True,  # Shows "Viewing 1-10 of 50"
            filters=False, # Adds search boxes under each column header
        )
