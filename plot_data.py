import json
import plotly
from plotly import express as px
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

def IRV_sankey(rankings, labelList, sourceList, targetList, valuesList):
    """
    creates a sankey plot for the IRV data
    args:
        rankings:   list of candidate rankings in order from first place
                    to last place (produced by voting_systems.IRV())
        labelList:  list of candidates in order of how they ranked each round
                    (produced by voting_systems.IRV())
        sourceList: list of candidates from which votes will move
                    (produced by voting_systems.IRV())
        targetList: list of candidates to which votes will move
                    (produced by voting_systems.IRV())
        valuesList: list of how many votes move from between candidates
                    (produced by voting_systems.IRV())
    returns:
        a sankey plot in the form of a JSON object
    """
    n = len(rankings)

    # Node position
    xList = [round(j/n+0.01,3) for j in range(n) for name in rankings[:n-j]]
    yList = [round(k/n+0.01,3) for j in range(n) for k in range(len(rankings[:n-j]))]

    # Node and link colors
    ColorDict = {rankings[j].split()[-1] : f'hsva({200+20*j},{100-12.5*j}%,100%,0.5)' for j in range(n)}
    nodeColorList = [ColorDict[name[:-1]] for name in labelList]
    linkColorList = [ColorDict[name[:-1]] for name in sourceList]

    # encoding labels for source and target lists
    indices = {key: val for val, key in enumerate(labelList)}
    sourceList = [indices.get(item,item)  for item in sourceList]
    targetList = [indices.get(item,item)  for item in targetList]

    # Removing indices at end of names for presentation
    labelList = [name[:-1] for name in labelList]
    
    # Creating sankey figure
    fig = go.Figure(data=[go.Sankey(arrangement='snap',
                                    node = dict(pad = 30,
                                                thickness = 10,
                                                line = dict(color = "black",
                                                            width = 0.5),
                                                label = labelList,
                                                color = nodeColorList,
                                                x = xList,
                                                y = yList,
                                                hovertemplate='%{value} votes<extra></extra>'),
                                    link = dict(source = sourceList,
                                                target = targetList,
                                                value = valuesList,
                                                color = linkColorList,
                                                hovertemplate='%{value} votes move from %{source.label} to %{target.label}<extra></extra>'))])

    # adding labels for each round of IRV
    for j in range(n):
        columnTitle = f"Round {j+1}"        # label text
        xCoord = j/8+(j//3)*0.037 - 0.025   # label position
        fig.add_annotation(x = xCoord,
                        y = 1.07,
                        xref = "paper",
                        yref = "paper",
                        text = columnTitle,
                        showarrow = False,
                        font = dict(size=14))
        
    # adding figure title and adjusting margins
    fig.update_layout(title_text = "Sankey Diagram for IRV Rounds",
                      margin = {"r":50,"t":100,"l":50,"b":50},
                      font_size = 12)

    # converting figure into a json object
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)