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
        
        # CORRECTED: Find the main table with the correct ID
        table = soup.find('table', {'id': 'team_game_log_reg'})
        if not table:
            print("No gamelog table found with ID 'team_game_log_reg'")
            # Try alternative table ID
            table = soup.find('table', {'id': 'tgl_basic'})
            if not table:
                print("No gamelog table found with ID 'tgl_basic' either")
                return {"Data": []}
            
        body = table.find('tbody')
        if not body:
            print("No table body found")
            return {"Data": []}
            
        rows = body.find_all('tr', class_=lambda x: x != 'thead')
        
        all_data = []
        game_count = 0
        
        # Get header information for debugging
        headers = table.find('thead').find_all('th')
        header_names = [header.get('data-stat') for header in headers if header.get('data-stat')]
        print(f"Available columns: {header_names}")
        
        for row in rows:
            # Skip rows that don't have game data
            if row.get('class') and 'thead' in row.get('class'):
                continue
                
            cells = row.find_all(['td', 'th'])
            if len(cells) < 10:  # Need at least basic game info
                continue
            
            # Extract data from cells using data-stat attributes for reliability
            data = {}
            
            try:
                # Use data-stat attributes to correctly identify each cell
                for cell in cells:
                    data_stat = cell.get('data-stat')
                    if data_stat:
                        data[data_stat] = cell.text.strip()
                
                # Map to your expected field names for consistency
                mapped_data = {
                    "Rk": data.get('ranker', ''),
                    "G": data.get('team_game_num_season', ''),
                    "Date": data.get('date', ''),
                    "Location": data.get('game_location', ''),
                    "Opp": data.get('opp_name_abbr', ''),
                    "W/L": data.get('team_game_result', ''),
                    "Tm": data.get('team_game_score', ''),
                    "Opp_Pts": data.get('opp_team_game_score', ''),
                    "OT": data.get('overtimes', ''),
                    "FG": data.get('fg', ''),
                    "FGA": data.get('fga', ''),
                    "FG%": data.get('fg_pct', ''),
                    "3P": data.get('fg3', ''),
                    "3PA": data.get('fg3a', ''),
                    "3P%": data.get('fg3_pct', ''),
                    "2P": data.get('fg2', ''),
                    "2PA": data.get('fg2a', ''),
                    "2P%": data.get('fg2_pct', ''),
                    "eFG%": data.get('efg_pct', ''),
                    "FT": data.get('ft', ''),
                    "FTA": data.get('fta', ''),
                    "FT%": data.get('ft_pct', ''),
                    "ORB": data.get('orb', ''),
                    "DRB": data.get('drb', ''),
                    "TRB": data.get('trb', ''),
                    "AST": data.get('ast', ''),
                    "STL": data.get('stl', ''),
                    "BLK": data.get('blk', ''),
                    "TOV": data.get('tov', ''),
                    "PF": data.get('pf', ''),
                    # Opponent stats
                    "OFG": data.get('opp_fg', ''),
                    "OFGA": data.get('opp_fga', ''),
                    "OFG%": data.get('opp_fg_pct', ''),
                    "O3P": data.get('opp_fg3', ''),
                    "O3PA": data.get('opp_fg3a', ''),
                    "O3P%": data.get('opp_fg3_pct', ''),
                    "O2P": data.get('opp_fg2', ''),
                    "O2PA": data.get('opp_fg2a', ''),
                    "O2P%": data.get('opp_fg2_pct', ''),
                    "OeFG%": data.get('opp_efg_pct', ''),
                    "OFT": data.get('opp_ft', ''),
                    "OFTA": data.get('opp_fta', ''),
                    "OFT%": data.get('opp_ft_pct', ''),
                    "OORB": data.get('opp_orb', ''),
                    "ODRB": data.get('opp_drb', ''),
                    "OTRB": data.get('opp_trb', ''),
                    "OAST": data.get('opp_ast', ''),
                    "OSTL": data.get('opp_stl', ''),
                    "OBLK": data.get('opp_blk', ''),
                    "OTOV": data.get('opp_tov', ''),
                    "OPF": data.get('opp_pf', '')
                }
                
                # Only add if we have basic game data
                if mapped_data["Date"] and mapped_data["Opp"]:
                    all_data.append(mapped_data)
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
if det_stats.get('Data'):
    print(f"First game: {det_stats['Data'][0]}")
