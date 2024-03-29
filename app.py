from flask import Flask, render_template, abort, redirect, url_for, json, request, g
import voting_systems
from get_data import get_plurality_df, get_borda_df, get_irv_df, get_toptwo_df
from plot_data import plurality_plot, borda_plot, IRV_sankey

app = Flask(__name__)

@app.route("/")
def render_home():
    """
    renders the home.html template
    args:
        none
    returns:
        a generated template file
    """
    return render_template("home.html")
    
@app.route("/WhatIsRCVoting/")
def render_intro():
    """
    renders the intro.html template
    args:
        none
    returns:
        a generated template file
    """
    return render_template("intro.html")
    
@app.route("/FairnessOfRCVoting/")
def render_intro2():
    """
    renders the intro2.html template
    args:
        none
    returns:
        a generated template file
    """
    return render_template("intro2.html")

@app.route("/PlayWithVoting/", methods = ["GET", "POST"])
def render_start():
    """
    renders the start.html template
    when user selects a voting system, it renders the selected voting system's page
    args:
        none
    returns:
        a generated template file
    """
    # if the request method is "GET"
    if request.method == "GET":
        # render the start.html page
        return render_template("start.html")
    # if the request method is "POST" (drop down menu)
    else:
        # render the url for the voting system user selected
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/plurality/", methods = ["GET", "POST"])
def render_plurality():
    """
    renders the plurality.html template
    when user selects a voting system while on this page, it renders the selected voting system's page
    args:
        none
    returns:
        a generated template file
    """
    # if the request method is "GET"
    if request.method == "GET":
        # get plurality dataframe and convert it to HTML
        pluralityDF = get_plurality_df()
        pluralityHTML = pluralityDF.to_html(index = False)

        # plot for plurality data
        graphJSON = plurality_plot(pluralityDF)

        # render the plurality.html template
        return render_template("plurality.html", graphJSON = graphJSON, pluralityDF = pluralityHTML)
    # if the request method is "POST" (drop down menu)
    else:
        # render the url for the voting system user selected
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/bordacount/", methods = ["GET", "POST"])
def render_borda():
    """
    renders the bordacount.html template
    depending on which submission button user selects, the function will either render the template with or without the interactive section
    when user selects a voting system while on this page, it renders the selected voting system's page
    args:
        none
    returns:
        a generated template file
    """
    # if the request method is "GET"
    if request.method == "GET":
        # get original borda count dataframe (regular point system) and convert to HTML
        bordaDF_og = get_borda_df()
        bordaHTML_og = bordaDF_og.to_html(index = False)

        # plot for the original borda count data
        borda_plot_og = borda_plot(bordaDF_og)

        # renders bordacount.html template with only the original data
        return render_template("bordacount.html", bordaDF_og = bordaHTML_og, borda_plot_og = borda_plot_og)
    
    # if the request method is "POST"
    else:
        # if the "POST" method is from the interactive
        if request.form["submit"] == "Submit Rank Values":
            # get original borda count dataframe (regular point system) and convert to HTML
            bordaDF_og = get_borda_df()
            bordaHTML_og = bordaDF_og.to_html(index = False)

            # plot for the original borda count data
            borda_plot_og = borda_plot(bordaDF_og)
            
            # getting the rank point values that user input
            rank1 = request.form['rank1']
            rank2 = request.form['rank2']
            rank3 = request.form['rank3']
            rank4 = request.form['rank4']
            rank5 = request.form['rank5']

            # taking the rank point values and making a new point_dict variable
            # that will be used in a new get_borda_df() function
            point_dict = {1 : rank1,
                          2 : rank2,
                          3 : rank3,
                          4 : rank4,
                          5 : rank5}

            # get interactive borda count dataframe (user point system) and convert to HTML
            bordaDF_interact = get_borda_df(point_dict)
            bordaHTML_interact = bordaDF_interact.to_html(index = False)

            # plot for the interactive borda count data
            borda_plot_interact = borda_plot(bordaDF_interact)

            # converting user rank point values into integers
            # will be used to show user what ranks they chose
            rank1 = int(rank1)
            rank2 = int(rank2)
            rank3 = int(rank3)
            rank4 = int(rank4)
            rank5 = int(rank5)

            # renders bordacount.html template with both the original and interactive data
            return render_template("bordacount.html", bordaDF_interact = bordaHTML_interact, bordaDF_og = bordaHTML_og, borda_plot_interact = borda_plot_interact, borda_plot_og = borda_plot_og, Rank_1 = rank1, Rank_2 = rank2, Rank_3 = rank3, Rank_4 = rank4, Rank_5 = rank5)
        
        # if the "POST" method is from the drop down menu
        elif request.form["submit"] == "Submit":
            try:
                # render the url for the voting system user selected
                url = request.form["system"]
                return redirect(url_for(url))
            except:
                # if user selects borda count page while already on the borda count page

                # get original borda count dataframe (regular point system) and convert to HTML
                bordaDF_og = get_borda_df()
                bordaHTML_og = bordaDF_og.to_html()

                # render bordacount.html template with only the original data
                return render_template("bordacount.html", bordaDF_og = bordaHTML_og)

