import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def extract_pitching_stats(url):
    # Fetch the HTML content from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Locate the table containing team pitching stats
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
                    
                    if data_stat == 'W':
                        stats['W'] = value
                    elif data_stat == 'L':
                        stats['L'] = value
                    elif data_stat == 'SO':
                        stats['SO'] = value
                    elif data_stat == 'earned_run_avg':
                        stats['ERA'] = value
                    elif data_stat == 'fip':
                        stats['FIP'] = value

                # Calculate percentages
                wins = int(stats.get('W', 0))
                losses = int(stats.get('L', 0))
                total_games = wins + losses
                
                # Avoid division by zero
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
    # Fetch the HTML content from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Locate the table containing team batting stats
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

def save_to_google_sheet(data, sheet_name):
    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    # Create or open a Google Sheet
    try:
        sheet = client.open(sheet_name).sheet1
    except gspread.SpreadsheetNotFound:
        sheet = client.create(sheet_name).sheet1

    # Clear existing data
    sheet.clear()

    # Prepare data for Google Sheets
    headers = ['URL', 'W', 'L', 'Win Percentage', 'Loss Percentage', 'SO', 'ERA', 'FIP', 'R', 'H', 'HR', 'BA', 'OBP', 'SLG']
    sheet.append_row(headers)

    for row in data:
        sheet.append_row(row)

def main():
    # Read URLs from urls.csv
    urls_df = pd.read_csv('urls.csv')
    urls = urls_df['URL'].tolist()

    all_stats = []

    for url in urls:
        pitching_stats = extract_pitching_stats(url)
        batting_stats = extract_batting_stats(url)
        
        if pitching_stats and batting_stats:
            # Combine stats with the URL
            combined_stats = [url] + [pitching_stats.get(stat, '') for stat in ['W', 'L', 'Win Percentage', 'Loss Percentage', 'SO', 'ERA', 'FIP']] + \
                             [batting_stats.get(stat, '') for stat in ['R', 'H', 'HR', 'BA', 'OBP', 'SLG']]
            all_stats.append(combined_stats)

    # Save the collected stats to Google Sheets
    save_to_google_sheet(all_stats, "Baseball Stats 2024")

if __name__ == "__main__":
    main()
