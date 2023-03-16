import json
import plotly
from plotly import express as px
import pandas as pd
import voting_systems

def get_plurality_df():
    pluralityList = voting_systems.plurality("votes")
    pluralityDF = pd.DataFrame(pluralityList, columns = ['Candidate', 'Number of Votes'])
    return pluralityDF

def get_borda_df(point_dict = {1:5, 2:4, 3:3, 4:2, 5:1}):
    bordaList = voting_systems.borda("votes", point_dict)
    bordaDF = pd.DataFrame(bordaList, columns = ['Candidate', 'Number of Points'])
    return bordaDF

def get_irv_df():
    irvList = voting_systems.IRV("votes")
    irvDF = pd.DataFrame(irvList, columns = ['Rankings'])
    return irvDF

def get_toptwo_df():
    toptwoList = voting_systems.TopTwo("votes")
    toptwoDF = pd.DataFrame(toptwoList, columns = ['Candidate'])
    return toptwoDF
