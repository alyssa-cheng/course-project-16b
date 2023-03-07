import sqlite3
import pandas as pd
import numpy as np
from flask import g

def get_voter_db():
    try:
        cmd = f"CREATE TABLE IF NOT EXISTS ranking_votes \
        (rank1 TEXT, rank2 TEXT, rank3 TEXT, rank4 TEXT, rank5 TEXT)"
        cursor.execute(cmd)
        return g.voter_db
    except:
        g.voter_db = sqlite3.connect('voter_data.sqlite')
        
        df = pd.read_csv("~/Documents/GitHub/course-project-16b/alaska_presidentialelection.csv")
        df = df[["rank1","rank2","rank3","rank4","rank5"]]
        df.to_sql("votes",g.voter_db,index=False,if_exists="replace")
            
        cursor = g.voter_db.cursor()
        for i in range(1,6):
            cmd = \
            f"""
            UPDATE votes 
            SET rank{i} = REPLACE(REPLACE(REPLACE(rank{i},"overvote","N/A"),"skipped","N/A"),"Undeclared","N/A")
            """
            cursor.execute(cmd)
            g.voter_db.commit()

        cmd = f"CREATE TABLE IF NOT EXISTS ranking_votes \
        (rank1 TEXT, rank2 TEXT, rank3 TEXT, rank4 TEXT, rank5 TEXT)"
        cursor.execute(cmd)

        return g.voter_db
        

results = ['Tulsi Gabbard',
 'Elizabeth Warren',
 'Pete Buttigieg',
 'Michael R. Bloomberg',
 'Tom Steyer',
 'Joseph R. Biden',
 'Bernie Sanders',
 'Amy Klobuchar']

def get_ranks(name,db_name):
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = f"""
        SELECT CASE
            WHEN '{name}' IN (rank1) THEN 1
            WHEN '{name}' IN (rank2) THEN 2
            WHEN '{name}' IN (rank3) THEN 3
            WHEN '{name}' IN (rank4) THEN 4
            WHEN '{name}' IN (rank5) THEN 5
            ELSE 6
        END FROM {db_name}
        """ #if ranked multiple times, returns highest rank
        cursor.execute(cmd)
        return np.array(list(zip(*cursor.fetchall()))[0])
    
def plurality(db_name):
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = f"""
        SELECT rank1, COUNT(rank1)
        FROM {db_name}
        GROUP BY rank1
        ORDER BY COUNT(rank1) DESC
        """
        cursor.execute(cmd)
        return cursor.fetchall()

def borda(db_name,point_dict={1:1,2:2,3:3,4:4,5:5}):
    #ask if there's a more efficient way to do this
    count = {}
    with get_voter_db() as conn:
        cursor = conn.cursor()
        for result in results:
            for col in [1,2,3,4,5]:
                cmd = f"SELECT {point_dict[col]}*COUNT(rank{col}) FROM {db_name} WHERE (rank{col}=='{result}')"
                cursor.execute(cmd)
                count[result] = count.get(result,0) + cursor.fetchone()[0]
    return sorted([(i,j) for i,j in count.items()],key = lambda x:-x[1])

def preference_profiles():
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT *,COUNT(*) FROM votes \
        GROUP BY rank1,rank2,rank3,rank4,rank5 \
        ORDER BY COUNT(*) DESC")
    return cursor.fetchall()

def IRV(db_name):
    #brute-force implementation
    #output is not necessarily a good ranking of preference, since worst candidates might
    #get no first place votes but more second-place votes
    #doesn't handle N/A votes well
    can_win = list(results)
    to_return = []
    with get_voter_db() as conn:
        count = 0
        cursor = conn.cursor()
        while len(can_win)>1:
            votes=[]
            tallies=[]
            can_win_str = tuple(can_win)
            
            cmd = f"SELECT rank1,COUNT(rank1) FROM {db_name} WHERE rank1 IN {can_win_str} GROUP BY rank1"
            cursor.execute(cmd)
            votes += [cursor.fetchall()]
            
            cmd = f"SELECT rank2,COUNT(rank2) FROM {db_name} \
            WHERE rank2 IN {can_win_str} AND rank1 NOT IN {can_win_str} GROUP BY rank2"
            cursor.execute(cmd)
            votes += [cursor.fetchall()]
            
            cmd = f"SELECT rank3,COUNT(rank3) FROM {db_name} \
            WHERE rank3 IN {can_win_str} AND rank1 NOT IN {can_win_str} AND rank2 NOT IN {can_win_str} \
            GROUP BY rank3"
            cursor.execute(cmd)
            votes += [cursor.fetchall()]
            
            cmd = f"SELECT rank4,COUNT(rank4) FROM {db_name} \
            WHERE rank4 IN {can_win_str} AND rank1 NOT IN {can_win_str} AND rank2 NOT IN {can_win_str} \
            AND rank3 NOT IN {can_win_str} \
            GROUP BY rank4"
            cursor.execute(cmd)
            votes += [cursor.fetchall()]
            
            cmd = f"SELECT rank5,COUNT(rank5) FROM {db_name} \
            WHERE rank5 IN {can_win_str} AND rank1 NOT IN {can_win_str} AND rank2 NOT IN {can_win_str} \
            AND rank3 NOT IN {can_win_str} AND rank4 NOT IN {can_win_str} \
            GROUP BY rank5"
            cursor.execute(cmd)
            votes += [cursor.fetchall()]
            
            for person in can_win:
                vote_count = sum([dict(votes[i]).get(person,0) for i in range(5)])
                tallies += [(person,vote_count)]
                
            tallies = sorted(tallies,key=lambda x:-x[1])
            last_place = tallies[-1][0]
            
            to_return = [last_place] + to_return
            can_win.remove(last_place)
            
        return can_win + to_return
    
def TopTwo(db_name):
    plural = plurality(db_name)
    top_two = [plural[0][0],plural[1][0]]
    count1 = np.sum([get_ranks(top_two[0],db_name)<get_ranks(top_two[1],db_name)])
    count2 = np.sum([get_ranks(top_two[0],db_name)>get_ranks(top_two[1],db_name)])
    results = list(zip(top_two,[count1,count2]))
    if count1 > count2:
        return results
    else:
        return results.reverse()
    
def dictatorship(db_name,index=0):
    with sqlite3.connect("voter_data.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT rank1 FROM {db_name} LIMIT 1 OFFSET {index}")
            return cursor.fetchall()[0][0]
        except:
            return -1
    
def add_vote(vote_list):
    with sqlite3.connect("voter_data.db") as conn:
        cursor = conn.cursor()
        cmd = f"INSERT INTO ranking_votes (rank1,rank2,rank3,rank4,rank5) \
        VALUES ('{vote_list[0]}','{vote_list[1]}','{vote_list[2]}','{vote_list[3]}','{vote_list[4]}')"
        cursor.execute(cmd)
    
        conn.commit()