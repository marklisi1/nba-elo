import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import pickle
from datetime import datetime
import streamlit as st
# plotting
import plotly.graph_objects as go 
import ast

# Set page config
st.set_page_config(layout="wide", page_title="NBA Elo Ratings")

# Title and description
st.title("NBA Elo Rating Tracker")
st.markdown("We track NBA team performance through Elo ratings throughout the 2024-25 season. Each team picks up where they left off at the end of the 2023-24 regular season.")



# Constants for plotting
TEAM_COLORS = {
        'Los Angeles Lakers': 'rgb(85,37,130)',
        'Phoenix Suns': 'rgb(29,17,96)',
        'Houston Rockets': 'rgb(206,17,65)',
        'Boston Celtics': 'rgb(0,122,51)',
        'Washington Wizards': 'rgb(0,43,92)',
        'Atlanta Hawks': 'rgb(200,16,46)',
        'Detroit Pistons': 'rgb(200,16,46)',
        'Minnesota Timberwolves': 'rgb(12,35,64)',
        'Cleveland Cavaliers': 'rgb(134,0,56)',
        'New Orleans Pelicans': 'rgb(0,22,65)',
        'Oklahoma City Thunder': 'rgb(0,125,195)',
        'Sacramento Kings': 'rgb(91,43,130)',
        'Dallas Mavericks': 'rgb(0,83,188)',
        'Portland Trail Blazers': 'rgb(224,58,62)',
        'Philadelphia 76ers': 'rgb(0,107,182)',
        'Denver Nuggets': 'rgb(13,34,64)',
        'New York Knicks': 'rgb(0,107,182)',
        'Miami Heat': 'rgb(152,0,46)',
        'Toronto Raptors': 'rgb(206,17,65)',
        'Brooklyn Nets': 'rgb(0,0,0)',
        'Los Angeles Clippers': 'rgb(200,16,46)',
        'Orlando Magic': 'rgb(0,125,197)',
        'Golden State Warriors': 'rgb(255,199,44)',
        'Chicago Bulls': 'rgb(206,17,65)',
        'Memphis Grizzlies': 'rgb(93,118,169)',
        'Indiana Pacers': 'rgb(0,45,98)',
        'Utah Jazz': 'rgb(0,43,92)',
        'San Antonio Spurs': 'rgb(196,206,211)',
        'Milwaukee Bucks': 'rgb(0,71,27)',
        'Charlotte Hornets': 'rgb(0,120,140)'
    }
    
TEAM_ABBRS = {
    'Los Angeles Lakers': 'LAL',
    'Phoenix Suns': 'PHX',
    'Houston Rockets': 'HOU',
    'Boston Celtics': 'BOS',
    'Washington Wizards': 'WAS',
    'Atlanta Hawks': 'ATL',
    'Detroit Pistons': 'DET',
    'Minnesota Timberwolves': 'MIN',
    'Cleveland Cavaliers': 'CLE',
    'New Orleans Pelicans': 'NOP',
    'Oklahoma City Thunder': 'OKC',
    'Sacramento Kings': 'SAC',
    'Dallas Mavericks': 'DAL',
    'Portland Trail Blazers': 'POR',
    'Philadelphia 76ers': 'PHI',
    'Denver Nuggets': 'DEN',
    'New York Knicks': 'NYK',
    'Miami Heat': 'MIA',
    'Toronto Raptors': 'TOR',
    'Brooklyn Nets': 'BKN',
    'Los Angeles Clippers': 'LAC',
    'Orlando Magic': 'ORL',
    'Golden State Warriors': 'GSW',
    'Chicago Bulls': 'CHI',
    'Memphis Grizzlies': 'MEM',
    'Indiana Pacers': 'IND',
    'Utah Jazz': 'UTA',
    'San Antonio Spurs': 'SAS',
    'Milwaukee Bucks': 'MIL',
    'Charlotte Hornets': 'CHA'
}

TEAM_NAMES = list(TEAM_ABBRS.keys())

