import requests
import bs4
from bs4 import BeautifulSoup

url3 = 'https://sportsbook.draftkings.com/leagues/basketball/nba'

def show_url_td(url):
    content = requests.get(url)
    soup = BeautifulSoup(content.content, 'html.parser')
    tr_data = soup.find_all('tr')
    all_teams = soup.select('.event-cell__name-text')
    all_spreads_and_overUnder = soup.select('.sportsbook-outcome-cell__line')
    all_moneylines = soup.select('.sportsbook-odds.american.no-margin.default-color')

    all_gamelines = [] #return

    spreads = []
    overUnders = []
    num = 0

    defOdds = '-110'

    for spread in all_spreads_and_overUnder:
        if spread.text[0] == '+' or spread.text[0] == '-':
            spreads.append(spread.text)
        else:
            overUnders.append(spread.text)
        num += 1
    num = 0

    for row in range(200):
        try:
            if num % 2 == 1:
                my_dict = {
                            'home': all_teams[num].text, 'away': all_teams[num - 1].text,
                            'home_ml': all_moneylines[num].text, 'away_ml': all_moneylines[num - 1].text, 
                            'home_spread': spreads[num], 'away_spread': spreads[num - 1],
                            'home_spread_odds': defOdds, 'away_spread_odds': defOdds,
                            'over': f'O {overUnders[num]}', 'under': f'U {overUnders[num - 1]}',
                            'over_odds': defOdds, 'under_odds': defOdds
                        }
                all_gamelines.append(my_dict)
        except:
            pass
        num += 1
    if len(all_gamelines) >= 0:
        print('out of season')
    for gl in all_gamelines:
        print(gl)
    return all_gamelines

nba_game_lines = show_url_td(url3)
