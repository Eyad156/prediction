import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def extract_pitching_stats(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    time.sleep(2)

    table = soup.find("table", {"id": "team_pitching"})
    stats = {}

    if table:
        tfoot = table.find("tfoot")
        if tfoot:
            team_totals_row = tfoot.find("tr")
            if team_totals_row:
                for td in team_totals_row.find_all("td"):
                    data_stat = td.get("data-stat")
                    value = td.text.strip()
                    
                    if data_stat == 'SO':
                        stats['SO'] = value
                    elif data_stat == 'earned_run_avg':
                        stats['ERA'] = value
                    elif data_stat == 'fip':
                        stats['FIP'] = value
                    elif data_stat == 'W':
                        stats['W'] = value
                    elif data_stat == 'L':
                        stats['L'] = value

                wins = int(stats.get('W', 0))
                losses = int(stats.get('L', 0))
                total_games = wins + losses

                if total_games > 0:
                    win_percentage = (wins / total_games) * 100
                    loss_percentage = (losses / total_games) * 100
                else:
                    win_percentage = loss_percentage = 0

                stats['Win Percentage'] = f"{win_percentage:.2f}%"
                stats['Loss Percentage'] = f"{loss_percentage:.2f}%"
            else:
                print(f"Could not find team totals row in tfoot for URL: {url}.")
        else:
            print(f"Could not find the tfoot section in the table for URL: {url}.")
    else:
        print(f"Could not find the table with ID 'team_pitching' for URL: {url}.")
    
    return stats

def extract_batting_stats(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": "team_batting"})
    stats = {}

    if table:
        tfoot = table.find("tfoot")
        if tfoot:
            team_totals_row = tfoot.find("tr")
            if team_totals_row:
                for td in team_totals_row.find_all("td"):
                    data_stat = td.get("data-stat")
                    value = td.text.strip()
                    
                    if data_stat == 'R':
                        stats['R'] = value
                    elif data_stat == 'H':
                        stats['H'] = value
                    elif data_stat == 'HR':
                        stats['HR'] = value
                    elif data_stat == 'SB':
                        stats['SB'] = value
                    elif data_stat == 'batting_avg':
                        stats['BA'] = value
                    elif data_stat == 'onbase_perc':
                        stats['OBP'] = value
                    elif data_stat == 'slugging_perc':
                        stats['SLG'] = value
            else:
                print(f"Could not find team totals row in tfoot for URL: {url}.")
        else:
            print(f"Could not find the tfoot section in the table for URL: {url}.")
    else:
        print(f"Could not find the table with ID 'team_batting' for URL: {url}.")
    
    return stats

def extract_player_stats(url, table_id):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": table_id})
    player_stats = []

    if table:
        tbody = table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                player_data = {}
                for td in row.find_all("td"):
                    data_stat = td.get("data-stat")
                    value = td.text.strip()
                    player_data[data_stat] = value
                player_stats.append(player_data)
        else:
            print(f"Could not find tbody in the table with ID '{table_id}' for URL: {url}.")
    else:
        print(f"Could not find the table with ID '{table_id}' for URL: {url}.")
    
    return player_stats

def save_team_stats_to_excel(data, filename):
    columns = ['URL', 'W', 'L', 'Win Percentage', 'Loss Percentage', 'SO', 'ERA', 'FIP', 'BA', 'OBP', 'SLG']
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(filename, index=False)

def save_player_stats_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

def main():
    urls_df = pd.read_csv('urls.csv')
    urls = urls_df['URL'].tolist()

    team_stats = []  # To hold team stats for each URL
    all_player_stats = []  # To hold player stats for each URL

    for url in urls:
        pitching_stats = extract_pitching_stats(url)
        batting_stats = extract_batting_stats(url)

        if pitching_stats and batting_stats:
            combined_stats = [url] + [
                pitching_stats.get(stat, '') for stat in ['W', 'L', 'Win Percentage', 'Loss Percentage', 'SO', 'ERA', 'FIP']
            ] + [
                batting_stats.get(stat, '') for stat in ['BA', 'OBP', 'SLG']
            ]
            team_stats.append(combined_stats)

        # Extract player stats for both batting and pitching
        batting_player_stats = extract_player_stats(url, 'team_batting')
        pitching_player_stats = extract_player_stats(url, 'team_pitching')
        
        # Label the data with the URL and the type of stat
        for player in batting_player_stats:
            player['URL'] = url
            player['Stat Type'] = 'Batting'
            all_player_stats.append(player)
        
        for player in pitching_player_stats:
            player['URL'] = url
            player['Stat Type'] = 'Pitching'
            all_player_stats.append(player)

    # Save team stats to one Excel file
    save_team_stats_to_excel(team_stats, "Baseball_Team_Stats_2024.xlsx")

    # Save player stats to another Excel file
    save_player_stats_to_excel(all_player_stats, "Baseball_Player_Stats_2024.xlsx")

if __name__ == "__main__":
    main()
