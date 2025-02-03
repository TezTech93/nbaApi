import datetime as dt
import requests
from bs4 import BeautifulSoup

now = dt.datetime.now()
today = f'{now.month},{now.day},{now.year}'



def get_team_stats(team,year):
    url = f'https://www.basketball-reference.com/teams/{team}/{year}/gamelog'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    
    stats = []
    stat_row = []
    for row in rows:
        #map to stat_row
        for cell in row.find_all('td'):
            stat_row.append(cell.text)
        
        #add stat_row to stats
        if stat_row:
            stats.append(stat_row)
            stat_row = []
        #get attrs
        print(stats)
        print(len(stats))

def get_player_stats(player):
    pass

def get_coach_stats(coach):
    pass

get_team_stats('DET',2024)