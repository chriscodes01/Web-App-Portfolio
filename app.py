import os, random
import sys

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, success, login_required

# Configure application
app = Flask(__name__)
Bootstrap(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///valorant.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of team"""
    user_id = session["user_id"]
    value = []

    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)
    team = db.execute("SELECT teamName, value, coach_id, player1_id, player2_id, player3_id, player4_id, player5_id, playerBench_id, freePlayer_id, freeCoach_id FROM team WHERE id = ?", user_id)

    for keys in team:
            dictTeam = keys
            for key in dictTeam:
                value.append(dictTeam.get(key))

    for keys in username:
        dictUsername = keys

    coach = db.execute("SELECT name, value, agent, region, role FROM coaches WHERE id = ? ", value[2])
    player1 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[3])
    player2 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[4])
    player3 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[5])
    player4 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[6])
    player5 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[7])
    playerBench = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[8])
    freePlayer = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[9])
    freeCoach = db.execute("SELECT name, value, agent, region, role FROM coaches WHERE id = ? ", value[10])

    if coach:
        for keys in coach:
            dictCoach = keys
    else:
        dictCoach = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if player1:
        for keys in player1:
            dictPlayer1 = keys
    else:
        dictPlayer1 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if player2:
        for keys in player2:
            dictPlayer2 = keys
    else:
        dictPlayer2 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if player3:
        for keys in player3:
            dictPlayer3 = keys
    else:
        dictPlayer3 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if player4:
        for keys in player4:
            dictPlayer4 = keys
    else:
        dictPlayer4 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if player5:
        for keys in player5:
            dictPlayer5 = keys
    else:
        dictPlayer5 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if playerBench:
        for keys in playerBench:
            dictPlayerBench = keys
    else:
        dictPlayerBench = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

    if freePlayer:
        for keys in freePlayer:
            dictFreePlayer = keys
    else:
        dictFreePlayer = {'name': '', 'value': "", 'agent': '', 'region': '', 'role': ''}

    if freeCoach:
        for keys in freeCoach:
            dictFreeCoach = keys
    else:
        dictFreeCoach = {'name': '', 'value': "", 'agent': '', 'region': '', 'role': ''}

    if coach and player1 and player2 and player3 and player4 and player5:
        totalValue = dictCoach["value"] * (dictPlayer1["value"] + dictPlayer2["value"] + dictPlayer3["value"] + dictPlayer4["value"] + dictPlayer5["value"])
        totalValue = int(totalValue)
        db.execute("UPDATE team SET value = ? WHERE id = ?", totalValue, user_id)
        db.execute("UPDATE team SET valid = 1 WHERE id = ?", user_id)
    else:
        totalValue = "Recruit more agents to reveal!"
        db.execute("UPDATE team SET valid = 0 WHERE id = ?", user_id)

    return render_template("index.html", username=dictUsername, team=dictTeam, totalValue=totalValue,
        coach=dictCoach, player1=dictPlayer1, player2=dictPlayer2,
        player3=dictPlayer3, player4=dictPlayer4, player5=dictPlayer5,
        playerBench=dictPlayerBench, freePlayer=dictFreePlayer, freeCoach=dictFreeCoach)

