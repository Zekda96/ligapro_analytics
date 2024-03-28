"""
This script reads through all 'lineups' files and creates a single
file with all teams' stats
"""

import os
import json
import pandas as pd

# teams = {'liga': 'LDU',
#          'emelec': 'Emelec',
#          'barcelona': 'Barcelona',
#          'delfin': 'Delfin',
#          'catolica': 'U. Catolica',
#          'nacional': 'El Nacional',
#          'macara': 'Macara',
#          'imbabura': 'Imbabura',
#          'cuenca': 'D. Cuenca',
#          'aucas': 'Aucas',
#          'independiente': 'IDV',
#          'mushuc-runa': 'Mushuc Runa',
#          'orense': 'Orense',
#          'cumbaya': 'Cumbaya',
#          'libertad': 'Libertad',
#          'tecnico': 'Tecnico U.'
#          }

# Find all matchweek folders
base_dir = './data/matches'
matchweek_dirs = os.listdir(base_dir)
# Select only directories
matchweek_folders = [x for x in matchweek_dirs if os.path.isdir(os.path.join(base_dir,x))]

match_files = []
data = []
# Loop through folders
for week in matchweek_folders:
    match_files = os.listdir(os.path.join(base_dir, week))

    # Loop through files
    for file in match_files:
        if file[-12:] == 'lineups.json':
            matchname = file[:-13]
            home, away = matchname.split('_')
            filepath = os.path.join(base_dir, week, file)

            # Read file and get json data
            with open(filepath, 'r') as f:
                players_data = json.load(f)

            team_names = [home, away]
            # team_names = [teams[home], teams[away]]

            home_players = players_data['home']['players']
            away_players = players_data['away']['players']

            for i, team in enumerate([home_players, away_players]):

                is_home = True if i==0 else False

                for player in team:
                    stats = player['statistics']
                    stats['player'] = player['player']['name']
                    stats['team'] = team_names[0] if is_home else team_names[1]
                    stats['home'] = team_names[0]
                    stats['away'] = team_names[1]
                    stats['matchweek'] = week[-1]

                    data.append(stats)


df = pd.DataFrame(data)
df = df.fillna(0)

# Column names
df = df.rename(
    columns=
     {
         'onTargetScoringAttempt': 'ShotOnTarget',
         'shotOffTarget': 'ShotOffTarget'
         }
    )

# New metrics
df['TotalShots'] = (df['ShotOffTarget'] + df['ShotOnTarget'])


# p90 metrics
df['accuratePass_p90'] = (df['accuratePass'] / df['minutesPlayed']) * 90
df['TotalShots_p90'] = (df['TotalShots'] / df['minutesPlayed']) * 90
df['ShotOnTarget_p90'] = (df['ShotOnTarget'] / df['minutesPlayed']) * 90

# Replace NaNs with 0
df = df.fillna(0)

df.to_csv(f"{os.path.join('data', 'ligapro_2024_lineups.csv')}")
