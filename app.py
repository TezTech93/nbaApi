from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
from fastapi import File, UploadFile
import json
from pydantic import BaseModel
from typing import List, Optional
import sys, os

sys.path.append(os.path.dirname(__file__) + "/nbaFiles/")
from nbaGamelines import *
from nbaGetData import get_team_stats as nba_get_team_stats  # Rename the import

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NBA team list for dropdowns
NBA_TEAMS = [
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
]

# Years for dropdown
YEARS = [str(year) for year in range(2020, 2025)]

# ---------- Pydantic models for dump route ----------
class NBAGameline(BaseModel):
    home: str
    away: str
    game_day: str
    start_time: Optional[str] = None
    home_ml: Optional[int] = None
    away_ml: Optional[int] = None
    home_spread: Optional[float] = None
    away_spread: Optional[float] = None
    home_spread_odds: Optional[int] = None
    away_spread_odds: Optional[int] = None
    over_under: Optional[float] = None
    over_odds: Optional[int] = None
    under_odds: Optional[int] = None

class GamelineDump(BaseModel):
    source: str  # e.g., "manual", "bulk_upload"
    gamelines: List[NBAGameline]

# ---------- Existing endpoints ----------
@app.get("/nba/current-season")
def get_current_season():
    return {'Current_Season': cur_season}

@app.get("/nba/gamelines")
def get_lines():
    return {"Gamelines": nba_game_lines}

