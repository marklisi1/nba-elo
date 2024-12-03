import streamlit as st
import requests
import pandas as pd
import time
import pickle
from datetime import datetime
import plotly.graph_objects as go

# Set page config
st.set_page_config(layout="wide", page_title="NBA Elo Ratings")

# Title and description
st.title("NBA Elo Rating Tracker")
st.markdown("Track which teams are *really* the NBA's best using Elo.")

st.header("What's Elo?")
st.write("Elo (not ELO) is a mathematical method for estimating the relative skill levels of players in zero-sum games; it was initially invented as a chess rating system. Here, we extend it to the NBA!")
st.header("How does it work?")
st.write("A team gains points for winning and loses points for losing (duh). The amount of rating a team gains or loses is based on their initial rating as well as their opponents - beating a higher-rated opponent will boost a team's rating much more, and losing to a lower-rated opponent will decrease a team's rating more.")
st.header("Why does this matter?")
st.markdown("This project was built as a way to settle arguments among my friends about which teams are actually the best - specifically, whether the top teams in the East are overrated since they play more games in the - let's be honest, much weaker - Eastern Conference. By tracking a metric that accounts for strength of opponents, we can get a more holistic view of which teams are the toughest to beat.")

# Constants 
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
    TEAM_NAMES = list(TEAM_ABBRS.keys())
    x = TEAM_NAMES
    y = [current_elos[i] for i in TEAM_NAMES]
    bar_colors = [TEAM_COLORS[i] for i in TEAM_NAMES]

    sorted_indices = sorted(range(len(TEAM_NAMES)), key=lambda i: current_elos[TEAM_NAMES[i]])
    sorted_x = [TEAM_NAMES[i] for i in sorted_indices]
    sorted_y = [current_elos[TEAM_NAMES[i]] for i in sorted_indices]
    sorted_bar_colors = [TEAM_COLORS[TEAM_NAMES[i]] for i in sorted_indices]

    fig = go.Figure(data=[go.Bar(
        x=sorted_x,
        y=sorted_y,
        marker_color=sorted_bar_colors
    )])

    fig.update_layout(
        height=600,
        plot_bgcolor='white',
        yaxis=dict(
            range=[1000, None]
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

def elo_line_plot(elo_histories, focused_team=None):
    games = list(range(0, 83))
    
    fig = go.Figure()
    
    # Add teams with enhanced styling
    for team, elo in elo_histories.items():
        # Determine line styling based on whether this is the focused team
        if team == focused_team:
            line_width = 4
            opacity = 1.0
        else:
            line_width = 1
            opacity = 0.4
        
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
        if team == focused_team or focused_team is None:
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
                ),
                opacity=opacity
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
        height=600,
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
    sorted_teams = sorted(deltas.keys(), key=lambda x: deltas[x])
    x = [TEAM_ABBRS[team] for team in sorted_teams]
    y = [deltas[team] for team in sorted_teams]
    colors = [TEAM_COLORS[team] for team in sorted_teams]
    
    fig = go.Figure(data=[go.Bar(
        x=x,
        y=y,
        marker_color=colors
    )])
    
    max_delta = max(y)
    min_delta = min(y)
    padding = (max_delta - min_delta) * 0.1
    
    fig.update_layout(
        height=600,
        plot_bgcolor='white',
        showlegend=False,
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

# Main app logic
def main():
    # Load initial Elos
    try:
        with open('2023-24/final_elos.pkl', 'rb') as f:
            current_elos = pickle.load(f)
    except FileNotFoundError:
        st.error("Error: Could not load initial Elo ratings file.")
        return

    schedule = pd.read_csv('2025_schedule.csv', index_col=False)

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
        st.write("This plot reflects the current Elo standings in the NBA. Higher is better!")
        fig_bar = elo_bar_plot(current_elos)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.header("Elo Rating History")
        st.write("Here we can track each team's progress across the 2024-25 NBA season. Updated nightly!")
        # Add team selector
        focused_team = st.selectbox(
            "Select a team to focus on:",
            options= sorted(team_names),
            index=0
        )
        
        # Pass None if "All Teams" is selected, otherwise pass the team name
        selected_team = None if focused_team == "All Teams" else focused_team
        fig_line = elo_line_plot(elo_histories, selected_team)
        st.plotly_chart(fig_line, use_container_width=True)
    
    with tab3:
        st.header("Elo Rating Changes")
        st.write("This plot reflects each team's change in Elo from the end of the previous season. Teams on the left are doing much worse, teams on the right are doing much better!")
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
    st.dataframe(df_ratings, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()