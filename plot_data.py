import json
import plotly
from plotly import express as px
import pandas as pd
import voting_systems

def plurality_plot(df):
    """
    creates a plot for the plurality data
    args:
        df: the dataframe that will be used in the plot
    returns:
        a plot in the form of a JSON object
    """
    # creating the plot using plotly
    fig = px.bar(data_frame = df, 
                 x = 'Candidate', 
                 y = 'Number of Votes',
                 hover_name = 'Candidate',
                 width = 700,
                 height = 400)

    # adding titles
    fig.update_layout(title = "Plurality Candidate Votes", xaxis_title = 'Name of Candidate', yaxis_title = 'Number of Votes')

    # converting figure into a json object
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def borda_plot(df):
    """
    creates a plot fo the borda count data
    args:
        df: the dataframe that will be used in the plot
    returns:
        a plot in the form of a JSON object
    """
    # creating the plot using plotly
    fig = px.bar(data_frame = df, 
                 x = 'Candidate', 
                 y = 'Number of Points',
                 hover_name = 'Candidate',
                 width = 700,
                 height = 400)

    # adding titles
    fig.update_layout(title = "Borda Count Candidate Votes", xaxis_title = 'Name of Candidate', yaxis_title = 'Number of Points')

    # converting figure into a json object
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)