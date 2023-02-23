from flask import Flask
from flask import render_template, abort, redirect, url_for
from flask import request, g
import pandas as pd
import sqlite3
import voting_systems

app = Flask(__name__)

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
        return render_template("plurality.html")
    else:
        url = request.form["system"]
        # results = voting_systems.plurality()
        return redirect(url_for(url))

def plural_df():
    pluralityList = voting_systems.plurality()
    pluralityDF = pd.DataFrame(pluralityList, columns = ['candidate', 'number of votes'])
    # return render_template('plurality.html',  tables=[pluralityDF.to_html(classes='data')], titles=pluralityDF.columns.values)


@app.route("/bordacount/", methods = ["GET", "POST"])
def render_borda():
    if request.method == "GET":
        return render_template("bordacount.html")
    else:
        try:
            url = request.form["system"]
            results = voting_systems.borda()
            return redirect(url_for(url))
        except:
            return render_template("bordacount.html")

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