import json
import plotly
from plotly import express as px
import pandas as pd
import voting_systems
import plotly.graph_objects as go

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

### NEEDS WORK ###
def IRV_sankey(rankings, sourceList, targetList, valuesList):
    n = len(rankings)

    # Node position
    xList = [round(j/8+0.01,3) for j in range(n) for name in rankings[:n-j]]
    yList = [round(k/8+0.01,3) for j in range(n) for k in range(len(rankings[:n-j]))]

    # Ordered labels
    labelList = [name.split()[-1] + str(j) for j in range(n) for name in rankings[:n-j]]
    labelList

    # Node and link colors
    ColorDict = {rankings[j].split()[-1] : f'hsva({200-25*j},{100-12.5*j}%,100%,0.5)' for j in range(n)}
    nodeColorList = [ColorDict[name[:-1]] for name in labelList]
    linkColorList = [ColorDict[name[:-1]] for name in sourceList]

    # encoding labels for source and target lists
    indices = {key: val for val, key in enumerate(labelList)}
    sourceList = [indices.get(item,item)  for item in sourceList]
    targetList = [indices.get(item,item)  for item in targetList]

    # creating the Sankey figure
    fig = go.Figure(data=[go.Sankey(arrangement='snap',
                                    node = dict(pad = 30,
                                                thickness = 10,
                                                line = dict(color = "black", width = 0.5),
                                                label = labelList,
                                                color = nodeColorList,
                                                x = xList,
                                                y = yList),
                                    link = dict(source = sourceList,
                                                target = targetList,
                                                value = valuesList,
                                                color = linkColorList))])
    
    # adding titles
    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    # converting figure into a json object
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)