@app.route("/recruit", methods=["GET", "POST"])
@login_required
def recruit():
    """Purchase Loot Box"""
    user_id = session["user_id"]

    if request.method == "POST":
        credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]

        if credits < 100:
            feedback = "You are too poor! Earn more credits by playing matches."
            return render_template("recruit.html", feedback=feedback)

        numberType = random.randint(0, 5)
        numberRarity = random.randint(1, 100)

        if numberType == 0:
            agentType = "coaches"
        elif numberType >= 1:
            agentType = "players"

        if numberRarity <= 1:
            rarity = 1
            rarityText = "A Tier"
        elif numberRarity > 1 and numberRarity <= 10:
            rarity = 2
            rarityText = "B Tier"
        elif numberRarity > 10 and numberRarity <= 40:
            rarity = 3
            rarityText = "C Tier"
        elif numberRarity > 40 and numberRarity <= 100:
            rarity = 4
            rarityText = "Casual"

        agentID = db.execute("SELECT id FROM ? WHERE rarity = ? ORDER BY RANDOM() LIMIT 1", agentType, rarity)[0]["id"]
        agentName = db.execute("SELECT name FROM ? WHERE id = ?", agentType, agentID)[0]["name"]
        agentRole = db.execute("SELECT role FROM ? WHERE id = ?", agentType, agentID)[0]["role"]
        agentAgent = db.execute("SELECT agent FROM ? WHERE id = ?", agentType, agentID)[0]["agent"]
        teamName = db.execute("SELECT teamName FROM team WHERE id = ?", user_id)[0]["teamName"]

        db.execute("UPDATE users SET credits = ? WHERE id = ?", credits - 100, user_id)
        credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]

        if agentType == "coaches":
            myCoachID = db.execute("SELECT coach_id FROM team WHERE id = ?", user_id)[0]["coach_id"]
            agentType = "Coach"

            if myCoachID:
                if agentID == myCoachID:
                    db.execute("UPDATE users SET credits = ? WHERE id = ?", credits + 50, user_id)
                    credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]
                    return render_template("recruit_failure.html", agentType=agentType, agentName=agentName, credits=credits)
                else:
                    db.execute("UPDATE team SET freeCoach_id = ? WHERE id = ?", agentID, user_id)
                    return redirect("/drop")
            else:
                agentType = "Coach"
                db.execute("UPDATE team SET coach_id = ? WHERE id = ?", agentID, user_id)
                return render_template("recruit_success.html", agentType=agentType, agentName=agentName, agentRole=agentRole, agentAgent=agentAgent, credits=credits, rarity=rarityText)

        elif agentType == "players":
            myPlayerIDs = db.execute("SELECT player1_id, player2_id, player3_id, player4_id, player5_id, playerBench_id, freePlayer_id FROM team WHERE id = ?", user_id)

            for keys in myPlayerIDs:
                dictMyPlayerIDs = keys

            owned = []

            for key in dictMyPlayerIDs:
                value = dictMyPlayerIDs.get(key)
                # if key has value:
                if value:
                    owned.append(value)

                    # if already have agent, return 50 credits
            for key in dictMyPlayerIDs:
                value = dictMyPlayerIDs.get(key)
                # if key has value:
                if value:
                    pass
                else:
                    agentType = "Player"
                    if agentID in owned:
                        db.execute("UPDATE users SET credits = ? WHERE id = ?", credits + 50, user_id)
                        credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]
                        return render_template("recruit_failure.html", agentType=agentType, agentName=agentName, credits=credits)
                    else:
                        db.execute("UPDATE team SET ? = ? WHERE id = ?", key, agentID, user_id)
                        return render_template("recruit_success.html", agentType=agentType, agentName=agentName, agentRole=agentRole, agentAgent=agentAgent, credits=credits, rarity=rarityText)

        # render if all player slots filled
        db.execute("UPDATE team SET freePlayer_id = ? WHERE id = ?", agentID, user_id)
        return redirect("/drop")

    elif (request.method == "GET"):
        credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]
        return render_template("recruit.html", credits=credits)

@app.route("/recruit_failure", methods=["GET"])
@login_required
def recruit_failure():
    """Feedback: Recruit Failure"""
    return render_template("recruit_failure.html")

