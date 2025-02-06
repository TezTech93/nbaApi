from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
import sys, os
sys.path.append(os.path.dirname((__file__)) + "/nbaFiles/")
from nbaGamelines import *
from nbaGetData import *


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/nba/gamelines")
def get_lines():
    return {"Gamelines":nba_game_lines}

@app.get("/nba/{team}/{year}")
def get_stats(team,year):
    try:
        results = get_team_stats(team, year)
        if not results:
            raise HTTPException(status_code=404, detail="No stats found for the given team and year")
        return {"Team_Stats": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nba/{player}/")
def get_player_stats(range):
    return 1

@app.get("/nba/{coach}/")
def get_coach_stats(range):
    return 1