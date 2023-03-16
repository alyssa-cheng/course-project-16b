import json
import plotly
from plotly import express as px
import pandas as pd
import voting_systems

def plurality_plot(df):
    fig = px.bar(data_frame = df, 
                 x = 'Candidate', 
                 y = 'Number of Votes',
                 hover_name = 'Candidate',
                 width = 700,
                 height = 400)

    fig.update_layout(title = "Plurality Candidate Votes", xaxis_title = 'Name of Candidate', yaxis_title = 'Number of Votes')

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def borda_plot(df, point_dict = {1:5, 2:4, 3:3, 4:2, 5:1}):
    fig = px.bar(data_frame = df, 
                 x = 'Candidate', 
                 y = 'Number of Points',
                 hover_name = 'Candidate',
                 width = 700,
                 height = 400)

    fig.update_layout(title = "Borda Count Candidate Votes", xaxis_title = 'Name of Candidate', yaxis_title = 'Number of Points')

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)