@app.route("/recruit_success", methods=["GET"])
@login_required
def recruit_success():
    """Feedback: Recruit Success"""
    user_id = session["user_id"]
    credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]

    if credits < 100:
        feedback = "You are too poor! Earn more credits by playing matches."
        return render_template("recruit.html", feedback=feedback)

    numberType = random.randint(0, 5)
    numberRarity = random.randint(1, 100)

    if numberType == 0:
        agentType = "coaches"
    elif numberType >= 1:
        agentType = "players"

    if numberRarity <= 1:
        rarity = 1
        rarityText = "A Tier"
    elif numberRarity > 1 and numberRarity <= 10:
        rarity = 2
        rarityText = "B Tier"
    elif numberRarity > 10 and numberRarity <= 40:
        rarity = 3
        rarityText = "C Tier"
    elif numberRarity > 40 and numberRarity <= 100:
        rarity = 4
        rarityText = "Casual"

    agentID = db.execute("SELECT id FROM ? WHERE rarity = ? ORDER BY RANDOM() LIMIT 1", agentType, rarity)[0]["id"]
    agentName = db.execute("SELECT name FROM ? WHERE id = ?", agentType, agentID)[0]["name"]
    agentRole = db.execute("SELECT role FROM ? WHERE id = ?", agentType, agentID)[0]["role"]
    agentAgent = db.execute("SELECT agent FROM ? WHERE id = ?", agentType, agentID)[0]["agent"]
    teamName = db.execute("SELECT teamName FROM team WHERE id = ?", user_id)[0]["teamName"]

    db.execute("UPDATE users SET credits = ? WHERE id = ?", credits - 100, user_id)
    credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]

    if agentType == "coaches":
        myCoachID = db.execute("SELECT coach_id FROM team WHERE id = ?", user_id)[0]["coach_id"]
        agentType = "Coach"

        if myCoachID:
            if agentID == myCoachID:
                db.execute("UPDATE users SET credits = ? WHERE id = ?", credits + 50, user_id)
                credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]
                return render_template("recruit_failure.html", agentType=agentType, agentName=agentName, credits=credits)
            else:
                db.execute("UPDATE team SET freeCoach_id = ? WHERE id = ?", agentID, user_id)
                return redirect("/drop")
        else:
            agentType = "Coach"
            db.execute("UPDATE team SET coach_id = ? WHERE id = ?", agentID, user_id)
            return render_template("recruit_success.html", agentType=agentType, agentName=agentName, agentRole=agentRole, agentAgent=agentAgent, credits=credits, rarity=rarityText)

    elif agentType == "players":
        myPlayerIDs = db.execute("SELECT player1_id, player2_id, player3_id, player4_id, player5_id, playerBench_id, freePlayer_id FROM team WHERE id = ?", user_id)

        for keys in myPlayerIDs:
            dictMyPlayerIDs = keys

        owned = []

        for key in dictMyPlayerIDs:
            value = dictMyPlayerIDs.get(key)
            # if key has value:
            if value:
                owned.append(value)

                # if already have agent, return 50 credits
        for key in dictMyPlayerIDs:
            value = dictMyPlayerIDs.get(key)
            # if key has value:
            if value:
                pass
            else:
                agentType = "Player"
                if agentID in owned:
                    db.execute("UPDATE users SET credits = ? WHERE id = ?", credits + 50, user_id)
                    credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]
                    return render_template("recruit_failure.html", agentType=agentType, agentName=agentName, credits=credits)
                else:
                    db.execute("UPDATE team SET ? = ? WHERE id = ?", key, agentID, user_id)
                    return render_template("recruit_success.html", agentType=agentType, agentName=agentName, agentRole=agentRole, agentAgent=agentAgent, credits=credits, rarity=rarityText)

    # render if all player slots filled
    db.execute("UPDATE team SET freePlayer_id = ? WHERE id = ?", agentID, user_id)
    return redirect("/drop")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            invalid_feedback = "Incorrect username and/or password."
            return render_template("login.html", invalid_feedback=invalid_feedback)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("login.html")