@app.get("/nba/gamelines/manual", response_class=HTMLResponse)
def manual_input_form():
    """Serve HTML form for manual NBA gameline input"""
    html_content = f"""
    <html>
    <head>
        <title>NBA Manual Gameline Input</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .formGrid {{ display: flex; flex-direction: column; gap: 20px; max-width: 800px; }}
            .dateTimeRow {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .teamRow {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select {{ padding: 8px; width: 100%; box-sizing: border-box; }}
            button {{ padding: 12px 24px; background: #007bff; color: white; border: none; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0056b3; }}
            .card {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h2>NBA Manual Gameline Input</h2>
        <form action="/nba/gamelines/manual" method="post">
            <div class="form-group gameline_card">
                <label for="source">Source:</label>
                <select id="source" name="source" required>
                    <option value="manual">Manual</option>
                    <option value="draftkings">DraftKings</option>
                    <option value="espn_bets">ESPN Bets</option>
                </select>
            </div>
            <div class="form-group">
                <label for="home_team">Home Team:</label>
                <input type="text" id="home_team" name="home_team" required>
            </div>
            <div class="form-group">
                <label for="away_team">Away Team:</label>
                <input type="text" id="away_team" name="away_team" required>
            </div>
            <div class="form-group">
                <label for="game_day">Game Date:</label>
                <input type="date" id="game_day" name="game_day" required>
            </div>
            <div class="form-group">
                <label for="start_time">Start Time:</label>
                <input type="time" id="start_time" name="start_time">
            </div>
            <div class="form-group">
                <label for="home_ml">Home ML:</label>
                <input type="number" id="home_ml" name="home_ml">
            </div>
            <div class="form-group">
                <label for="away_ml">Away ML:</label>
                <input type="number" id="away_ml" name="away_ml">
            </div>
            <div class="form-group">
                <label for="home_spread">Home Spread:</label>
                <input type="number" step="0.1" id="home_spread" name="home_spread">
            </div>
            <div class="form-group">
                <label for="away_spread">Away Spread:</label>
                <input type="number" step="0.1" id="away_spread" name="away_spread">
            </div>
            <div class="form-group">
                <label for="over_under">Over/Under:</label>
                <input type="number" step="0.1" id="over_under" name="over_under">
            </div>
            <button type="submit">Submit Gameline</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/nba/gamelines/manual")
async def submit_manual_gameline(
    source: str = Form(...),
    home_team: str = Form(...),
    away_team: str = Form(...),
    game_day: str = Form(...),
    start_time: str = Form(None),
    home_ml: int = Form(None),
    away_ml: int = Form(None),
    home_spread: float = Form(None),
    away_spread: float = Form(None),
    home_spread_odds: int = Form(None),
    away_spread_odds: int = Form(None),
    over_under: float = Form(None),
    over_odds: int = Form(None),
    under_odds: int = Form(None)
):
    """Handle manual NBA gameline submission"""
    try:
        game_data = {
            'home': home_team,
            'away': away_team,
            'game_day': game_day,
            'start_time': start_time,
            'home_ml': home_ml,
            'away_ml': away_ml,
            'home_spread': home_spread,
            'away_spread': away_spread,
            'home_spread_odds': home_spread_odds,
            'away_spread_odds': away_spread_odds,
            'over_under': over_under,
            'over_odds': over_odds,
            'under_odds': under_odds,
            'source': source
        }
        
        # Append to global list (if nba_game_lines is mutable)
        nba_game_lines.append(game_data)
        
        return {
            "status": "success",
            "message": f"NBA Gameline for {away_team} @ {home_team} submitted successfully",
            "data": game_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting NBA gameline: {str(e)}")

# ---------- NEW DUMP ROUTES ----------
@app.post("/nba/gamelines/dump")
async def dump_gamelines(payload: GamelineDump):
    """
    Accept a JSON object containing multiple NBA gamelines and add them to the nba_game_lines list.
    """
    try:
        added_count = 0
        for game in payload.gamelines:
            game_dict = game.dict()
            game_dict['source'] = payload.source
            nba_game_lines.append(game_dict)
            added_count += 1
        
        return {
            "status": "success",
            "message": f"Added {added_count} gameline(s) from source '{payload.source}'",
            "total_gamelines": len(nba_game_lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dumping gamelines: {str(e)}")

@app.get("/nba/gamelines/dump")
async def get_dumped_gamelines():
    """
    Retrieve all gamelines currently in memory (including those added via dump or manual).
    """
    return {
        "total": len(nba_game_lines),
        "gamelines": nba_game_lines
    }

# ---------- Existing stats endpoints ----------
@app.get("/nba/team-select", response_class=HTMLResponse)
def team_select_form():
    """Serve HTML form for team stats with dropdowns"""
    html_content = f"""
    <html>
    <head>
        <title>NBA Team Stats</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            select, button {{ padding: 10px; font-size: 16px; }}
            button {{ background: #007bff; color: white; border: none; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h2>NBA Team Statistics</h2>
        <form action="/nba/team-stats" method="get" id="teamForm">
            <div class="form-group">
                <label for="team">Team:</label>
                <select id="team" name="team" required>
                    <option value="">Select Team</option>
                    {"".join([f'<option value="{team}">{team}</option>' for team in NBA_TEAMS])}
                </select>
            </div>
            <div class="form-group">
                <label for="year">Year:</label>
                <select id="year" name="year" required>
                    <option value="">Select Year</option>
                    {"".join([f'<option value="{year}">{year}</option>' for year in YEARS])}
                </select>
            </div>
            <button type="submit">Get Team Stats</button>
        </form>
        <div id="results"></div>
        
        <script>
            document.getElementById('teamForm').onsubmit = async function(e) {{
                e.preventDefault();
                const team = document.getElementById('team').value;
                const year = document.getElementById('year').value;
                
                if (team && year) {{
                    try {{
                        const response = await fetch(`/nba/${{team}}/${{year}}`);
                        const data = await response.json();
                        document.getElementById('results').innerHTML = 
                            '<h3>Results:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    }} catch (error) {{
                        document.getElementById('results').innerHTML = 
                            '<p style="color: red;">Error fetching data</p>';
                    }}
                }}
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/nba/team-stats")
def get_team_stats_via_form(team: str, year: str):
    """Get team stats via form parameters"""
    return get_nba_team_stats(team, year)

@app.get("/nba/{team}/{year}")
def get_nba_team_stats(team: str, year: str):
    """Original team stats endpoint"""
    try:
        print(f"Fetching stats for {team} in {year}")
        results = nba_get_team_stats(team, year)
        print(f"Results: {results}")
        
        if not results or not results.get("Data"):
            raise HTTPException(status_code=404, detail="No stats found for the given team and year")
        
        return {"Team_Stats": results["Data"]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nba/player-stats", response_class=HTMLResponse)
def player_select_form():
    """Serve HTML form for player stats (placeholder)"""
    html_content = """
    <html>
    <head>
        <title>NBA Player Stats</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, button { padding: 10px; font-size: 16px; }
            button { background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h2>NBA Player Statistics (Coming Soon)</h2>
        <p>Player stats functionality will be implemented here.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/nba/gamelines/dump/form", response_class=HTMLResponse)
async def dump_gamelines_form():
    """HTML form to input JSON gamelines for bulk upload"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NBA Bulk Gameline Dump</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: auto; }
            textarea { width: 100%; height: 300px; font-family: monospace; }
            input[type="file"] { margin: 10px 0; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
            .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>NBA Bulk Gameline Dump</h1>
            <p>Paste JSON or upload a file containing an array of gamelines.</p>
            <p>JSON format:</p>
            <pre>{
  "source": "my_upload",
  "gamelines": [
    {
      "home": "LAL",
      "away": "BOS",
      "game_day": "2025-04-06",
      "start_time": "19:30",
      "home_ml": -150,
      "away_ml": 130,
      "home_spread": -5.5,
      "away_spread": 5.5,
      "home_spread_odds": -110,
      "away_spread_odds": -110,
      "over_under": 225.5,
      "over_odds": -110,
      "under_odds": -110
    }
  ]
}</pre>
            
            <form id="dumpForm">
                <label for="source">Source name:</label>
                <input type="text" id="source" name="source" placeholder="e.g., my_bulk_upload" required><br><br>
                
                <label for="jsonInput">JSON Input (paste here):</label>
                <textarea id="jsonInput" placeholder='{"gamelines": [...]}'></textarea>
                
                <p>OR upload a JSON file:</p>
                <input type="file" id="fileInput" accept=".json"><br><br>
                
                <button type="submit">Submit Bulk Dump</button>
            </form>
            <div id="result"></div>
        </div>
        <script>
            document.getElementById('dumpForm').onsubmit = async (e) => {
                e.preventDefault();
                const source = document.getElementById('source').value;
                let jsonText = document.getElementById('jsonInput').value;
                const file = document.getElementById('fileInput').files[0];
                
                if (!source) {
                    alert("Source name is required");
                    return;
                }
                
                let payload = null;
                if (file) {
                    const fileText = await file.text();
                    try {
                        payload = JSON.parse(fileText);
                    } catch(err) {
                        document.getElementById('result').innerHTML = '<div class="status error">Invalid JSON in file</div>';
                        return;
                    }
                } else if (jsonText.trim()) {
                    try {
                        payload = JSON.parse(jsonText);
                    } catch(err) {
                        document.getElementById('result').innerHTML = '<div class="status error">Invalid JSON in textarea</div>';
                        return;
                    }
                } else {
                    document.getElementById('result').innerHTML = '<div class="status error">Please provide JSON via textarea or file</div>';
                    return;
                }
                
                // Ensure payload has a "gamelines" array
                if (!payload.gamelines || !Array.isArray(payload.gamelines)) {
                    document.getElementById('result').innerHTML = '<div class="status error">JSON must contain a "gamelines" array</div>';
                    return;
                }
                
                // Add source to payload
                payload.source = source;
                
                try {
                    const response = await fetch('/nba/gamelines/dump', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await response.json();
                    if (response.ok) {
                        document.getElementById('result').innerHTML = `<div class="status success">${result.message}<br>Total gamelines: ${result.total_gamelines}</div>`;
                        document.getElementById('jsonInput').value = '';
                        document.getElementById('fileInput').value = '';
                    } else {
                        document.getElementById('result').innerHTML = `<div class="status error">Error: ${result.detail || 'Unknown error'}</div>`;
                    }
                } catch (err) {
                    document.getElementById('result').innerHTML = `<div class="status error">Network error: ${err.message}</div>`;
                }
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/nba/gamelines/dump/file")
async def dump_gamelines_file(
    source: str = Form(...),
    file: UploadFile = File(...)
):
    """Alternative endpoint: upload a JSON file directly"""
    try:
        contents = await file.read()
        payload = json.loads(contents)
        if not isinstance(payload, dict) or "gamelines" not in payload:
            raise HTTPException(status_code=400, detail="JSON must contain 'gamelines' array")
        # Reuse the same logic
        added_count = 0
        for game in payload["gamelines"]:
            game_dict = game
            game_dict['source'] = source
            nba_game_lines.append(game_dict)
            added_count += 1
        return {
            "status": "success",
            "message": f"Added {added_count} gameline(s) from file",
            "total_gamelines": len(nba_game_lines)
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nba/{player}/")
def get_player_stats(player: str):
    """Placeholder for player stats"""
    return {"message": "Player stats endpoint - implementation pending"}

@app.get("/nba/coach-stats", response_class=HTMLResponse)
def coach_select_form():
    """Serve HTML form for coach stats (placeholder)"""
    html_content = """
    <html>
    <head>
        <title>NBA Coach Stats</title>
    </head>
    <body>
        <h2>NBA Coach Statistics (Coming Soon)</h2>
        <p>Coach stats functionality will be implemented here.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/nba/{coach}/")
def get_coach_stats(coach: str):
    """Placeholder for coach stats"""
    return {"message": "Coach stats endpoint - implementation pending"}
