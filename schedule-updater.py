from datetime import datetime
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup

def get_schedule():

    months = ['october','november','december','january','february','march','april']
    current_month = datetime.now().strftime("%B").lower()
    
    schedule = pd.DataFrame()

    for month in months:
        url = f"https://www.basketball-reference.com/leagues/NBA_2025_games-{month}.html"

        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            # Make the request with a slight delay to be respectful to the server
            time.sleep(3)
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the schedule table
            table = soup.find('table', id='schedule')
            
            if table is None:
                raise ValueError("Schedule table not found on the page")

            # Define the columns we want to extract
            columns = [
                'Date',
                'Start (ET)',
                'Visitor/Neutral',
                'away_pts',
                'Home/Neutral',
                'home_pts',
                'Box Score',
                'OT',
                'Attend.',
                'LOG',
                'Arena',
                'Notes'
            ]
            
            # Extract rows
            rows = []
            for row in table.find_all('tr')[1:]:  # Skip header row
                game_data = []
                cells = row.find_all(['td', 'th'])
                if cells:  # Only process rows with data
                    for cell in cells:
                        text = cell.text.strip()
                        game_data.append(text)
                    if game_data:  # Only append non-empty rows
                        rows.append(game_data)
            
            # Create DataFrame with explicit column names
            df = pd.DataFrame(rows, columns=columns)
            df = df[df['away_pts'] != '']
            schedule = pd.concat((schedule, df))
            
            if month == current_month:
                break
                



        except requests.RequestException as e:
            print(f"Error fetching the webpage: {e}")
        except Exception as e:
            print(f"Error processing the data: {e}")

    # Optionally save to CSV
    schedule.to_csv('2025_schedule.csv', index=False)
    print("\nData has been saved to '2025_schedule.csv'")
    return schedule

schedule = get_schedule()