@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    """Calculate power rating"""
    if request.method == "POST":
        agentName = request.form.get("agentName")
        matches = request.form.get("matches")
        winrate = request.form.get("winrate")
        acs = request.form.get("acs")
        kast = request.form.get("kast")
        multiplier = request.form.get("multiplier")

        matches = int(matches)
        winrate = float(winrate)
        acs = float(acs)
        kast = float(kast)
        multiplier = float(multiplier)

        power = ((matches * winrate) + (acs * kast)) * multiplier
        power = round(power, 2)

        return render_template("calculated.html", agentName=agentName, power=power)

    elif request.method == "GET":
        return render_template("calculate.html")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    """Submit new coach or player"""
    if request.method == "POST":
        agentType = request.form.get("agentType")
        agentRegion = request.form.get("agentRegion")
        agentName = request.form.get("agentName")
        agentValue = request.form.get("agentValue")
        agentAgent = request.form.get("agentAgent")
        agentRole = request.form.get("agentRole")
        agentRarity = request.form.get("agentRarity")

        ascent = request.form.get("ascentW%")
        bind = request.form.get("bindW%")
        breeze = request.form.get("breezeW%")
        fracture = request.form.get("fractureW%")
        haven = request.form.get("havenW%")
        icebox = request.form.get("iceboxW%")
        pearl = request.form.get("pearlW%")
        split = request.form.get("splitW%")

        if agentType == "Coach":
            db.execute("INSERT INTO coaches (name, value, region, rarity) VALUES (?, ?, ?, ?)",
                        agentName, agentValue, agentRegion, agentRarity)
        elif agentType == "Player":
            db.execute("INSERT INTO players (name, value, agent, region, role, rarity) VALUES (?, ?, ?, ?, ?, ?)",
                        agentName, agentValue, agentAgent, agentRegion, agentRole, agentRarity)
            player_id = db.execute("SELECT id FROM players WHERE name = ?", agentName)[0]["id"]
            db.execute("INSERT INTO mapStats (player_id, ascent, bind, breeze, fracture, haven, icebox, pearl, split) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", player_id, ascent, bind, breeze, fracture, haven, icebox, pearl, split)

        feedback = "Submission successful!"
        return render_template("submit.html", feedback=feedback)

    else:
        return render_template("submit.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        region = request.form.get("region")
        teamName = request.form.get("teamName")
        teamShort = request.form.get("teamShort")

        hash = generate_password_hash(password)

        # NEW: Select from DB the inputted username. If new variable == username, then change innerHTML.
        # Else, INSERT and redirect.
        checkUsername = db.execute("SELECT username FROM users WHERE username LIKE ?", username)
        checkTeamName = db.execute("SELECT teamName FROM users WHERE teamName LIKE ?", teamName)
        checkTeamShort = db.execute("SELECT teamShort FROM users WHERE teamName LIKE ?", teamShort)

        # Validate
        if checkUsername:
            invalid_feedback = "Username already exists."
            return render_template("register.html", invalid_feedback=invalid_feedback)
        if checkTeamName:
            invalid_feedback = "Team Name already exists."
            return render_template("register.html", invalid_feedback_2=invalid_feedback)
        if checkTeamShort:
            invalid_feedback = "Team Abbreviation already exists."
            return render_template("register.html", invalid_feedback_3=invalid_feedback)

        # Create new account
        db.execute("INSERT INTO users (username, hash, Name, credits, region, teamName, teamShort) VALUES (?, ?, ?, ?, ?, ?, ?)", username, hash, name, 2000, region, teamName, teamShort)

        # Create empty team
        db.execute("INSERT INTO team (teamName) VALUES (?)", teamName)
        db.execute("UPDATE team SET coach_id = 16 WHERE teamName = ?", teamName)
        feedback = "Registration successful!"
        return render_template("/login.html", feedback=feedback)

    elif request.method == "GET":
        return render_template("register.html")



@app.route("/drop", methods=["GET", "POST"])
@login_required
def drop():
    """Drop member of team"""
    user_id = session["user_id"]
    if request.method == "POST":
        dropAgent = request.form.get("drop")
        db.execute("UPDATE team SET ? = null WHERE id = ?", dropAgent, user_id)

        if dropAgent == "coach_id":
            newCoach = db.execute("SELECT freeCoach_id FROM team WHERE id = ?", user_id)[0]["freeCoach_id"]
            db.execute("UPDATE team SET coach_id = ? WHERE id = ?", newCoach, user_id)
            db.execute("UPDATE team SET freeCoach_id = null WHERE id = ?", user_id)
        elif dropAgent == "player1_id" or "player2_id" or "player3_id" or "player4_id" or "player5_id" or "playerBench_id":
            newPlayer = db.execute("SELECT freePlayer_id FROM team WHERE id = ?", user_id)[0]["freePlayer_id"]
            db.execute("UPDATE team SET ? = ? WHERE id = ?", dropAgent, newPlayer, user_id)
            db.execute("UPDATE team SET freePlayer_id = null WHERE id = ?", user_id)

        return render_template("drop_success.html")

    elif request.method == "GET":
        value = []

        team = db.execute("SELECT teamName, value, coach_id, player1_id, player2_id, player3_id, player4_id, player5_id, playerBench_id, freePlayer_id, freeCoach_id FROM team WHERE id = ?", user_id)

        for keys in team:
                dictTeam = keys
                for key in dictTeam:
                    value.append(dictTeam.get(key))

        coach = db.execute("SELECT name, value, agent, region, role FROM coaches WHERE id = ? ", value[2])
        player1 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[3])
        player2 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[4])
        player3 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[5])
        player4 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[6])
        player5 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[7])
        playerBench = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[8])
        freePlayer = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", value[9])
        freeCoach = db.execute("SELECT name, value, agent, region, role FROM coaches WHERE id = ? ", value[10])

        if coach:
            for keys in coach:
                dictCoach = keys
        else:
            dictCoach = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if player1:
            for keys in player1:
                dictPlayer1 = keys
        else:
            dictPlayer1 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if player2:
            for keys in player2:
                dictPlayer2 = keys
        else:
            dictPlayer2 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if player3:
            for keys in player3:
                dictPlayer3 = keys
        else:
            dictPlayer3 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if player4:
            for keys in player4:
                dictPlayer4 = keys
        else:
            dictPlayer4 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if player5:
            for keys in player5:
                dictPlayer5 = keys
        else:
            dictPlayer5 = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if playerBench:
            for keys in playerBench:
                dictPlayerBench = keys
        else:
            dictPlayerBench = {'name': 'Open slot', 'value': 0, 'agent': '', 'region': '', 'role': ''}

        if freePlayer:
            for keys in freePlayer:
                dictFreePlayer = keys
        else:
            dictFreePlayer = {'name': '', 'value': "", 'agent': '', 'region': '', 'role': ''}

        if freeCoach:
            for keys in freeCoach:
                dictFreeCoach = keys
        else:
            dictFreeCoach = {'name': '', 'value': "", 'agent': '', 'region': '', 'role': ''}

        if coach and player1 and player2 and player3 and player4 and player5:
            totalValue = dictCoach["value"] * (dictPlayer1["value"] + dictPlayer2["value"] + dictPlayer3["value"] + dictPlayer4["value"] + dictPlayer5["value"])
            totalValue = int(totalValue)
            db.execute("UPDATE team SET value = ? WHERE id = ?", totalValue, user_id)
            db.execute("UPDATE team SET valid = 1 WHERE id = ?", user_id)
        else:
            db.execute("UPDATE team SET valid = 0 WHERE id = ?", user_id)

        return render_template("drop.html", team=team, coach=dictCoach,
            player1=dictPlayer1, player2=dictPlayer2, player3=dictPlayer3,
            player4=dictPlayer4, player5=dictPlayer5, playerBench=dictPlayerBench,
            freePlayer=dictFreePlayer, freeCoach=dictFreeCoach)

