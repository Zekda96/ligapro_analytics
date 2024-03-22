import json
import os

# Find all matchweek folders
base_dir = './data/matches'
matchweek_dirs = os.listdir(base_dir)
# Select only directories
matchweek_folders = [x for x in matchweek_dirs if os.path.isdir(os.path.join(base_dir,x))]

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
            with open(file, 'r') as f:
               data = json.load(f)

            groups = data['statistics'][0]['groups']


            # Create one row for each team for each match
            for team in ['home', 'away']:
                data = {'home': home,
                        'away': away,
                        'team': home if team=='home' else away,
                        'possesion': groups[0]['statisticsItems'][0][team],

                        # Shots
                        'total_shots': groups[1]['statisticsItems'][0][team],
                        'on_target': groups[1]['statisticsItems'][1][team],
                        'off_target': groups[1]['statisticsItems'][2][team],
                        'blocket_shots': groups[1]['statisticsItems'][3][team],
                        'shots_inside_box': groups[3]['statisticsItems'][4][team],
                        'shots_outside_box': groups[3]['statisticsItems'][5][team],
                        # Defensive
                        'gk_saves': groups[3]['statisticsItems'][6][team],
                        }
                final_data.append(data)

    