# Helper functions
@st.cache_data
def get_schedule():
    months = ['october','november','december','january','february','march','april']
    current_month = datetime.now().strftime("%B").lower()
    
    schedule = pd.DataFrame()
    
    for month in months:
        url = f"https://www.basketball-reference.com/leagues/NBA_2025_games-{month}.html"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            time.sleep(3)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', id='schedule')
            
            if table is None:
                continue

            columns = [
                'Date', 'Start (ET)', 'Visitor/Neutral', 'away_pts',
                'Home/Neutral', 'home_pts', 'Box Score', 'OT',
                'Attend.', 'LOG', 'Arena', 'Notes'
            ]
            
            rows = []
            for row in table.find_all('tr')[1:]:
                game_data = []
                cells = row.find_all(['td', 'th'])
                if cells:
                    for cell in cells:
                        text = cell.text.strip()
                        game_data.append(text)
                    if game_data:
                        rows.append(game_data)
            
            df = pd.DataFrame(rows, columns=columns)
            df = df[df['away_pts'] != '']
            schedule = pd.concat((schedule, df))
            
            if month == current_month:
                break

        except Exception as e:
            st.error(f"Error processing data for {month}: {str(e)}")
            continue

    return schedule

def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating, expected, actual, k=20):
    return rating + k * (actual - expected)

def calculate_elos(schedule, current_elos, elo_histories):
    for index, row in schedule.iterrows():
        away = row['Visitor/Neutral']
        away_score = int(row['away_pts'])
        home = row['Home/Neutral']
        home_score = int(row['home_pts'])
        home_elo = current_elos[home]
        away_elo = current_elos[away]

        result = 1 if home_score > away_score else 0
        
        expected_home_score = expected_score(current_elos[home], current_elos[away])
        expected_away_score = expected_score(current_elos[away], current_elos[home])
        new_rating_home = update_elo(home_elo, expected_home_score, result)
        new_rating_away = update_elo(away_elo, expected_away_score, 1 - result)

        elo_histories[home].append(new_rating_home)
        elo_histories[away].append(new_rating_away)

        current_elos[home] = new_rating_home
        current_elos[away] = new_rating_away
    
    return current_elos, elo_histories

def elo_bar_plot(current_elos):

    sorted_indices = sorted(range(len(TEAM_NAMES)), key=lambda i: current_elos[TEAM_NAMES[i]])
    # Apply the same permutation to x and bar_colors
    sorted_x = [TEAM_NAMES[i] for i in sorted_indices]
    sorted_y = [current_elos[TEAM_NAMES[i]] for i in sorted_indices]
    sorted_bar_colors = [TEAM_COLORS[TEAM_NAMES[i]] for i in sorted_indices]

    fig = go.Figure(data=[go.Bar(
        x=sorted_x,
        y=sorted_y,
        marker_color=sorted_bar_colors # marker color can be a single color value or an iterable
    )])

    fig.update_layout(
        autosize=False,
        width=2000,
        height=1200,
        plot_bgcolor='white',
        yaxis=dict(
            range=[1000, None]  # Adjust minimum_y_value to the desired minimum y value
        )
    )

    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        autorange=False,
        range=[sorted_y[0]+-100, sorted_y[-1] + 50]
    )

    return fig

