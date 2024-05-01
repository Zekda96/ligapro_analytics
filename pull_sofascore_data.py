import PySimpleGUI as sg
import pandas as pd
import json
import os
from inflection import underscore
from sqlalchemy import create_engine
from datetime import datetime


# equipos = {
#     'Aucas': 'aucas',
#     'Barcelona SC': 'barcelona',
#     'Cuenca': 'cuenca',
#     'Cumbayá FC': 'cumbaya',
#     'Delfín': 'delfin',
#     'El Nacional': 'nacional',
#     'Emelec': 'emelec',
#     'Imbabura': 'imbabura',
#     'Independiente del Valle': 'independiente',
#     'LDU': 'liga',
#     'Libertad': 'libertad',
#     'Macará': 'macara',
#     'Mushuc Runa': 'mushuc-runa',
#     'Orense': 'orense',
#     'Universidad Católica': 'catolica',
#     'Técnico': 'tecnico',
# }


def parse_json_lineups(lineups_data, home, away, week):
    players_data = json.loads(lineups_data)
    team_names = [home, away]

    home_players = players_data['home']['players']
    away_players = players_data['away']['players']

    data = []
    for i, team in enumerate([home_players, away_players]):

        is_home = True if i == 0 else False

        for player in team:
            stats = player['statistics']
            stats['player'] = player['player']['name']
            stats['team'] = team_names[0] if is_home else team_names[1]
            stats['home'] = team_names[0]
            stats['away'] = team_names[1]
            stats['matchweek'] = week

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

    df.loc[:, 'ratingVersions'] = df['ratingVersions'].astype('string')

    ####
    # df_lineups = df[['team', 'TotalShots', 'ShotOnTarget',
    #                  'goals', 'ShotOffTarget', 'blockedScoringAttempt']].groupby('team').sum()

    return df


def parse_json_statistics(data, home, away, week):
    final_data = []

    data = json.loads(data)
    groups = data['statistics'][0]['groups']

    # Create one row for each team for each match
    for team in ['home', 'away']:
        data = {'home': home,
                'away': away,
                'team': home if team == 'home' else away,
                'matchweek': week
                }

        for stat_group in groups:
            for stat in stat_group['statisticsItems']:
                stat_name = stat['name'].lower().replace(' ', '_')
                data[stat_name] = stat[team + 'Value']
        final_data.append(data)

    df = pd.DataFrame(final_data).fillna(0)

    # -------------------------- Passes
    # # Split passes column
    df.rename(columns={'accurate_passes': 'passes_completed'}, inplace=True)

    # # Calculate new metric
    df.insert(df.columns.get_loc('passes') + 2, 'passes_accuracy',
              round(df['passes_completed'] / df['passes'], 4))

    # df_statistics = df[['team', 'total_shots', 'shots_on_target',
    #                     'ball_possession', 'passes', 'passes_completed',
    #                     'passes_accuracy']].groupby('team').sum()

    return df


def parse_json_shotmap(shots, home, away, week):
    shots = json.loads(shots)['shotmap']
    final_data = []

    # Create one row for each shot

    for shot in shots:
        data = {'home': home,
                'away': away,
                'team': home if shot['isHome'] else away,
                'matchweek': week
                }
        for info in shot:
            if info == 'player':
                data['player'] = shot['player']['name']
            # If stat is a dict, create one stat per each dict key
            elif isinstance(shot[info], dict):
                for key in shot[info]:
                    # If stat is a dict, create one stat per each dict key
                    if isinstance(shot[info][key], dict):
                        for key2 in shot[info][key]:
                            data[f"{underscore(info)}_{key}_{key2}"] = shot[info][key][key2]
                            # print(shot[info][key][key2])

                    else:
                        data[f"{underscore(info)}_{key}"] = shot[info][key]
                    # print(shot[info][key])
            elif info != 'isHome':
                data[underscore(info)] = shot[info]
                # print(shot[info])

        final_data.append(data)

    df = pd.DataFrame(final_data).fillna(0)

    # # Goals
    # df1 = df[['team', 'shot_type']][df['shot_type'] == 'goal'].groupby('team').count()
    # df1 = df1.rename(columns={"shot_type": "goals"})
    #
    # # On Target
    # df2 = df[['team', 'shot_type']][df['shot_type'].isin(['save', 'goal'])].groupby('team').count()
    # df2 = df2.rename(columns={"shot_type": "ShotsOnTarget"})
    #
    # # Shots
    # df3 = df[['team', 'shot_type']].groupby('team').count()
    # df3 = df3.rename(columns={"shot_type": "Shots"})
    #
    # # Join df2 and df3
    # df_shotmap = df3.join(df2, how='outer')
    #
    # # Join df and df1
    # df_shotmap = df_shotmap.join(df1, how='outer')
    #
    # df_shotmap = df_shotmap.fillna(0)

    return df


