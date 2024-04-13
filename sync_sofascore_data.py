import requests
import json
import time
import os
import pandas as pd
from pathlib import Path


def pull_sofascore_data(matches_data, data_name, mw_no, headers):
    """
    Input matches_data to pull using sofascore API.
    :param matches_data: List of dict with 'match_id', 'home' and 'away'
    :param data_name: Type of data between 'shotmap', 'statistics' or 'lineups'
    :param mw_no: Number of mw
    :param headers: headers for get request
    :return: Null
    """
    for i, event in enumerate(matches_data):

        file = f'{event["home"]}_{event["away"]}_{data}.json'
        mw_dir = os.path.join('data', 'matches', f'mw{mw_no}')
        fp = os.path.join(mw_dir, file)

        # Get match data
        resp = requests.get(f'https://api.sofascore.com/api/v1/event/{event["match_id"]}/{data_name}',
                                headers=headers)

        # Create folder if it doesn't exist
        Path(mw_dir).mkdir(parents=True, exist_ok=True)

        with open(fp, 'w') as f:
            json.dump(resp.json(), f)

        print(f'Mw{mw_no} Match {i + 1}: Saved {fp}')
        print(f'{time.localtime().tm_hour}h {time.localtime().tm_min}m {time.localtime().tm_sec}s')

        # After last match has been saved, stop waiting
        if i < len(matches_data) - 1:
            time.sleep(120)


def get_week_matches(mw, headers):
    url = f'https://api.sofascore.com/api/v1/unique-tournament/240/season/58043/events/round/{mw}'
    response = requests.get(url, headers=headers)

    matches = []
    for match in response.json()['events']:
        if match['status']['description'] == 'Ended':
            match_id = match['id']
            local = equipos[match['homeTeam']['shortName']]
            visitante = equipos[match['awayTeam']['shortName']]
            matches.append({'match_id': str(match_id), 'home': local, 'away': visitante})

    return matches


def get_current_mw(headers):
    url = f'https://api.sofascore.com/api/v1/unique-tournament/240/season/58043/rounds'
    response = requests.get(url, headers=headers)
    current_mw = response.json()['currentRound']['round']
    return current_mw


def read_db(data_name):
    base_dir = './data'
    lineups = os.path.join(base_dir, f'ligapro_2024_{data_name}.csv')

    df = pd.read_csv(lineups)
    return df


def get_incomplete_matchweeks(df, headers):
    # Unique matches in DB
    m = df.groupby('matchweek').count()
    # List of matchweeks in DB with 8 matches (no need to update)
    complete_matchweeks = m[m["home"] == 8].index.tolist()

    # Get current mw to get a list of all played matchweeks to date
    current_mw = get_current_mw(headers)
    all_matchweeks = list(range(1, current_mw+1))

    # List of all played matchweeks without 8 matches in DB
    incomplete_matchweeks = list(set(all_matchweeks) - set(complete_matchweeks))
    incomplete_matchweeks.sort()

    print(f'Incomplete MWs are: {incomplete_matchweeks}')

    # Return list of incomplete mws to update them
    return incomplete_matchweeks


headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,es;q=0.7',
    'cache-control': 'max-age=0',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.3'
}

equipos = {
    'Aucas': 'aucas',
    'Barcelona SC': 'barcelona',
    'Cuenca': 'cuenca',
    'Cumbayá FC': 'cumbaya',
    'Delfín': 'delfin',
    'El Nacional': 'nacional',
    'Emelec': 'emelec',
    'Imbabura': 'imbabura',
    'Independiente del Valle': 'independiente',
    'LDU': 'liga',
    'Libertad': 'libertad',
    'Macará': 'macara',
    'Mushuc Runa': 'mushuc-runa',
    'Orense': 'orense',
    'Universidad Católica': 'catolica',
    'Técnico': 'tecnico',

}

# data = 'statistics'
# data = 'shotmap'
# data = 'lineups'


if __name__ == '__main__':

    data_names = ['statistics', 'shotmap', 'lineups']

    for data in data_names:
        print(f'-------- {data} --------')
        df = read_db(data)

        db_matches = df[['home', 'away', 'matchweek']].drop_duplicates()

        incomplete_matchweeks = get_incomplete_matchweeks(db_matches, headers)

        for matchweek in incomplete_matchweeks:

            matches = get_week_matches(matchweek, headers)
            # Available matches from that week from Sofascore
            sofa_matches_week = pd.DataFrame(matches)
            print(f'MW{matchweek} - sofascore {data}')
            print(sofa_matches_week)

            # Matches from that week in DB
            db_matches_week = db_matches[db_matches['matchweek'] == matchweek][['home', 'away']]
            print(f'MW{matchweek} - DB {data}')
            print(db_matches_week)

            # Missing matches that are available in Sofascore
            missing_matches_id = pd.concat([sofa_matches_week, db_matches_week]).drop_duplicates('home', keep=False).to_dict('records')
            print(f'Available matches\' {data} to download are:')
            print(json.dumps(missing_matches_id, sort_keys=True, indent=1))

            pull_sofascore_data(missing_matches_id, data, matchweek, headers)
