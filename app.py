from flask import Flask
from flask import render_template, abort, redirect, url_for
from flask import request, g
import sqlite3

app = Flask(__name__)

@app.route("/")
def render_main():
    return render_template("main.html")

@app.route("/plurality/")
def render_plurality():
    return render_template("plurality.html")

@app.route("/bordacount/")
def render_borda():
    return render_template("bordacount.html")

@app.route("/rankchoice/")
def render_rcv():
    return render_template("rankchoice.html")