import re
import json
import requests
import pickle
import sys
import os
from datetime import timedelta
import datetime as dt
from time import sleep
from pprint import pprint
import logging
import sqlite3
from enum import Enum

now = dt.datetime.now()
today = now.date()

# Add paths
sys.path.append(os.path.dirname(__file__) + "/api_scrapers/")
sys.path.append(os.path.dirname(__file__) + "/web_scrapers/")

# Import scrapers
try:
    from api_scrapers.espn_bets import get_espn_bets_gamelines
except ImportError:
    get_espn_bets_gamelines = None

try:
    from web_scrapers.draftkings_web import get_draftkings_nba_gamelines
except ImportError:
    get_draftkings_nba_gamelines = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
CACHE_FILE = 'nba_gamelines_cache.pkl'
CACHE_EXPIRY_MINUTES = 2
REQUEST_DELAY = 1
DB_FILE = 'nba_gamelines.db'

# Sportsbook configurations with priority order
SPORTSBOOKS = {
    'draftkings': {
        'name': 'DraftKings',
        'type': 'web',  # web or api
        'function': get_draftkings_nba_gamelines,
        'enabled': True,
        'priority': 1
    },
    'espn_bets': {
        'name': 'ESPN Bets', 
        'type': 'api',
        'function': get_espn_bets_gamelines,
        'enabled': True,
        'priority': 2
    }
}

class NBASeasonType(Enum):
    OFF_SEASON = "off_season"
    PRESEASON = "preseason"
    REG_SEASON = "reg_season"
    PLAYOFFS = "playoffs"

# NBA Current Season 2025-2026
NBA_CURRENT_SEASON = {
    "season_start": dt.date(2025, 10, 21),
    "season_end": dt.date(2026, 6, 18),
    "preseason_start": dt.date(2025, 9, 30),
    "preseason_end": dt.date(2025, 10, 20),
    "reg_season_start": dt.date(2025, 10, 21),
    "reg_season_end": dt.date(2026, 4, 15),
    "playoffs_start": dt.date(2026, 4, 16),
    "playoffs_end": dt.date(2026, 6, 18),
    "off_season_start": dt.date(2026, 6, 19),
    "off_season_end": dt.date(2025, 9, 29)
}

# NBA Season type date ranges
NBA_SEASON_RANGES = {
    NBASeasonType.OFF_SEASON: {
        "start": NBA_CURRENT_SEASON["off_season_start"],
        "end": NBA_CURRENT_SEASON["off_season_end"]
    },
    NBASeasonType.PRESEASON: {
        "start": NBA_CURRENT_SEASON["preseason_start"],
        "end": NBA_CURRENT_SEASON["preseason_end"]
    },
    NBASeasonType.REG_SEASON: {
        "start": NBA_CURRENT_SEASON["reg_season_start"],
        "end": NBA_CURRENT_SEASON["reg_season_end"]
    },
    NBASeasonType.PLAYOFFS: {
        "start": NBA_CURRENT_SEASON["playoffs_start"],
        "end": NBA_CURRENT_SEASON["playoffs_end"]
    }
}

def get_nba_season_type(target_date: dt.date = None) -> NBASeasonType:
    if target_date is None:
        target_date = dt.date.today()
    
    for season_type, date_range in NBA_SEASON_RANGES.items():
        if date_range["start"] <= target_date <= date_range["end"]:
            return season_type
    
    # Handle off-season wrap-around
    off_season_range = NBA_SEASON_RANGES[NBASeasonType.OFF_SEASON]
    if (target_date >= off_season_range["start"] or 
        target_date <= off_season_range["end"]):
        return NBASeasonType.OFF_SEASON
    
    return NBASeasonType.OFF_SEASON

cur_season = get_nba_season_type()

