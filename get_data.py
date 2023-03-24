from plotly import express as px
import pandas as pd
import voting_systems

def get_plurality_df():
    """
    converts plurality data into a pandas dataframe
    args:
        None
    returns:
        a pandas dataframe that contains all the plurality data
    """
    # getting plurality data using the plurality() function in voting_systems.py
    # data in the form of a list of tuples
    pluralityList = voting_systems.plurality("votes") 
    # converting data into pandas dataframe
    pluralityDF = pd.DataFrame(pluralityList, columns = ['Candidate', 'Number of Votes'])
    return pluralityDF

def get_borda_df(point_dict = {1:5, 2:4, 3:3, 4:2, 5:1}):
    """
    converts borda count data into a pandas dataframe
    args:
        point_dict: a dictionary that holds the number of points per rank
    returns:
        a pandas dataframe that contains all the borda count data
    """
    # getting borda count data using the borda() function in voting_systems.py
    # data in the form of a list of tuples
    bordaList = voting_systems.borda("votes", point_dict)
    # converting data into pandas dataframe
    bordaDF = pd.DataFrame(bordaList, columns = ['Candidate', 'Number of Points'])
    return bordaDF

def get_irv_df():
    """
    converts the instant runoff data into a pandas dataframe
    args:
        none
    returns:
        a pandas dataframe that contains all the instant runoff data
    """
    # getting instant runoff count data using the IRV() function in voting_systems.py
    # data in the form of a list of tuples
    rankings, label, source, target, value  = voting_systems.IRV("votes")
    irvList = rankings[:5]
    # converting data into pandas dataframe
    irvDF = pd.DataFrame(irvList, columns = ['Rankings'])
    return irvDF, rankings, label, source, target, value

def get_toptwo_df():
    """
    converts the top-two runoff data into a pandas dataframe
    args:
        none
    returns:
        a pandas dataframe that contains all the instant runoff data
    """
    # getting top-two runoff count data using the TopTwo() function in voting_systems.py
    # data in the form of a list of tuples
    toptwoList = voting_systems.TopTwo("votes")
    # converting data into pandas dataframe
    toptwoDF = pd.DataFrame(toptwoList, columns = ['Candidate'])
    return toptwoDF
