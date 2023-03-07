from flask import Flask, render_template, abort, redirect, url_for, json, request, g
import json
import plotly
from plotly import express as px
import pandas as pd
import sqlite3
import voting_systems

app = Flask(__name__)

def get_voting_db():
    return voting_systems.get_voter_db()

def get_plurality_df():
    pluralityList = voting_systems.plurality("votes")
    pluralityDF = pd.DataFrame(pluralityList, columns = ['Candidate', 'Number of Votes'])
    return pluralityDF

def plurality_graph():
    df = get_plurality_df()
    fig = px.bar(data_frame = df, 
                 x = 'candidate', 
                 y = 'number of votes',
                 hover_name = 'candidate',
                 width = 700,
                 height = 400)

    fig.update_layout(title = "Plurality Candidate Votes", xaxis_title = 'Name of Candidate', yaxis_title = 'Number of Votes')

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_borda_df(point_dict = {1:1, 2:2, 3:3, 4:4, 5:5}):
    bordaList = voting_systems.borda("votes", point_dict)
    bordaDF = pd.DataFrame(bordaList, columns = ['Candidate', 'Cumulative Points'])
    return bordaDF

@app.route("/", methods = ["GET", "POST"])
def render_main():
    if request.method == "GET":
        # g.table = voting_systems.make_table() #change this later
        return render_template("main.html")
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/plurality/", methods = ["GET", "POST"])
def render_plurality():
    if request.method == "GET":
        graphJSON = plurality_graph()
        return render_template("plurality.html", graphJSON = graphJSON)
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/bordacount/", methods = ["GET", "POST"])
def render_borda():
    if request.method == "GET":
        bordaDF_og = get_borda_df()
        bordaDF_og = bordaDF_og.to_html(index=False)
        return render_template("bordacount.html", bordaDF_og = bordaDF_og)
    else:
        if request.form["submit"] == "Submit Rank Values":
            bordaDF_og = get_borda_df()
            bordaDF_og = bordaDF_og.to_html(index=False)
            
            rank1 = request.form['rank1']
            rank2 = request.form['rank2']
            rank3 = request.form['rank3']
            rank4 = request.form['rank4']
            rank5 = request.form['rank5']

            point_dict = {1 : rank1,
                          2 : rank2,
                          3 : rank3,
                          4 : rank4,
                          5 : rank5}
            
            bordaDF_interact = get_borda_df(point_dict)
            bordaDF_interact = bordaDF_interact.to_html(index=False)
            return render_template("bordacount.html", bordaDF_interact = bordaDF_interact, bordaDF_og = bordaDF_og)
        elif request.form["submit"] == "Submit":
            try:
                url = request.form["system"]
                return redirect(url_for(url))
            except:
                bordaDF_og = get_borda_df()
                bordaDF_og = bordaDF_og.to_html(index=False)
                return render_template("bordacount.html", bordaDF_og = bordaDF_og)

@app.route("/rankchoice/", methods = ["GET", "POST"])
def render_rcv():
    if request.method == "GET":
        return render_template("rankchoice.html")
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/toptwo/", methods = ["GET", "POST"])
def render_toptwo():
    if request.method == "GET":
        return render_template("toptwo.html")
    else:
        url = request.form["system"]
        return redirect(url_for(url))