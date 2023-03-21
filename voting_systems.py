import sqlite3
import pandas as pd
import numpy as np
from flask import g

def get_voter_db():
    '''
    returns database of vote data, creates database if it doesn't already exist
    '''
    try:
        return g.voter_db
    except:
        g.voter_db = sqlite3.connect('voter_data.sqlite')
        
        #create table in database for Alaska dataset
        df = pd.read_csv("https://raw.githubusercontent.com/alyssa-cheng/course-project-     16b/main/alaska_presidentialelection.csv")
        df = df[["rank1","rank2","rank3","rank4","rank5"]]
        df.to_sql("votes",g.voter_db,index=False,if_exists="replace")
        
        #clean data
        cursor = g.voter_db.cursor()
        for i in range(1,6):
            cmd = \
            f"""
            UPDATE votes 
            SET rank{i} = REPLACE(REPLACE(REPLACE(rank{i},"overvote","N/A"),"skipped","N/A"),"Undeclared","N/A")
            """
            cursor.execute(cmd)
            g.voter_db.commit()
        
        #create table for voting system vote data
        cmd = f"CREATE TABLE IF NOT EXISTS ranking_votes \
        (rank1 TEXT, rank2 TEXT, rank3 TEXT, rank4 TEXT, rank5 TEXT)"
        cursor.execute(cmd)
        g.voter_db.commit()

        return g.voter_db

def get_results(db_name):
    '''
    returns list of possible candidates corresponding to database db_name
    '''
    #hard-coded for tables used in the project
    if db_name == "votes":
        return ['Tulsi Gabbard',
                'Elizabeth Warren',
                'Pete Buttigieg',
                'Michael R. Bloomberg',
                'Tom Steyer',
                'Joseph R. Biden',
                'Bernie Sanders',
                'Amy Klobuchar']
    elif db_name == "ranking_votes":
        return ['Borda Count',
                'Top Two Runoff',
                'Dictatorship',
                'Instant Runoff',
                'Plurality']
    else:
        return -1

def get_ranks(name,db_name):
    '''
    returns Numpy array of all of a candidate's ranks in db_name
    '''
    if name not in get_results(db_name):
        return -1
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
    '''
    applies plurality voting to data in db_name and returns resulting preference with number of votes
    '''
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = f"""
        SELECT rank1, COUNT(rank1)
        FROM {db_name}
        GROUP BY rank1
        ORDER BY COUNT(rank1) DESC
        """
        cursor.execute(cmd)
        return cursor.fetchall()[:5]

def borda(db_name,point_dict={1:5,2:4,3:3,4:2,5:1}):
    '''
    applies borda count vote to data in db_name with respect to provided point values
    returns resulting preference with number of points
    '''
    count = {} #dictionary of candidates and point values
    with get_voter_db() as conn:
        cursor = conn.cursor()
        for result in get_results(db_name):
            for col in [1,2,3,4,5]: #for each candidate, counts the total number of points received from being in col
                cmd = f"SELECT {point_dict[col]}*COUNT(rank{col}) FROM {db_name} WHERE (rank{col}=='{result}')"
                cursor.execute(cmd)
                count[result] = count.get(result,0) + cursor.fetchall()[0][0]
    return sorted([(i,j) for i,j in count.items()],key = lambda x:-x[1])[:5]

def IRV(db_name):
    '''
    applies instant runoff vote to data in db_name
    returns resulting preference
    '''
    can_win = get_results(db_name) #remaining possible winning candidates
    to_return = []
    with get_voter_db() as conn:
        cursor = conn.cursor()
        while len(can_win)>1: #iterates rounds of instant runoff
            votes=[]
            tallies=[]
            can_win_str = tuple(can_win)
            
            #count number of first place votes in current iteration of instant runoff
            #only takes into account candidates in can_win when determining rank
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
            
            #consolidate votes for each candidate
            for person in can_win:
                vote_count = sum([dict(votes[i]).get(person,0) for i in range(5)])
                tallies += [(person,vote_count)]
            
            #determine last place in current round of instant runoff
            tallies = sorted(tallies,key=lambda x:-x[1])
            last_place = tallies[-1][0]
            
            #update to_return and can_win
            to_return = [last_place] + to_return
            can_win.remove(last_place)
            
        return (can_win + to_return)[:5]
    
def TopTwo(db_name):
    '''
    applies top two runoff to data in db_name
    returns resulting preference
    '''
    try:
        with get_voter_db() as conn:
            to_return = []
            remaining = list(get_results(db_name))
            cursor = conn.cursor()
            while len(remaining) > 1: #iterates rounds of runoff until full preference profile created
                cmd = f"""
                SELECT rank1
                FROM {db_name}
                WHERE rank1 IN {tuple(remaining)}
                GROUP BY rank1
                ORDER BY COUNT(rank1) DESC
                """ #run plurality on remaining candidates
                cursor.execute(cmd)
                fetch = cursor.fetchall()
                top_two = [fetch[0][0],fetch[1][0]] #extract top two
                
                #find relative ranking between current top two candidates
                count1 = np.sum([get_ranks(top_two[0],db_name)<get_ranks(top_two[1],db_name)])
                count2 = np.sum([get_ranks(top_two[0],db_name)>get_ranks(top_two[1],db_name)])
                
                #update to_return and remaining accordingly
                if count1 > count2:
                    to_return += [top_two[0]]
                    remaining.remove(top_two[0])
                else:
                    to_return += [top_two[1]]
                    remaining.remove(top_two[1])
                    
            return (to_return + remaining)[:5]
    except: #in the case that plurality() only returns one result, will return that one element
        return [plurality(db_name)[0][0]]
    
def dictatorship(db_name,index=0):
    '''
    return the rank 1 vote of the dictator given by index in db_name
    '''
    with get_voter_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {db_name} LIMIT 1 OFFSET {index}")
            results = cursor.fetchall()[0]
            results = [i for i in results if i != "N/A"]
            return results[0] #returns highest non-N/A value
        except:
            return -1
    
def add_vote(vote_list):
    '''
    adds preference profile vote_list as a row into ranking_votes
    '''
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = f"INSERT INTO ranking_votes (rank1,rank2,rank3,rank4,rank5) \
        VALUES ('{vote_list[0]}','{vote_list[1]}','{vote_list[2]}','{vote_list[3]}','{vote_list[4]}')"
        cursor.execute(cmd)
    
        conn.commit()
        
def get_favorite_systems():
    '''
    returns dictionary of current favorite voting systems based on each voting system
    '''
    try:
        return {"borda":borda("ranking_votes")[0][0],
                "dictator":dictatorship("ranking_votes"),
                "irv":IRV("ranking_votes")[0],
                "plural":plurality("ranking_votes")[0][0],
                "toptwo":TopTwo("ranking_votes")[0]}
    except: #if ranking_votes is empty
        return {"borda":"",
                "dictator":"",
                "irv":"",
                "plural":"",
                "toptwo":""}
    
def view_rankings():
    '''
    prints ranking_votes table (for debugging only)
    '''
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = "SELECT * FROM ranking_votes"
        cursor.execute(cmd)
        print(cursor.fetchall())
        
def clear_rankings():
    '''
    clears rows from ranking_votes dataset
    '''
    with get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = "DELETE FROM ranking_votes"
        cursor.execute(cmd)
        conn.commit()