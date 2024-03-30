import json
import pandas as pd
import os
from datetime import timedelta
from inflection import underscore

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
        # Get team names and filetype to only use desired files
        home, away, filetype = file.split('_')

        if filetype == 'shotmap.json':
            # Read 'statistics' file
            with open(os.path.join(base_dir, week, file), 'r') as f:
                shots = json.load(f)['shotmap']

            # Create one row for each shot

            for shot in shots:
                data = {'home': home,
                        'away': away,
                        'team': home if shot['isHome'] else away,
                        'matchweek': week[-1]
                        }
                for info in shot:
                    if info == 'player':
                        data['player'] = shot['player']['name']
                    # If stat is a dict, create one stat per each dict key
                    elif type(shot[info]) == dict:
                        for key in shot[info]:
                            # If stat is a dict, create one stat per each dict key
                            if type(shot[info][key]) == dict:
                                for key2 in shot[info][key]:
                                    data[f"{underscore(info)}_{key}_{key2}"] = shot[info][key][key2]
                                    print(shot[info][key][key2])

                            else:
                                data[f"{underscore(info)}_{key}"] = shot[info][key]
                            print(shot[info][key])
                    elif info != 'isHome':
                        data[underscore(info)] = shot[info]
                        print(shot[info])

                final_data.append(data)

df = pd.DataFrame(final_data).fillna(0)

df.to_csv(os.path.join('data', 'ligapro_2024_shots.csv'))
