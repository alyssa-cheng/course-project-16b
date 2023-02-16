import sqlite3
import pandas as pd

results = ['Tulsi Gabbard',
 'Elizabeth Warren',
 'Pete Buttigieg',
 'Michael R. Bloomberg',
 'Tom Steyer',
 'Joseph R. Biden',
 'Bernie Sanders',
 'Amy Klobuchar']

def make_table():
    with sqlite3.connect("voter_data.db") as conn:
        df = pd.read_csv("~/Documents/GitHub/course-project-16b/alaska_presidentialelection.csv")
        df = df[["rank1","rank2","rank3","rank4","rank5"]]
        df.to_sql("votes",conn,index=False,if_exists="replace")
        

def plurality():
    with sqlite3.connect("voter_data.db") as conn:
        cursor = conn.cursor()
        cmd = """
        SELECT rank1, COUNT(rank1)
        FROM votes
        GROUP BY rank1
        ORDER BY COUNT(rank1) DESC
        """
        cursor.execute(cmd)
        return cursor.fetchall()

def borda(point_dict={1:1,2:2,3:3,4:4,5:5}):
    #ask if there's a more efficient way to do this
    
    count = {}
    with sqlite3.connect("voter_data.db") as conn:
        cursor = conn.cursor()
        for result in results:
            for col in [1,2,3,4,5]:
                cmd = f"SELECT {point_dict[col]}*COUNT(rank{col}) FROM votes WHERE (rank{col}=='{result}')"
                cursor.execute(cmd)
                count[result] = count.get(result,0) + cursor.fetchone()[0]
    return [(i,j) for i,j in count.items()]

def TopTwo():
    plural = plurality()
    top_two = [plural[0][0],plural[1][0]]
    with sqlite3.connect("voter_data.db") as conn:
        cursor = conn.cursor()
        #hard-coded because I have no idea how else to do this
        cmd = f"""
        SELECT COUNT(*) FROM votes
        WHERE (rank1 == '{top_two[0]}' AND rank2 == '{top_two[1]}')
        OR (rank1 == '{top_two[0]}' AND rank3 == '{top_two[1]}')
        OR (rank1 == '{top_two[0]}' AND rank4 == '{top_two[1]}')
        OR (rank1 == '{top_two[0]}' AND rank5 == '{top_two[1]}')
        OR (rank2 == '{top_two[0]}' AND rank3 == '{top_two[1]}')
        OR (rank2 == '{top_two[0]}' AND rank4 == '{top_two[1]}')
        OR (rank2 == '{top_two[0]}' AND rank5 == '{top_two[1]}')
        OR (rank3 == '{top_two[0]}' AND rank4 == '{top_two[1]}')
        OR (rank3 == '{top_two[0]}' AND rank5 == '{top_two[1]}')
        OR (rank4 == '{top_two[0]}' AND rank5 == '{top_two[1]}')
        OR (rank5 == '{top_two[0]}' AND rank1 != '{top_two[1]}' AND rank2 != '{top_two[1]}'
        AND rank3 != '{top_two[1]}' AND rank4 != '{top_two[1]}')
        """
        cursor.execute(cmd)
        count1 = cursor.fetchone()[0]
        
        cmd = f"""
        SELECT COUNT(*) FROM votes
        WHERE (rank1 == '{top_two[1]}' AND rank2 == '{top_two[0]}')
        OR (rank1 == '{top_two[1]}' AND rank3 == '{top_two[0]}')
        OR (rank1 == '{top_two[1]}' AND rank4 == '{top_two[0]}')
        OR (rank1 == '{top_two[1]}' AND rank5 == '{top_two[0]}')
        OR (rank2 == '{top_two[1]}' AND rank3 == '{top_two[0]}')
        OR (rank2 == '{top_two[1]}' AND rank4 == '{top_two[0]}')
        OR (rank2 == '{top_two[1]}' AND rank5 == '{top_two[0]}')
        OR (rank3 == '{top_two[1]}' AND rank4 == '{top_two[0]}')
        OR (rank3 == '{top_two[1]}' AND rank5 == '{top_two[0]}')
        OR (rank4 == '{top_two[1]}' AND rank5 == '{top_two[0]}')
        OR (rank5 == '{top_two[1]}' AND rank1 != '{top_two[0]}' AND rank2 != '{top_two[0]}'
        AND rank3 != '{top_two[0]}' AND rank4 != '{top_two[0]}')
        """
        cursor.execute(cmd)
        count2 = cursor.fetchone()[0]
        
    return list(zip(top_two,[count1,count2]))