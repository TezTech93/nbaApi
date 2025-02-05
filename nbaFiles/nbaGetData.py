import datetime as dt
import requests
from bs4 import BeautifulSoup

now = dt.datetime.now()
today = f'{now.month},{now.day},{now.year}'

headers = [
    "Rk", "G", "Date", "Opp", "W/L", "Tm", "Opp", "FG", "FGA", "FG%", "3P", "3PA", "3P%", 
    "FT", "FTA", "FT%", "ORB", "TRB", "AST", "STL", "BLK", "TOV", "PF", 
    "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%", "ORB", "TRB", "AST", "STL", "BLK", "TOV", "PF"
]

data = {
            "Rk": None, "G": None, "Date": None, "Opp": None, "W/L": None, "Tm": None, 
            "Opp": None, "FG": None, "FGA": None, "FG%": None, "3P": None, "3PA": None, 
            "3P%": None, "FT": None, "FTA": None, "FT%": None, "ORB": None, "TRB": None, 
            "AST": None, "STL": None, "BLK": None, "TOV": None, "PF": None, 
            "OFG": None, "OFGA": None, "OFG%": None, "O3P": None, "O3PA": None, "O3P%": None, 
            "OFT": None, "OFTA": None, "OFT%": None, "OORB": None, "OTRB": None, "OAST": None, 
            "OSTL": None, "OBLK": None, "OTOV": None, "OPF": None
        }



def get_team_stats(team,year):
    url = f'https://www.basketball-reference.com/teams/{team}/{year}/gamelog/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    
    stats = []
    stat_row = []
    stat_dict_list = []
    for row in rows:
        #map to stat_row
        for cell in row.find_all('td'):
            stat_row.append(cell.text)
        
        #add stat_row to stats
        if stat_row:
            stats.append(stat_row)
            stat_row = []

        for row in stats:
            data["Rk"] = row[0]
            data["G"] = row[1]
            data["Date"] = row[2]
            data["Opp"] = row[3]
            data["W/L"] = row[4]
            data["Tm"] = row[5]
            data["Opp"] = row[6]
            data["FG"] = row[7]
            data["FGA"] = row[8]
            data["FG%"] = row[9]
            data["3P"] = row[10]
            data["3PA"] = row[11]
            data["3P%"] = row[12]
            data["FT"] = row[13]
            data["FTA"] = row[14]
            data["FT%"] = row[15]
            data["ORB"] = row[16]
            data["TRB"] = row[17]
            data["AST"] = row[18]
            data["STL"] = row[19]
            data["BLK"] = row[20]
            data["TOV"] = row[21]
            data["PF"] = row[22]
            data["OFG"] = row[7 + 16]
            data["OFGA"] = row[8 + 16]
            data["OFG%"] = row[9 + 16]
            data["O3P"] = row[10 + 16]
            data["O3PA"] = row[11 + 16]
            data["O3P%"] = row[12 + 16]
            data["OFT"] = row[13 + 16]
            data["OFTA"] = row[14 + 16]
            data["OFT%"] = row[15 + 16]
            data["OORB"] = row[16 + 16]
            data["OTRB"] = row[17 + 16]
            data["OAST"] = row[18 + 16]
            data["OSTL"] = row[19 + 16]
            data["OBLK"] = row[20 + 16]
            data["OTOV"] = row[21 + 16]
            data["OPF"] = row[22 + 16]
            print(data)
            stat_dict_list.append(data.copy())
        return stat_dict_list


def get_player_stats(player,year):
    fname_lname = player.split(' ')
    fname = fname_lname[0]
    lname = fname_lname[1]
    letter = lname[0].lower()
    print(letter)
    player_id = lname[0:5] + fname[0:2] +'01'
    player_id = player_id.lower()
    print(player_id)
    #url = 'https://www.basketball-reference.com/players/{letter}/{player_id}/gamelog/{year}'
    #response = requests.get(url)
    #soup = BeautifulSoup(response.text, 'html.parser')
    #rows = soup.find_all('tr')

    #for row in rows:
        #print(row)

def get_coach_stats(coach):
    pass

get_player_stats('Dell Curry','2024')