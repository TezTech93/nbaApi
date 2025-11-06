from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
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
            <!-- ... your existing form HTML ... -->
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
            'under_odds': under_odds
        }
        
        return {
            "status": "success",
            "message": f"NBA Gameline for {away_team} @ {home_team} submitted successfully",
            "data": game_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting NBA gameline: {str(e)}")

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
    return get_nba_team_stats(team, year)  # Call the renamed function

@app.get("/nba/{team}/{year}")
def get_nba_team_stats(team: str, year: str):  # Renamed endpoint function
    """Original team stats endpoint"""
    try:
        print(f"Fetching stats for {team} in {year}")  # Debug print
        results = nba_get_team_stats(team, year)  # Call the imported function
        print(f"Results: {results}")  # Debug print
        
        if not results or not results.get("Data"):
            raise HTTPException(status_code=404, detail="No stats found for the given team and year")
        
        return {"Team_Stats": results["Data"]}  # Return the data directly
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in endpoint: {e}")  # Debug print
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
