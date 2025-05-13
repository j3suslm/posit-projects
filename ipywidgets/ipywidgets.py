import pandas as pd
import polars as pl
import seaborn as sns
import ipywidgets as widgets

df = pl.read_csv('https://raw.githubusercontent.com/posit-hosted/examples-jupyter/refs/heads/main/data/penguins_clean.csv')

df = df.drop_nulls()

opts = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]

@widgets.interact(attribute=opts)
def penguins_box(attribute = "body_mass_g"):
    g = sns.boxplot(x = 'island',
                    y = attribute,
                    hue = 'species',
                    data = df,
                    palette=['#FF8C00','#159090','#A034F0'],
                    linewidth=0.3)