class GamelineManager:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gamelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                game_day DATE NOT NULL,
                start_time TEXT,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_ml INTEGER,
                away_ml INTEGER,
                home_spread REAL,
                away_spread REAL,
                home_spread_odds INTEGER,
                away_spread_odds INTEGER,
                over_under REAL,
                over_odds INTEGER,
                under_odds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source, game_day, home_team, away_team)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("NBA database initialized")
    
    def update_gameline(self, source, game_data):
        """Update or insert gameline into database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO gamelines 
                (source, game_day, start_time, home_team, away_team, home_ml, away_ml, 
                 home_spread, away_spread, home_spread_odds, away_spread_odds, 
                 over_under, over_odds, under_odds, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                source,
                game_data.get('game_day', now),
                game_data.get('start_time'),
                game_data['home'],
                game_data['away'],
                game_data.get('home_ml'),
                game_data.get('away_ml'),
                game_data.get('home_spread'),
                game_data.get('away_spread'),
                game_data.get('home_spread_odds'),
                game_data.get('away_spread_odds'),
                game_data.get('over_under'),
                game_data.get('over_odds'),
                game_data.get('under_odds')
            ))
            
            conn.commit()
            logger.info(f"Updated NBA gameline for {game_data['home']} vs {game_data['away']} from {source}")
            
        except Exception as e:
            logger.error(f"Error updating NBA gameline: {e}")
        finally:
            conn.close()
    
    def read_gamelines(self, source=None):
        """Read gamelines from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            if source:
                cursor.execute('SELECT * FROM gamelines WHERE source = ? ORDER BY game_day, start_time', (source,))
            else:
                cursor.execute('SELECT * FROM gamelines ORDER BY game_day, start_time')
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
            
        except Exception as e:
            logger.error(f"Error reading NBA gamelines: {e}")
            return []
        finally:
            conn.close()

    def delete_gamelines(self, source=None):
        """Delete gamelines that have already started or are from past dates"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        print('Deleting old NBA gamelines...')
        
        try:
            # Build the base query to select potential rows to delete
            query = 'SELECT id, game_day, start_time, home_team, away_team FROM gamelines'
            params = []
            if source:
                query += ' WHERE source = ?'
                params.append(source)
            query += ' ORDER BY game_day, start_time'
            
            cursor.execute(query, params)
            rows_to_check = cursor.fetchall()
            
            deleted_count = 0
            for row in rows_to_check:
                row_id, game_day_str, start_time, home_team, away_team = row
                
                # Convert game_day string to date object
                try:
                    game_day = dt.datetime.strptime(game_day_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Could not parse game_day: {game_day_str}")
                    continue
                
                # Convert start_time string to time object if it exists
                game_time = None
                if start_time:
                    try:
                        # Handle various time formats
                        if ':' in start_time and 'Z' in start_time:
                            # Handle format like "00:15Z"
                            time_part = start_time.replace('Z', '')
                            game_time = dt.datetime.strptime(time_part, '%H:%M').time()
                        else:
                            game_time = dt.datetime.strptime(start_time, '%H:%M:%S').time()
                    except ValueError:
                        try:
                            game_time = dt.datetime.strptime(start_time, '%H:%M').time()
                        except ValueError:
                            logger.warning(f"Could not parse start_time: {start_time}")
                            continue
                
                # Check if the game is from a past date
                if today > game_day:
                    cursor.execute('DELETE FROM gamelines WHERE id = ?', (row_id,))
                    deleted_count += 1
                    logger.debug(f"Deleted past NBA game: {home_team} vs {away_team} from {game_day}")
                # Check if the game is from today but the start time has passed
                elif today == game_day and game_time:
                    # Create datetime object for game start
                    game_datetime = dt.datetime.combine(game_day, game_time)
                    if now > game_datetime:
                        cursor.execute('DELETE FROM gamelines WHERE id = ?', (row_id,))
                        deleted_count += 1
                        logger.debug(f"Deleted completed NBA game: {home_team} vs {away_team} from {game_day} at {start_time}")
            
            conn.commit()
            logger.info(f"Successfully deleted {deleted_count} expired NBA gamelines")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting NBA gamelines: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

# Cache functions
def cache_data(data, filename=CACHE_FILE):
    """Cache data with timestamp"""
    cache_data = {
        'timestamp': now,
        'data': data
    }
    try:
        with open(filename, 'wb') as f:
            pickle.dump(cache_data, f)
        logger.info(f"NBA data cached to {filename}")
    except Exception as e:
        logger.error(f"Error caching NBA data: {e}")

def load_cached_data(filename=CACHE_FILE, expiry_minutes=CACHE_EXPIRY_MINUTES):
    """Load cached data if it hasn't expired"""
    try:
        with open(filename, 'rb') as f:
            cache_data = pickle.load(f)
        
        cache_age = now - cache_data['timestamp']
        if cache_age < timedelta(minutes=expiry_minutes):
            logger.info(f"Using cached NBA data (age: {cache_age.total_seconds():.0f}s)")
            return cache_data['data']
        else:
            logger.info(f"NBA cache expired (age: {cache_age.total_seconds():.0f}s)")
    except FileNotFoundError:
        logger.info("No NBA cache file found")
    except Exception as e:
        logger.error(f"Error loading NBA cache: {e}")
    
    return None

