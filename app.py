from flask import Flask, render_template, abort, redirect, url_for, json, request, g
import json
import plotly
from plotly import express as px
import pandas as pd
import sqlite3
import voting_systems
from get_data import get_plurality_df, get_borda_df, get_irv_df, get_toptwo_df
from plot_data import plurality_plot, borda_plot

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template("main.html")
    
@app.route("/intro/")
def render_intro():
    return render_template("intro.html")
    
@app.route("/intro2/")
def render_intro2():
    return render_template("intro2.html")

@app.route("/start/", methods = ["GET", "POST"])
def render_start():
    if request.method == "GET":
        return render_template("start.html")
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/plurality/", methods = ["GET", "POST"])
def render_plurality():
    if request.method == "GET":
        pluralityDF = get_plurality_df()
        pluralityHTML = pluralityDF.to_html(index = False)
        graphJSON = plurality_plot(pluralityDF)
        return render_template("plurality.html", graphJSON = graphJSON, pluralityDF = pluralityHTML)
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/bordacount/", methods = ["GET", "POST"])
def render_borda():
    if request.method == "GET":
        bordaDF_og = get_borda_df()
        bordaHTML_og = bordaDF_og.to_html(index = False)
        borda_plot_og = borda_plot(bordaDF_og)
        return render_template("bordacount.html", bordaDF_og = bordaHTML_og, borda_plot_og = borda_plot_og)
    else:
        if request.form["submit"] == "Submit Rank Values":
            bordaDF_og = get_borda_df()
            bordaHTML_og = bordaDF_og.to_html(index = False)
            borda_plot_og = borda_plot(bordaDF_og)
            
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
            bordaHTML_interact = bordaDF_interact.to_html()

            borda_plot_interact = borda_plot(bordaDF_interact, point_dict)

            rank1 = int(rank1)
            rank2 = int(rank2)
            rank3 = int(rank3)
            rank4 = int(rank4)
            rank5 = int(rank5)

            return render_template("bordacount.html", bordaDF_interact = bordaHTML_interact, bordaDF_og = bordaHTML_og, borda_plot_interact = borda_plot_interact, borda_plot_og = borda_plot_og, Rank_1 = rank1, Rank_2 = rank2, Rank_3 = rank3, Rank_4 = rank4, Rank_5 = rank5)
        elif request.form["submit"] == "Submit":
            try:
                url = request.form["system"]
                return redirect(url_for(url))
            except:
                bordaDF_og = get_borda_df()
                bordaHTML_og = bordaDF_og.to_html()
                return render_template("bordacount.html", bordaDF_og = bordaHTML_og)

@app.route("/instantrunoff/", methods = ["GET", "POST"])
def render_irv():
    if request.method == "GET":
        irvDF = get_irv_df()
        irvHTML = irvDF.to_html(index = False)
        return render_template("instantrunoff.html", irvDF = irvHTML)
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/toptwo/", methods = ["GET", "POST"])
def render_toptwo():
    if request.method == "GET":
        toptwoDF = get_toptwo_df()
        toptwoHTML = toptwoDF.to_html(index = False)
        return render_template("toptwo.html", toptwoDF = toptwoHTML)
    else:
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/dictatorship/", methods = ["GET", "POST"])
def render_dictatorship():
    with voting_systems.get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = "SELECT COUNT(*) FROM votes"
        cursor.execute(cmd)
        upperbound0 = cursor.fetchall()[0][0]
        upperbound0 -= 1
        upperbound = str(upperbound0)

    if request.method == "GET":
        return render_template("dictatorship.html", upperbound = upperbound, chooseDict = False, resultDict = ' ')
    
    else:
        if request.form["submit"] == "Submit choice for dictator":
            errorstring = f"This is not an acceptable index. Please input an integer between 0 and {upperbound}."
            indexDict = request.form["indexDict"]
            indexDict = int(indexDict)
            resultDict = voting_systems.dictatorship("votes",index=indexDict)
            if (indexDict < 0) or (indexDict > upperbound0):
                resultDict = errorstring
            else:
                resultDict = str(resultDict)
            
            return render_template("dictatorship.html", upperbound = upperbound, chooseDict = True, resultDict = resultDict)
        elif request.form["submit"] == "Submit":
            url = request.form["system"]
            return redirect(url_for(url))
            
@app.route('/choice/', methods=['POST','GET'])
def render_choice():
    # if they submit a vote
    if request.method == 'POST':
        # store the vote in the database
        rank1 = request.form['rank1'] 
        rank2 = request.form['rank2']
        rank3 = request.form['rank3'] 
        rank4 = request.form['rank4']
        rank5 = request.form['rank5']
        vote = [rank1, rank2, rank3, rank4, rank5]
        voting_systems.add_vote(vote)
        results = voting_systems.get_favorite_systems() #get results after submission
        # display the thank you message
        return render_template('choice.html', submitted=True, results=results)
    # otherwise display the standard page
    else:
        results = voting_systems.get_favorite_systems()
        return render_template('choice.html', submitted=False, results=results)