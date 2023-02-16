import sqlite3
import pandas as pd

def make_table():
    with sqlite3.connect("voter_data.db") as conn:
        cursor = conn.cursor()
        

def plurality():
    pass

def borda():
    pass

def IRV():
    pass