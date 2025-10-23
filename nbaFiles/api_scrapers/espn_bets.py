import re
import pickle
from datetime import datetime, timedelta
from time import sleep
from pprint import pprint
import logging
import requests
from bs4 import BeautifulSoup
import json

source1 = 'https://www.espn.com/nba/odds'
source2 = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'

error_codes = [500, 403, 404]

espn_api_successful = False

def get_espn_bets_gamelines():
    logger = logging.getLogger(__name__)

    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from ESPN: {e}")
        return []

    game_lines = []
    events = 0
    
    if 'events' in data:
        for event in data['events']:
            events += 1
            if 'competitions' in event:
                for competition in event['competitions']:
                    if 'odds' in competition and competition['odds']:
                        # Extract date and time
                        date_str = event.get('date', '')
                        game_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d') if date_str else ''
                        game_time = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%H:%MZ') if date_str else ''
                        
                        game_info = {
                            'game_id': competition.get('id'),
                            'name': event.get('name'),
                            'short_name': event.get('shortName'),
                            'game_day': game_date,
                            'start_time': game_time,
                            'source': 'espn_bets'
                        }
                        
                        for odds_entry in competition['odds']:
                            line = {
                                'provider': odds_entry.get('provider', {}).get('name'),
                                'over_under': odds_entry.get('overUnder'),
                                'spread': odds_entry.get('spread'),
                                'home_moneyline': odds_entry.get('homeTeamOdds', {}).get('moneyLine'),
                                'away_moneyline': odds_entry.get('awayTeamOdds', {}).get('moneyLine')
                            }
                            game_lines.append({**game_info, **line})
            else:
                return False
    else:
        logger.warning("No 'events' key found in the JSON response") 

    if len(game_lines) <= 1:
        print('No odds found for ESPN NBA API')

    espn_api_successful = True
    gl_data = restructure_gameline_data(game_lines)
    return gl_data

def get_data(source):
    raw_data = requests.get(source)
    soup = BeautifulSoup(raw_data.text, 'html.parser')

    if soup:
        print(soup)
    else:
        print('No soup!')

    print(source, 'has been printed')

def restructure_gameline_data(raw_data):
    structured_data = []

    for game in raw_data:
        # Extract the necessary team names
        names = game['short_name'].split('@')
        away_team = names[0].strip()
        home_team = names[1].strip()
        
        # Extract spread data (NBA uses spread like NFL)
        home_spread_odds = '-110'
        away_spread_odds = '-110'

        # Extract moneyline data
        home_moneyline = game.get('home_moneyline', 'N/A')
        away_moneyline = game.get('away_moneyline', 'N/A')

        # Handle spread logic for NBA
        spread = game.get('spread', 0)
        if home_moneyline != 'N/A' and away_moneyline != 'N/A':
            if home_moneyline < away_moneyline:  # Home team is favorite
                home_spread = f"-{spread}"
                away_spread = f"+{spread}"
            else:  # Away team is favorite
                home_spread = f"+{spread}"
                away_spread = f"-{spread}"
        else:
            home_spread = f"{spread}"
            away_spread = f"{spread}"

        # Extract Over/Under (total) data
        over_under = game.get('over_under', 'N/A')
        over_odds = '-110'
        under_odds = '-110'

        # Create a new dictionary for the game
        new_game_entry = {
            'home': home_team,
            'away': away_team,
            'home_ml': home_moneyline,
            'away_ml': away_moneyline,
            'home_spread': home_spread,
            'away_spread': away_spread,
            'home_spread_odds': home_spread_odds,
            'away_spread_odds': away_spread_odds,
            'total': over_under,
            'over_odds': over_odds,
            'under_odds': under_odds,
            'game_day': game.get('game_day', ''),
            'start_time': game.get('start_time', ''),
            'source': game.get('source', 'espn_bets')
        }

        structured_data.append(new_game_entry)
    
    print(f"Structured {len(structured_data)} NBA games")
    return structured_data

# Additional function to get gamelines from multiple sources
def get_nba_gamelines(source='espn_bets'):
    """
    Main function to get NBA gamelines from specified source
    """
    if source == 'espn_bets':
        return get_espn_bets_gamelines()
    else:
        # Placeholder for other sportsbook sources
        print(f"Source {source} not yet implemented for NBA")
        return []

# Function to format the final API response (matching MLB structure)
def format_nba_api_response(gamelines_data, source='espn_bets'):
    """
    Format the response to match the expected frontend structure
    """
    return {
        "gamelines": gamelines_data,
        "source": source,
        "last_updated": datetime.now().isoformat(),
        "game_count": len(gamelines_data)
    }

# Function to get all NBA gamelines in MLB-style format
def get_all_nba_gamelines():
    """
    Get NBA gamelines in the same format as MLB
    Returns: dict with gamelines array
    """
    gamelines = get_espn_bets_gamelines()
    return {
        "gamelines": gamelines,
        "last_updated": datetime.now().isoformat()
    }

nba_games = get_espn_bets_gamelines()
if nba_games:
  print(f"Successfully fetched {len(nba_games)} NBA games")
  for game in nba_games:
    print(f"{game['away']} @ {game['home']} - Spread: {game['home_spread']} | Total: {game['total']}")
else:
  print("No NBA games found")
