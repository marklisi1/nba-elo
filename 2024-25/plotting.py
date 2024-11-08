import pandas as pd
import plotly.graph_objects as go 
import ast

def elo_bar_plot(current_elos):

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
    x = TEAM_NAMES
    y = [current_elos[i] for i in TEAM_NAMES]
    bar_colors = [TEAM_COLORS[i] for i in TEAM_NAMES]

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
    games = list(range(0, 83))

    fig = go.Figure() # ha ha
    for team, elo in elo_histories.items():
        fig.add_trace(go.Scatter(x=games, y=elo,
                                mode='lines',
                                name=TEAM_ABBRS[team],
                                line=dict(color=TEAM_COLORS[team])))
        

    fig.update_layout(
        autosize=False,
        width=2000,
        height=1200,
        plot_bgcolor='white'
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
        gridcolor='lightgrey'
    )

    return fig

def elo_delta_plot(deltas):
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