def test_sot(df_line, df_stats, df_shots):
    df_line = df_line[['team', 'ShotOnTarget']].groupby('team').sum()
    df_stats = df_stats[["team", "shots_on_target"]].groupby('team').sum()

    df_shots = df_shots[['team', 'shot_type']]
    df_shots = df_shots[df_shots['shot_type'].isin(['save', 'goal'])].groupby('team').count()
    df_shots = df_shots.rename(columns={"shot_type": "ShotsOnTarget"})

    sot1 = df_line['ShotOnTarget'].astype(int)
    sot2 = df_stats['shots_on_target'].astype(int)
    sot3 = df_shots['ShotsOnTarget'].astype(int)

    t1 = sot1.equals(sot2)
    t2 = sot1.equals(sot3)
    t3 = sot2.equals(sot3)

    val = t1 & t2 & t3
    return val


def test_total_shots(df_statistics, df_shotmap):
    df_shotmap = df_shotmap[['team', 'shot_type']].groupby('team').count()
    df_shotmap = df_shotmap.rename(columns={"shot_type": "Shots"})

    df_statistics = df_statistics[['team', 'total_shots']].groupby('team').sum()

    shots1 = df_shotmap['Shots'].astype(int)
    shots2 = df_statistics['total_shots'].astype(int)

    return shots1.equals(shots2)


def test_goals(df_lineups, df_shotmap):
    df_lineups = df_lineups[['team', 'goals']].groupby('team').sum()

    df_shotmap = df_shotmap[['team', 'shot_type']]
    df_shotmap = df_shotmap[df_shotmap['shot_type'] == 'goal'].groupby('team').count()
    df_shotmap = df_shotmap.rename(columns={"shot_type": "goals"})

    teams1 = df_lineups.index.to_list()
    teams2 = df_shotmap.index.to_list() #possibly incomplete if team didnt score

    missing_team = list(set(teams1) - set(teams2))

    if missing_team:
        df_shotmap.loc[missing_team[0]] = 0
        df_shotmap = df_shotmap.sort_index()

    goals1 = df_lineups['goals'].astype(int)
    goals2 = df_shotmap['goals'].astype(int)

    return goals1.equals(goals2)


def parse_json_data(raw_data, home, away, mw):
    df_lineups = parse_json_lineups(raw_data['lineups'], home, away, mw)
    df_statistics = parse_json_statistics(raw_data['statistics'], home, away, mw)
    df_shotmap = parse_json_shotmap(raw_data['shotmap'], home, away, mw)

    dfs = {'lineups': df_lineups,
           'statistics': df_statistics,
           'shotmap': df_shotmap
           }
    return dfs


def quality_check(data):
    df_lineups = data['lineups']
    df_statistics = data['statistics']
    df_shotmap = data['shotmap']

    test1 = test_sot(df_lineups, df_statistics, df_shotmap)
    test2 = test_total_shots(df_statistics, df_shotmap)
    test3 = test_goals(df_lineups, df_shotmap)
    test4 = df_statistics['ball_possession'].values.sum() == 100

    return_val = [f"SoT: {test1}", f"Total Shots: {test2}", f"Goals: {test3}", f"Possession: {test4}"]
    return return_val