def validate_gamelines(gamelines):
    """Validate that gamelines data is complete and reasonable"""
    if not gamelines or len(gamelines) == 0:
        return False
    
    valid_count = 0
    for game in gamelines:
        # Check for essential fields
        if (game.get('home') and game.get('away') and 
            (game.get('home_ml') or game.get('away_ml') or 
             game.get('home_spread') or game.get('over_under'))):
            valid_count += 1
    
    # Consider valid if at least 50% of games have data
    return valid_count >= len(gamelines) * 0.5

def get_gamelines_with_fallback():
    """Get gamelines with fallback strategy: API -> Web -> Manual"""
    manager = GamelineManager()
    
    # Try API scrapers first
    api_sources = {k: v for k, v in SPORTSBOOKS.items() if v['type'] == 'api' and v['enabled']}
    web_sources = {k: v for k, v in SPORTSBOOKS.items() if v['type'] == 'web' and v['enabled']}
    
    all_gamelines = {}
    
    # Try API sources first
    for source_id, config in sorted(api_sources.items(), key=lambda x: x[1]['priority']):
        if not config['function']:
            continue
            
        logger.info(f"Trying NBA API scraper: {config['name']}")
        try:
            gamelines = config['function']()
            if validate_gamelines(gamelines):
                all_gamelines[source_id] = gamelines
                logger.info(f"✓ NBA API {config['name']} successful: {len(gamelines)} games")
                
                # Update database
                for game in gamelines:
                    manager.update_gameline(source_id, game)
                    
                break  # Stop after first successful API source
            else:
                logger.warning(f"✗ NBA API {config['name']} returned invalid data")
        except Exception as e:
            logger.error(f"Error with NBA API {config['name']}: {e}")
    
    # If no API sources worked, try web scrapers
    if not all_gamelines:
        logger.info("No NBA API sources successful, trying web scrapers...")
        for source_id, config in sorted(web_sources.items(), key=lambda x: x[1]['priority']):
            if not config['function']:
                continue
                
            logger.info(f"Trying NBA web scraper: {config['name']}")
            try:
                gamelines = config['function']()
                if validate_gamelines(gamelines):
                    all_gamelines[source_id] = gamelines
                    logger.info(f"✓ NBA Web {config['name']} successful: {len(gamelines)} games")
                    
                    # Update database
                    for game in gamelines:
                        manager.update_gameline(source_id, game)
                        
                    break  # Stop after first successful web source
                else:
                    logger.warning(f"✗ NBA Web {config['name']} returned invalid data")
            except Exception as e:
                logger.error(f"Error with NBA web {config['name']}: {e}")
    
    return all_gamelines

def get_all_nba_gamelines(use_cache=True):
    """Get gamelines from all sources with caching and fallback"""
    
    if use_cache:
        cached_data = load_cached_data()
        if cached_data is not None:
            return cached_data
    
    all_gamelines = get_gamelines_with_fallback()
    
    # Cache the results
    if all_gamelines:
        cache_data(all_gamelines)
    
    return all_gamelines

def main():
    """Main function"""
    print("Fetching NBA gamelines...")
    all_gamelines = get_all_nba_gamelines()
    
    if all_gamelines:
        print(f"Successfully retrieved NBA gamelines from {len(all_gamelines)} sources:")
        for source, games in all_gamelines.items():
            print(f"  {source}: {len(games)} games")
            
        # Format response for API
        formatted_response = {}
        for source, games in all_gamelines.items():
            formatted_response[source] = games
            
        return formatted_response
    else:
        print("No NBA gamelines could be retrieved automatically.")
        print("Please use the manual input route in the web app.")
        return {"gamelines": []}

# Clean up old gamelines and fetch new ones
deleter = GamelineManager()
deleter.delete_gamelines()

nba_game_lines = main()

# Export for API use
if __name__ == "__main__":
    # This allows the file to be imported without running main()
    pass