@app.route("/instantrunoff/", methods = ["GET", "POST"])
def render_irv():
    """
    renders the instantrunoff.html template
    when user selects a voting system while on this page, it renders the selected voting system's page
    args:
        none
    returns:
        a generated template file
    """
    # if the request method is "GET"
    if request.method == "GET":
        # get instant runoff dataframe and convert to HTML
        irvDF, rankings, label, source, target, value = get_irv_df()
        irvHTML = irvDF.to_html(index = False)
        
        # sankey diagram for irv data
        graphJSON = IRV_sankey(rankings, label, source, target, value)

        # render instantrunoff.html template 
        return render_template("instantrunoff.html", graphJSON = graphJSON, irvDF = irvHTML)
    # if the "POST" method is from the drop down menu
    else:
        # render the url for the voting system user selected
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/toptwo/", methods = ["GET", "POST"])
def render_toptwo():
    """
    renders the toptwo.html template
    when user selects a voting system while on this page, it renders the selected voting system's page
    args:
        none
    returns:
        a generated template file
    """
    # if the request method is "GET"
    if request.method == "GET":
        # get top-two runoff dataframe and convert to HTML
        toptwoDF = get_toptwo_df()
        toptwoHTML = toptwoDF.to_html(index = False)

        # render toptwo.html template
        return render_template("toptwo.html", toptwoDF = toptwoHTML)
    # if the "POST" method is from the drop down menu
    else:
        # render the url for the voting system user selected
        url = request.form["system"]
        return redirect(url_for(url))

@app.route("/dictatorship/", methods = ["GET", "POST"])
def render_dictatorship():
    """
    renders the dictatorship.html template
    when user selects a voting system while on this page, it renders the selected voting system's page
    args:
        none
    returns:
        a generated template file
    """
    # figuring out how many voters there are
    with voting_systems.get_voter_db() as conn:
        cursor = conn.cursor()
        cmd = "SELECT COUNT(*) FROM votes"
        cursor.execute(cmd)
        upperbound0 = cursor.fetchall()[0][0]
        upperbound0 -= 1
        upperbound = str(upperbound0)

    # rendering dictatorship.html with correct upper bound for voter indices
    if request.method == "GET":
        return render_template("dictatorship.html", upperbound = upperbound, chooseDict = False, resultDict = ' ')
    
    # this code if request method is POST
    else:
        # when they submit an index to be the dictator
        if request.form["submit"] == "Submit choice for dictator":
            # error checking to make sure index is in the correct range
            errorstring = f"This is not an acceptable index. Please input an integer between 0 and {upperbound}."
            indexDict = request.form["indexDict"]
            indexDict = int(indexDict)
            resultDict = voting_systems.dictatorship("votes",index=indexDict)
            if (indexDict < 0) or (indexDict > upperbound0):
                resultDict = errorstring
            else:
                resultDict = str(resultDict)
            
            # one secret exception which is secret code to clear the
            # votes from the "Vote for Your Favorite System" page
            if indexDict == 5212001:
                voting_systems.clear_rankings()
            
            # rendering the dictatorship.html to show results
            return render_template("dictatorship.html", upperbound = upperbound, chooseDict = True, resultDict = resultDict)
        # render the url for the voting system user selected
        elif request.form["submit"] == "Submit":
            url = request.form["system"]
            return redirect(url_for(url))
            
@app.route('/FavoriteSystems/', methods=['POST','GET'])
def render_choice():
    """
    renders the choice.html template
    user inputs a voting system for each drop down menu
    args:
        none
    returns:
        a generated template file
    """
    # if user submits a vote
    if request.method == 'POST':
        # store the vote in the database
        rank1 = request.form['rank1'] 
        rank2 = request.form['rank2']
        rank3 = request.form['rank3'] 
        rank4 = request.form['rank4']
        rank5 = request.form['rank5']
        vote = [rank1, rank2, rank3, rank4, rank5]
        if len(list(set(vote))) == 5: # if valid vote (all unique inputs)
            voting_systems.add_vote(vote)
            results = voting_systems.get_favorite_systems() #get results after submission
            # display the thank you message
            return render_template('choice.html', submitted=True, results=results, badsubmit=False)
        else: 
            results = voting_systems.get_favorite_systems()
            return render_template('choice.html', submitted=False, results=results, badsubmit=True)
    # otherwise display the standard page
    else:
        results = voting_systems.get_favorite_systems()
        return render_template('choice.html', submitted=False, results=results, badsubmit=False)