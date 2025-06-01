# import shiny express and widgets
from shiny.express import ui, render, input
from shinywidgets import render_plotly
from shinywidgets import render_widget


# import other libraries
import plotly.express as px
import pandas as pd
from data_import import df

ui.page_opts(title="Penguins")

with ui.card():
    # markdown text
    ui.markdown(
        """
        # My First App with Shiny

        This is a testing **web app** using *shiny* for `Python`

        [Portfolio](https://tinyurl.com/jesuslm-website)
        """
    )


# sidebar
with ui.sidebar(open='closed', bg='#f8f8f8'):
    # slider widget
    ui.input_slider('mass', 'Max Body Mass', 2_000, 8_000, 6_000)


with ui.layout_columns():

    with ui.card():
        'Chart'
                
        # chart
        @render_plotly
        def plot():
            df_subset = df[df['body_mass_g'] < input.mass()]
            if input.show_species():
                return px.scatter(df_subset, x='bill_depth_mm', y='bill_length_mm', color='species')
            else:
                return px.scatter(df_subset, x='bill_depth_mm', y='bill_length_mm')

        ui.input_checkbox('show_species', 'Show Species', value=True)


    with ui.card():
        'Raw data'
        # table
        @render.data_frame
        def data():
            return df[df['body_mass_g'] < input.mass()]
