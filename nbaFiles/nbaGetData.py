import datetime as dt
import requests
from bs4 import BeautifulSoup
import csv
import os

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

def get_team_stats(team, year):
    # Create filename based on team and year
    filename = f"{team}_{year}_stats.csv"
    
    # Check if file exists
    if os.path.exists(filename):
        # Read data from existing CSV file
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            all_data = [row for row in reader]
        print(f"Loaded data from existing file: {filename}")
        return all_data
    else:
        # Scrape data from website
        url = f'https://www.basketball-reference.com/teams/{team}/{year}/gamelog/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('tbody')
        rows = body.find_all('tr')  

        all_data = []
        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue
            
            data = {
                "Rk": cells[0].text if len(cells) > 0 else None,
                "G": cells[1].text if len(cells) > 1 else None,
                "Date": cells[2].text if len(cells) > 2 else None,
                "Opp": cells[3].text if len(cells) > 3 else None,
                "W/L": cells[4].text if len(cells) > 4 else None,
                "Tm": cells[5].text if len(cells) > 5 else None,
                "Opp_Pts": cells[6].text if len(cells) > 6 else None,
                "FG": cells[7].text if len(cells) > 7 else None,
                "FGA": cells[8].text if len(cells) > 8 else None,
                "FG%": cells[9].text if len(cells) > 9 else None,
                "3P": cells[10].text if len(cells) > 10 else None,
                "3PA": cells[11].text if len(cells) > 11 else None,
                "3P%": cells[12].text if len(cells) > 12 else None,
                "FT": cells[13].text if len(cells) > 13 else None,
                "FTA": cells[14].text if len(cells) > 14 else None,
                "FT%": cells[15].text if len(cells) > 15 else None,
                "ORB": cells[16].text if len(cells) > 16 else None,
                "TRB": cells[17].text if len(cells) > 17 else None,
                "AST": cells[18].text if len(cells) > 18 else None,
                "STL": cells[19].text if len(cells) > 19 else None,
                "BLK": cells[20].text if len(cells) > 20 else None,
                "TOV": cells[21].text if len(cells) > 21 else None,
                "PF": cells[22].text if len(cells) > 22 else None,
                "OFG": cells[23].text if len(cells) > 23 else None,
                "OFGA": cells[24].text if len(cells) > 24 else None,
                "OFG%": cells[25].text if len(cells) > 25 else None,
                "O3P": cells[26].text if len(cells) > 26 else None,
                "O3PA": cells[27].text if len(cells) > 27 else None,
                "O3P%": cells[28].text if len(cells) > 28 else None,
                "OFT": cells[29].text if len(cells) > 29 else None,
                "OFTA": cells[30].text if len(cells) > 30 else None,
                "OFT%": cells[31].text if len(cells) > 31 else None,
                "OORB": cells[32].text if len(cells) > 32 else None,
                "OTRB": cells[33].text if len(cells) > 33 else None,
                "OAST": cells[34].text if len(cells) > 34 else None,
                "OSTL": cells[35].text if len(cells) > 35 else None,
                "OBLK": cells[36].text if len(cells) > 36 else None,
                "OTOV": cells[37].text if len(cells) > 37 else None,
                "OPF": cells[38].text if len(cells) > 38 else None,
            }
            all_data.append(data)

        # Save data to CSV file
        if all_data:  # Only save if we got data
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=all_data[0].keys())
                writer.writeheader()
                writer.writerows(all_data)
            print(f"Saved data to new file: {filename}")

        return all_data

def get_player_stats(player, year):
    fname_lname = player.split(' ')
    fname = fname_lname[0]
    lname = fname_lname[1]
    letter = lname[0].lower()
    print(letter)
    player_id = lname[0:5] + fname[0:2] +'01'
    player_id = player_id.lower()
    print(player_id)

def get_coach_stats(coach):
    pass

# Example usage
team_stats = get_team_stats("DET", "2025")