@app.route("/competitive", methods=["GET", "POST"])
@login_required
def competitive():
    # Preload data
    user_id = session["user_id"]


    if request.method == "GET":
        team = db.execute("SELECT teamName, value, coach_id, player1_id, player2_id, player3_id, player4_id, player5_id, wins, losses FROM team WHERE id = ?", user_id)
        agentIDs = []

        for keys in team:
                dictTeam = keys
                if not dictTeam["coach_id"] or not dictTeam["player1_id"] or not dictTeam["player2_id"] or not dictTeam["player3_id"] or not dictTeam["player4_id"] or not dictTeam["player5_id"]:
                    return apology("Please fill out your team.")
                for key in dictTeam:
                    agentIDs.append(dictTeam.get(key))

        totalValue = dictTeam["value"]
        wins = dictTeam["wins"]
        losses = dictTeam["losses"]

        VSteam = db.execute("SELECT teamName, value, coach_id, player1_id, player2_id, player3_id, player4_id, player5_id, wins, losses FROM team WHERE valid = 1 AND id != ? ORDER BY RANDOM() LIMIT 1", user_id)

        if not VSteam:
            return apology("No valid teams to compete against.")

        VSagentIDs = []

        for keys in VSteam:
                dictVSteam = keys
                for key in dictVSteam:
                    VSagentIDs.append(dictVSteam.get(key))

        VS_id = db.execute("SELECT id FROM users WHERE teamName = ?", dictVSteam["teamName"])[0]["id"]
        VSusername = db.execute("SELECT username FROM users WHERE id = ?", VS_id)[0]["username"]
        session["VS_id"] = VS_id

        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

        VStotalValue = dictVSteam["value"]
        VSwins = dictVSteam["wins"]
        VSlosses = dictVSteam["losses"]

        teamName = dictTeam["teamName"]

        coach = db.execute("SELECT name, value, agent, region, role FROM coaches WHERE id = ? ", agentIDs[2])
        player1 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", agentIDs[3])
        player2 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", agentIDs[4])
        player3 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", agentIDs[5])
        player4 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", agentIDs[6])
        player5 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", agentIDs[7])

        for keys in coach:
            dictCoach = keys
        for keys in player1:
            dictPlayer1 = keys
        for keys in player2:
            dictPlayer2 = keys
        for keys in player3:
            dictPlayer3 = keys
        for keys in player4:
            dictPlayer4 = keys
        for keys in player5:
            dictPlayer5 = keys

        totalValue = dictCoach["value"] * (dictPlayer1["value"] + dictPlayer2["value"] + dictPlayer3["value"] + dictPlayer4["value"] + dictPlayer5["value"])
        totalValue = int(totalValue)
        db.execute("UPDATE team SET value = ? WHERE id = ?", totalValue, user_id)

        VSteamName = dictVSteam["teamName"]

        VScoach = db.execute("SELECT name, value, agent, region, role FROM coaches WHERE id = ? ", VSagentIDs[2])
        VSplayer1 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", VSagentIDs[3])
        VSplayer2 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", VSagentIDs[4])
        VSplayer3 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", VSagentIDs[5])
        VSplayer4 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", VSagentIDs[6])
        VSplayer5 = db.execute("SELECT name, value, agent, region, role FROM players WHERE id = ?", VSagentIDs[7])

        for keys in VScoach:
            dictVScoach = keys
        for keys in VSplayer1:
            dictVSplayer1 = keys
        for keys in VSplayer2:
            dictVSplayer2 = keys
        for keys in VSplayer3:
            dictVSplayer3 = keys
        for keys in VSplayer4:
            dictVSplayer4 = keys
        for keys in VSplayer5:
            dictVSplayer5 = keys

        map = db.execute("SELECT map FROM maps ORDER BY RANDOM() LIMIT 1")[0]["map"]

        return render_template("competitive.html", map=map, username=username, VSusername=VSusername, teamName=teamName, totalValue=totalValue,
            coach=dictCoach, player1=dictPlayer1, player2=dictPlayer2,
            player3=dictPlayer3, player4=dictPlayer4, player5=dictPlayer5, wins=wins, losses=losses,
            VSteamName=VSteamName, VStotalValue=VStotalValue,
            VScoach=dictVScoach, VSplayer1=dictVSplayer1, VSplayer2=dictVSplayer2,
            VSplayer3=dictVSplayer3, VSplayer4=dictVSplayer4, VSplayer5=dictVSplayer5, VSwins=VSwins, VSlosses=VSlosses)

    elif request.method == "POST":
        VS_id = session["VS_id"]
        credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)[0]["credits"]
        totalValue = db.execute("SELECT value FROM team WHERE id = ?", user_id)[0]["value"]
        VStotalValue = db.execute("SELECT value FROM team WHERE id = ?", VS_id)[0]["value"]

        # Victory
        if totalValue > VStotalValue:
            wins = db.execute("SELECT wins FROM team WHERE id = ?", user_id)[0]["wins"]
            VSlosses = db.execute("SELECT losses FROM team WHERE id = ?", VS_id)[0]["losses"]

            db.execute("UPDATE users SET credits = ? WHERE id = ?", credits + 250, user_id)
            db.execute("UPDATE team SET wins = ? WHERE id = ?", wins + 1, user_id)
            db.execute("UPDATE team SET losses = ? WHERE id = ?", VSlosses + 1, VS_id)

            return success("Victory!")

        # Draw
        elif totalValue == VStotalValue:
            return apology("Draw")

        # Loss
        elif totalValue < VStotalValue:
            losses = db.execute("SELECT losses FROM team WHERE id = ?", user_id)[0]["losses"]
            VSwins = db.execute("SELECT wins FROM team WHERE id = ?", VS_id)[0]["wins"]

            db.execute("UPDATE team SET losses = ? WHERE id = ?", losses + 1, user_id)
            db.execute("UPDATE team SET wins = ? WHERE id = ?", VSwins + 1, VS_id)

            return apology("Loss")