def elo_line_plot(elo_histories):
    games = list(range(0, 83))
    
    # Create figure with larger default size
    fig = go.Figure()
    
    # Add teams with enhanced styling
    for team, elo in elo_histories.items():
        # Determine line styling
        line_width = 1
        opacity = 0.3
        
        if team in ['Los Angeles Lakers', 'Boston Celtics', 'Golden State Warriors']:
            line_width = 3
            opacity = 1.0
        
        # Add the line trace
        fig.add_trace(go.Scatter(
            x=games,
            y=elo,
            mode='lines',
            name=TEAM_ABBRS[team],
            line=dict(
                color=TEAM_COLORS[team],
                width=line_width
            ),
            opacity=opacity,
            hovertemplate=f"{team}<br>Game: %{{x}}<br>Elo: %{{y}}<extra></extra>"
        ))
        
        # Add end-of-line labels
        fig.add_annotation(
            x=games[-1],
            y=elo[-1],
            text=TEAM_ABBRS[team],
            xanchor='left',
            yanchor='middle',
            xshift=5,
            showarrow=False,
            font=dict(
                size=10,
                color=TEAM_COLORS[team]
            )
        )

    fig.update_layout(
        title=dict(
            text='NBA Team Elo Ratings Throughout Season',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=24)
        ),
        autosize=False,
        width=2000,
        height=1200,
        plot_bgcolor='white',
        showlegend=False,
        margin=dict(r=100),
        xaxis_title="Games Played",
        yaxis_title="Elo Rating",
        hovermode='closest'
    )
    
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        zeroline=False,
        tickmode='linear',
        tick0=0,
        dtick=10
    )
    
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        zeroline=False,
        tickformat='.0f'
    )
    
    return fig

def elo_delta_plot(deltas):
    
    # Sort teams by delta
    sorted_teams = sorted(deltas.keys(), key=lambda x: deltas[x])
    
    # Create lists for plotting
    x = [TEAM_ABBRS[team] for team in sorted_teams]
    y = [deltas[team] for team in sorted_teams]
    colors = [TEAM_COLORS[team] for team in sorted_teams]
    
    # Create the figure
    fig = go.Figure(data=[go.Bar(
        x=x,
        y=y,
        marker_color=colors
    )])
    
    # Calculate y-axis range with padding
    max_delta = max(y)
    min_delta = min(y)
    padding = (max_delta - min_delta) * 0.1
    
    # Update layout
    fig.update_layout(
        autosize=False,
        width=2000,
        height=1200,
        plot_bgcolor='white',
        showlegend=False,
        # Add a horizontal line at y=0
        shapes=[dict(
            type='line',
            x0=-0.5,
            x1=len(x) - 0.5,
            y0=0,
            y1=0,
            line=dict(
                color='black',
                width=1
            )
        )]
    )
    
    # Update axes
    fig.update_xaxes(
        tickangle=45,
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        range=[min_delta - padding, max_delta + padding]
    )
    
    return fig

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

# Main app logic
def main():
    # Load initial Elos
    try:
        with open('2023-24/final_elos.pkl', 'rb') as f:
            current_elos = pickle.load(f)
    except FileNotFoundError:
        st.error("Error: Could not load initial Elo ratings file.")
        return

    # Get schedule data
    with st.spinner("Fetching schedule data..."):
        schedule = get_schedule()

    if schedule.empty:
        st.error("Error: Could not fetch schedule data.")
        return

    # Initialize elo histories
    elo_histories = {}
    team_names = list(schedule['Visitor/Neutral'].unique())
    for name in team_names:
        elo_histories[name] = [current_elos[name]]

    # Calculate current Elos
    current_elos, elo_histories = calculate_elos(schedule, current_elos, elo_histories)

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Current Ratings", "Rating History", "Rating Changes"])

    with tab1:
        st.header("Current NBA Team Elo Ratings")
        fig_bar = elo_bar_plot(current_elos)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.header("Elo Rating History")
        fig_line = elo_line_plot(elo_histories)
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.header("Elo Rating Changes")
        # Calculate deltas
        elo_deltas = {name: elo_histories[name][-1] - elo_histories[name][0] for name in team_names}
        fig_delta = elo_delta_plot(elo_deltas)
        st.plotly_chart(fig_delta, use_container_width=True)

    # Add a data table section
    st.header("Team Ratings Data")
    df_ratings = pd.DataFrame({
        'Team': list(current_elos.keys()),
        'Current Elo': [round(elo, 1) for elo in current_elos.values()],
        'Change': [round(elo_histories[team][-1] - elo_histories[team][0], 1) for team in current_elos.keys()]
    })
    df_ratings = df_ratings.sort_values('Current Elo', ascending=False)
    st.dataframe(df_ratings, use_container_width=True)

if __name__ == "__main__":
    main()