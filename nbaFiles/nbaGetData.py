import datetime as dt
import requests
from bs4 import BeautifulSoup
import csv
import os
import re

now = dt.datetime.now()
today = f'{now.month},{now.day},{now.year}'

def get_team_stats(team, year):
    # Create filename based on team and year
    filename = f"{team}_{year}_stats.csv"
    
    # Check if file exists and is recent (less than 24 hours old)
    if os.path.exists(filename):
        file_time = os.path.getmtime(filename)
        current_time = dt.datetime.now().timestamp()
        # If file is less than 24 hours old, use it
        if current_time - file_time < 86400:  # 86400 seconds = 24 hours
            # Read data from existing CSV file
            with open(filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                all_data = [row for row in reader]
            print(f"Loaded data from existing file: {filename}")
            return {"Data": all_data}
    
    # Scrape data from website
    url = f'https://www.basketball-reference.com/teams/{team}/{year}/gamelog/'
    print(f"Scraping data from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main table - look for the gamelog table
        table = soup.find('table', {'id': 'tgl_basic'})
        if not table:
            print("No gamelog table found")
            return {"Data": []}
            
        body = table.find('tbody')
        if not body:
            print("No table body found")
            return {"Data": []}
            
        rows = body.find_all('tr', class_=lambda x: x != 'thead')
        
        all_data = []
        game_count = 0
        
        for row in rows:
            # Skip rows that don't have game data
            if row.get('class') and 'thead' in row.get('class'):
                continue
                
            cells = row.find_all(['td', 'th'])
            if len(cells) < 10:  # Need at least basic game info
                continue
            
            # Extract data from cells
            data = {}
            
            # Basic game info
            try:
                data["Rk"] = cells[0].text.strip() if cells[0].name == 'td' else None
                data["G"] = cells[1].text.strip() if len(cells) > 1 and cells[1].name == 'td' else None
                data["Date"] = cells[2].text.strip() if len(cells) > 2 else None
                
                # Opponent - handle links
                opp_cell = cells[3] if len(cells) > 3 else None
                if opp_cell:
                    opp_link = opp_cell.find('a')
                    data["Opp"] = opp_link.text.strip() if opp_link else opp_cell.text.strip()
                else:
                    data["Opp"] = None
                
                # Game result and scores
                data["W/L"] = cells[4].text.strip() if len(cells) > 4 else None
                data["Tm"] = cells[5].text.strip() if len(cells) > 5 else None
                data["Opp_Pts"] = cells[6].text.strip() if len(cells) > 6 else None
                
                # Team stats
                data["FG"] = cells[7].text.strip() if len(cells) > 7 else None
                data["FGA"] = cells[8].text.strip() if len(cells) > 8 else None
                data["FG%"] = cells[9].text.strip() if len(cells) > 9 else None
                data["3P"] = cells[10].text.strip() if len(cells) > 10 else None
                data["3PA"] = cells[11].text.strip() if len(cells) > 11 else None
                data["3P%"] = cells[12].text.strip() if len(cells) > 12 else None
                data["FT"] = cells[13].text.strip() if len(cells) > 13 else None
                data["FTA"] = cells[14].text.strip() if len(cells) > 14 else None
                data["FT%"] = cells[15].text.strip() if len(cells) > 15 else None
                data["ORB"] = cells[16].text.strip() if len(cells) > 16 else None
                data["TRB"] = cells[17].text.strip() if len(cells) > 17 else None
                data["AST"] = cells[18].text.strip() if len(cells) > 18 else None
                data["STL"] = cells[19].text.strip() if len(cells) > 19 else None
                data["BLK"] = cells[20].text.strip() if len(cells) > 20 else None
                data["TOV"] = cells[21].text.strip() if len(cells) > 21 else None
                data["PF"] = cells[22].text.strip() if len(cells) > 22 else None
                
                # Opponent stats (if available)
                if len(cells) > 38:
                    data["OFG"] = cells[23].text.strip() if len(cells) > 23 else None
                    data["OFGA"] = cells[24].text.strip() if len(cells) > 24 else None
                    data["OFG%"] = cells[25].text.strip() if len(cells) > 25 else None
                    data["O3P"] = cells[26].text.strip() if len(cells) > 26 else None
                    data["O3PA"] = cells[27].text.strip() if len(cells) > 27 else None
                    data["O3P%"] = cells[28].text.strip() if len(cells) > 28 else None
                    data["OFT"] = cells[29].text.strip() if len(cells) > 29 else None
                    data["OFTA"] = cells[30].text.strip() if len(cells) > 30 else None
                    data["OFT%"] = cells[31].text.strip() if len(cells) > 31 else None
                    data["OORB"] = cells[32].text.strip() if len(cells) > 32 else None
                    data["OTRB"] = cells[33].text.strip() if len(cells) > 33 else None
                    data["OAST"] = cells[34].text.strip() if len(cells) > 34 else None
                    data["OSTL"] = cells[35].text.strip() if len(cells) > 35 else None
                    data["OBLK"] = cells[36].text.strip() if len(cells) > 36 else None
                    data["OTOV"] = cells[37].text.strip() if len(cells) > 37 else None
                    data["OPF"] = cells[38].text.strip() if len(cells) > 38 else None
                
                # Only add if we have basic game data
                if data["Date"] and data["Opp"]:
                    all_data.append(data)
                    game_count += 1
                    
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        print(f"Successfully scraped {game_count} games for {team} {year}")

        # Save data to CSV file
        if all_data:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                if all_data:
                    writer = csv.DictWriter(file, fieldnames=all_data[0].keys())
                    writer.writeheader()
                    writer.writerows(all_data)
                print(f"Saved data to new file: {filename}")

        return {"Data": all_data}
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        return {"Data": [], "error": str(e)}

def get_player_stats(player, year):
    """Get player stats - placeholder implementation"""
    fname_lname = player.split(' ')
    if len(fname_lname) < 2:
        return {"error": "Please provide both first and last name"}
        
    fname = fname_lname[0]
    lname = fname_lname[1]
    letter = lname[0].lower()
    player_id = lname[0:5].lower() + fname[0:2].lower() + '01'
    
    print(f"Player ID: {player_id}")
    return {"player_id": player_id, "message": "Player stats endpoint"}

def get_coach_stats(coach):
    """Get coach stats - placeholder implementation"""
    return {"message": "Coach stats endpoint - implementation pending"}

det_stats = get_team_stats("DET", "2024")
print(f"Retrieved {len(det_stats.get('Data', []))} games for Detroit Pistons")