def main():
    # GUI
    sg.theme('SystemDefault')
    #print(sg.Text.fonts_installed_list())

    t = sg.Text
    i = sg.Input
    fb = sg.FileBrowse

    w1 = 18
    w2 = 45

    base_font = ('Arial', 13)
    results_font = ('Arial', 14)
    results_w = 65

    rt = 'Results will show here'  # Results Text

    # 1. Define the window's contents

    # Create columns to show results
    column_lineups = [
        [t('Lineups')],
        [sg.Multiline(s=(results_w, 3), k='-LINEUPS-', default_text=rt, font=results_font)]
    ]

    column_statistics = [
        [t('Statistics')],
        [sg.Multiline(s=(results_w, 3), k='-STATISTICS-', default_text=rt, font=results_font)]
    ]

    column_shotmap = [
        [t('Shotmap')],
        [sg.Multiline(s=(results_w, 3), k='-SHOTMAP-', default_text=rt, font=results_font)]
    ]

    # Window Layout with columns at the end
    layout = [
        [t('Please paste Sofascore match')],
        [t('Url:'), i(s=(60, 1), enable_events=True, k="-URL-")],
        [t('Home team'), i(s=(30, 1), enable_events=True, k="-HOME-")],
        [t('Away team'), i(s=(30, 1), enable_events=True, k="-AWAY-")],
        [t('Matchweek'), i(s=(30, 1), enable_events=True, k="-MW-")],

        [t('')],
        [sg.Button('Get urls')],
        [t('')],
        [sg.Column(column_lineups), sg.Column(column_statistics)],
        [sg.Column(column_shotmap)],
        [t('')],
        [sg.Button('Load')],
        [sg.Multiline(s=(results_w, 5), k='-CHECKS-', default_text=rt, font=results_font)],
        [sg.Button('Save')],

    ]

    # 2. Create the window
    window = sg.Window('Pull Sofascore match data', layout, font=base_font)

    # 3. Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        # Once files have been chosen, submit for scoring
        if event == 'Get urls':
            match_id = values["-URL-"][-8:]
            url = f'https://api.sofascore.com/api/v1/event/{match_id}/'

            url_lineups = f'{url}lineups'
            url_statistics = f'{url}statistics'
            url_shotmap = f'{url}shotmap'

            print(event, url_lineups)
            print(event, url_statistics)
            print(event, url_shotmap)

            # Show results on textbox
            window['-LINEUPS-'].update(url_lineups)
            window['-STATISTICS-'].update(url_statistics)
            window['-SHOTMAP-'].update(url_shotmap)

        if event == 'Load':
            raw_data = {}
            home = values["-HOME-"]
            away = values["-AWAY-"]
            mw = values["-MW-"]

            for data in ['lineups', 'statistics', 'shotmap']:
                vals = values[f'-{data.swapcase()}-']
                raw_data[data] = vals
                # Perform quality check

            dataframes = parse_json_data(raw_data, home, away, mw)
            checks = quality_check(dataframes)
            window['-CHECKS-'].update("\n".join(checks))

        if event == 'Save':
            # Save data in file and in SQL db
            db_name = 'data/liga_pro_ecuador.db'
            db_engine = create_engine(f'sqlite:///{db_name}')

            for data in ['lineups', 'statistics', 'shotmap']:
                # home = values["-HOME-"]
                # away = values["-AWAY-"]
                # mw = values["-MW-"]

                file = f'{home}_{away}_{data}.json'
                mw_dir = os.path.join('data', 'matches', f'mw{mw}')
                fp = os.path.join(mw_dir, file)

                with open(fp, 'w', encoding="utf-8") as f:
                    f.write(raw_data[data])

                print(f'{data} file saved at {fp}')

                # Process data and insert into SQLite db
                date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                date_object = pd.to_datetime(date_string)
                dataframes[data].loc[:, 'timestamp'] = date_object

                dataframes[data].to_sql(data, con=db_engine, if_exists='append', index=False)
                print(f'{data} df saved at {db_name}.{data}')


        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

    # 4. Remove from the screen
    window.close()


if __name__ == "__main__":
    main()
