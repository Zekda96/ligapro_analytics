import json
import pandas as pd
import os

# Find all matchweek folders
base_dir = './data/matches'
matchweek_dirs = os.listdir(base_dir)
# Select only directories
matchweek_folders = [x for x in matchweek_dirs if
                     os.path.isdir(os.path.join(base_dir, x))]

match_files = []
final_data = []
# Loop through folders
for week in matchweek_folders:
    match_files = os.listdir(os.path.join(base_dir, week))

    # Loop through files
    for file in match_files:
        # Get team names and filetype to only use 'statistics' files
        home, away, filetype = file.split('_')

        if filetype == 'statistics.json':
            # Read 'statistics' file
            with open(os.path.join(base_dir, week, file), 'r') as f:
                data = json.load(f)

            groups = data['statistics'][0]['groups']

            # Create one row for each team for each match
            for team in ['home', 'away']:
                data = {'home': home,
                        'away': away,
                        'team': home if team == 'home' else away,
                        'matchweek': week[-1]
                        }

                for stat_group in groups:
                    for stat in stat_group['statisticsItems']:
                        stat_name = stat['name'].lower().replace(' ', '_')
                        data[stat_name] = stat[team]
                final_data.append(data)

df = pd.DataFrame(final_data).fillna(0)

# -------------------------- Passes
# Split passes column
df['accurate_passes'] = df['accurate_passes'].str.split().str[0]
df.rename(columns={'accurate_passes': 'passes_completed'}, inplace=True)

# Change data type to numeric to be able to perform calculations
df['passes'] = pd.to_numeric(df['passes'])
df['passes_completed'] = pd.to_numeric(df['passes_completed'])

# Calculate new metric
df.insert(df.columns.get_loc('passes') + 2, 'passes_accuracy',
          round(df['passes_completed'] / df['passes'], 4))


def separate_percentages(stat, df):
    accurate = f'{stat}_completed'
    accuracy = f'{stat}_accuracy'

    # Split column into two
    df[[stat, accurate]] = df[stat].str.split().str[0].str.split('/',
                                                                 expand=True)

    # Move new column next to old relevant column
    column_to_move = df.pop(accurate)
    df.insert(df.columns.get_loc(stat) + 1, accurate, column_to_move)

    # Change data type to numeric to be able to perform calculations
    df[stat] = pd.to_numeric(df[stat])
    df[accurate] = pd.to_numeric(df[accurate])

    # Calculate new metric
    df.insert(df.columns.get_loc(stat) + 2, accuracy,
              round(df[stat] / df[accurate], 4))
    return df


df = separate_percentages('long_balls', df)
df = separate_percentages('dribbles', df)
df = separate_percentages('crosses', df)

df['ball_possession'] = df['ball_possession'].str.replace('%', '')

df.to_csv(os.path.join('data', 'ligapro_2024_statistics.csv'))
