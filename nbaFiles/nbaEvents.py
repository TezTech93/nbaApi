import datetime as dt
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class NBAEvents:
    def __init__(self):
        self.sport = 'nba'
    
    def get_schedule(self, days: int = 7) -> List[Dict]:
        """Get NBA schedule for upcoming days"""
        try:
            upcoming_dates = self._get_upcoming_dates(days)
            games = []
            
            for target_date in upcoming_dates:
                url = f"https://www.espn.com/nba/schedule/_/date/{target_date.strftime('%Y%m%d')}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for game containers
                game_containers = soup.find_all('div', class_=lambda x: x and 'ScheduleTables' in x)
                
                for container in game_containers:
                    try:
                        teams = container.find_all('a', class_='team-name')
                        for i in range(0, len(teams), 2):
                            if i + 1 < len(teams):
                                away_team = self._clean_team_name(teams[i].text.strip())
                                home_team = self._clean_team_name(teams[i + 1].text.strip())
                                
                                if away_team and home_team:
                                    game_data = {
                                        'game_day': target_date.strftime('%Y-%m-%d'),
                                        'start_time': 'TBD',
                                        'home_team': home_team,
                                        'away_team': away_team
                                    }
                                    games.append(game_data)
                    except Exception as e:
                        logger.debug(f"Error parsing NBA game container: {e}")
                        continue
            
            return games
            
        except Exception as e:
            logger.error(f"Error scraping NBA schedule: {e}")
            return []
    
    def get_existing_gamelines(self, days: int = 7) -> List[Dict]:
        """Get existing NBA gamelines from database"""
        try:
            # Connect to NBA gamelines database
            conn = sqlite3.connect('nba_gamelines.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM gamelines 
                WHERE game_day BETWEEN date('now') AND date('now', ?)
                ORDER BY game_day, start_time
            ''', (f'+{days} days',))
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error reading NBA gamelines: {e}")
            return []
    
    def _get_upcoming_dates(self, days: int):
        """Get dates for the next X days"""
        today = dt.date.today()
        return [today + dt.timedelta(days=i) for i in range(days)]
    
    def _clean_team_name(self, team_name: str) -> str:
        """Clean team name for consistency"""
        # Remove location prefixes and clean up names
        clean_name = team_name.split()[-1]  # Get last word (team name)
        return clean_name
