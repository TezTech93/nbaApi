from fastapi import FastAPI
import sys, os
sys.path.append(os.path.dirname((__file__)) + "/nbaFiles/")
from nbaGamelines import *
from nbaGetData import *


app = FastAPI()

@app.get("/nba/gamelines")
def get_lines():
    return {"Data":nba_game_lines}

@app.get("/nba/{team}/{year}")
def get_team_stats(team,year):
    results = []
    #return a list of game data for specified year

@app.get("/nba/{player}/")
def get_player_stats(range):
    return 1

@app.get("/nba/{coach}/")
def get_coach_stats(range):
    return 1