# Data 
import json
import pandas as pd
import os

# Plot
from plottable import ColumnDefinition, Table
from plottable.formatters import decimal_to_percent
from plottable.plots import *

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import Pitch, Standardizer, FontManager

import math


def read_db(file):
    """
    Load data
    """
    fp = os.path.join('data', file)
    with open(fp, 'r', encoding="utf8") as f:
        df = pd.read_csv(f)

    return df


def team_name_to_path(fn):
    """
    Replace team name with path to logo for plottable
    """

    img_path = './data/logos'
    teams = {
        'aucas': 'au',
        'imbabura': 'im',
        'barcelona': 'bsc',
        'emelec': 'cse',
        'delfin': 'de',
        'tecnico': 'tu',
        'cumbaya': 'cu',
        'cuenca': 'dc',
        'independiente': 'idv',
        'imbabura': 'im',
        'libertad': 'lb',
        'liga': 'ldu',
        'macara': 'ma',
        'mushuc-runa': 'mu',
        'nacional': 'na',
        'orense': 'or',
        'catolica': 'uc',
    }

    fp = os.path.join(img_path, f'{teams[fn]}.png')
    return fp


def order_data(df, match_teams, team, stat_type):
    select = [
        'player', 'team', 'minutesPlayed'
    ]

    if stat_type == 'pass':
        select.append('totalPass')
        select.append('accuratePass')

        order_by = 'totalPass'


    elif stat_type == 'shot':
        select.append('TotalShots')
        select.append('ShotOnTarget')

        order_by = 'TotalShots'

    home = match_teams[0]
    away = match_teams[1]

    where = (
        (df['home'] == home)
        & (df['away'] == away)
        & (df['minutesPlayed'] > 0)
        & (df['team'] == team)
        )

    limit = 5

    df = df[where]
    df = df[select]
    df = df.sort_values(order_by, ascending=False, ignore_index=True)
    df = df.iloc[:limit, :]

    # Start index from 1 so it is a ranking on the table (1-16)
    df.index += 1

    # Add percentages
    if stat_type == 'pass':
        # Pass Accuracy
        pass_accuracy = (df['accuratePass'] / df['totalPass'])
        df.insert(5, 'PassAccuracy', pass_accuracy)
    elif stat_type == 'shot':
        # Shot on Target %
        shot_on_target = (df['ShotOnTarget'] / df['TotalShots'])
        df.insert(len(df.columns), 'SoT_percent', shot_on_target)

    # Replace NaNs with 0
    df = df.fillna(0)

    df = df.drop(['team'], axis=1)

    return df


def add_labels(fig, home_team, away_team):

    teams = {'liga': 'LDU',
         'emelec': 'Emelec',
         'barcelona': 'Barcelona',
         'delfin': 'Delfin',
         'catolica': 'U. Catolica',
         'nacional': 'El Nacional',
         'macara': 'Macara',
         'imbabura': 'Imbabura',
         'cuenca': 'D. Cuenca',
         'aucas': 'Aucas',
         'independiente': 'IDV',
         'mushuc-runa': 'Mushuc Runa',
         'orense': 'Orense',
         'cumbaya': 'Cumbaya',
         'libertad': 'Libertad',
         'tecnico': 'Tecnico U.'
         }
    
    # ------------------- Labels
    ax_title.text(x=0.5, y=0.9,
                s=f'{teams[home_team]} vs. {teams[away_team]}',
                  size=40,
                  ha='center',
                  va='top'
                  )
    
    ax_title.text(x=0.5, y=0.5,
                s=f'Reporte de Partido - Liga Pro 2024',
                size=25,
                ha='center',
                va='top'
                )


def get_team_stats(df: pd.DataFrame, stats: dict, home, away):
    df = df[(df['home'] == home) & (df['away'] == away)]
    data = {'home': {},
            'away': {}}

    for stat in stats.values():
        if type(stat) == list:
            data['home']['goals'] = stat[0]
            data['away']['goals'] = stat[1]
        else:
            data['home'][stat] = df[stat].iloc[0]
            data['away'][stat] = df[stat].iloc[1]

    data = pd.DataFrame(data).transpose()
    return data


def get_goals(df, home: str, away: str):
    df = df[df['shot_type'] == 'goal']
    df = df[(df['home'] == home) & (df['away'] == away)]
    home_goals = len(df[df['team'] == home])
    away_goals = len(df[df['team'] == away])

    return [home_goals, away_goals]


def add_pitch_stats(ax, home_team: str, away_team: str):
    """
    Func to add team stats on pitch.
    :param ax: Axis containing pitch.
    :param home_team: Name of home team.
    :param away_team: Name of away team
    :return:
    """

    df_stats = read_db('ligapro_2024_statistics.csv')
    goals = get_goals(read_db('ligapro_2024_shotmap.csv'), home_team, away_team)

    # Stats to show on pitch. Display name and col name on df
    stats = {
        'Goles': goals,
        'Posesion': 'ball_possession',
        'Remates': 'total_shots',
        'Al Arco': 'shots_on_target',
        'Pases': 'passes_completed'
    }

    df = get_team_stats(df_stats, stats, home_team, away_team)

    # Name to display of each stat
    stat_names = list(stats.keys())
    dist = 8
    n = len(stat_names) - 1
    border = (80 - n*dist)/2

    data_diff = 16

    tags_size = 14
    for i, stat in enumerate(df.columns):
        # Write stat name
        ax.text(x=60, y=(border + dist*i),
                s=stat_names[i],
                size=tags_size,
                ha='center', va='center',
                # fontproperties=robotto_bold.prop
                )

        # Add Home value
        text = f"{df[stat]['home']}"
        # Add '%' for possession stat
        text = text + '%' if stat == 'ball_possession' else text
        ax.text(x=60-data_diff, y=(border + dist*i),
                s=text,
                size=tags_size,
                ha='center', va='center'
                )
        # Add Away value
        text = f"{df[stat]['away']}"
        # Add '%' for possession stat
        text = text + '%' if stat == 'ball_possession' else text

        ax.text(x=60+data_diff, y=(border + dist*i),
                s=text,
                size=tags_size,
                ha='center', va='center'
                )

        # Add bar
        stat1_val = df[stat]['home']
        stat2_val = df[stat]['away']
        total = stat1_val + stat2_val

        h_padding = tags_size/2.4
        v_offset = tags_size/3.5
        bar_spacing = 1

        bar_total_width = data_diff * 2 + (2 * h_padding)

        stat1_width = bar_total_width * (stat1_val/total)
        stat2_width = bar_total_width * (stat2_val/total)

        left_coordinate = 60 - data_diff - h_padding
        middle_coordinate = left_coordinate + stat1_width

        rect1 = Rectangle((left_coordinate, border+dist*i-v_offset),
                          stat1_width,
                          dist-bar_spacing,
                          # color='blue',
                          fc='red',
                          alpha=0.1,
                          lw=2)

        rect2 = Rectangle((middle_coordinate, border + dist * i - v_offset),
                          stat2_width,
                          dist-bar_spacing,
                          # color='blue',
                          fc='blue',
                          alpha=0.1,
                          lw=2,
                          zorder=10)
        ax.add_patch(rect1)
        ax.add_patch(rect2)


def add_pitch_shots(ax_pitch, ax, home_team, away_team):

    """
    Func to add team stats on pitch.
    :param ax: Axis containing pitch.
    :param home_team: Name of home team.
    :param away_team: Name of away team
    :return:
    """
    # Standardizer
    standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')
    df = read_db('ligapro_2024_shotmap.csv')

    df.rename(columns={'player_coordinates_x': 'x',
                       'player_coordinates_y': 'y'},
              inplace=True)

    df = df[(df['home'] == home_team) & (df['away'] == away_team)]

    # Invert away team shot coordinates
    df.loc[df['team'] == away_team, 'x'] = 100 - df.loc[df['team'] == away_team, 'x']
    df.loc[df['team'] == away_team, 'y'] = 100 - df.loc[df['team'] == away_team, 'y']

    df.loc[:, 'x'], df.loc[:, 'y'] = standard.transform(df['x'], df['y'])

    mask = df['shot_type'] == 'goal'
    goals_df, shots_df = df[mask], df[~mask]

    target_mask = shots_df['shot_type'] == 'save'
    target_df, miss_df = shots_df[target_mask], shots_df[~target_mask]

    target = ax_pitch.scatter(target_df.x, target_df.y, ax=ax,
                             facecolor='red',
                             edgecolor='red',
                              zorder=1,
                              )

    miss = ax_pitch.scatter(miss_df.x, miss_df.y, ax=ax,
                             facecolor='white',
                             edgecolor='red')

    goals = ax_pitch.scatter(goals_df.x, goals_df.y, ax=ax,
                             facecolor='red',
                             marker='*',
                             edgecolor='red')



def get_col_defs(stat_type):
       
    cmap_test = LinearSegmentedColormap.from_list(
        # name="bugw", colors=["#ffffff", "#f2fbd2", "#c9ecb4", "#93d3ab", "#35b0ab"], N=256
        name="bugw", colors=["#FF9C9C", "#FFFFFF", "#53CD76"], N=256
    )

    cmap1 = LinearSegmentedColormap.from_list(
        name="gray",
        colors=[
            "#f2f2f4",
            "#f2f2f4",
            ], N=256
    )

    data_width = 0.6
    percent_width = 1

    col_defs = [
        ColumnDefinition(
            name='index',
            title='',
            width=0.3,
            ),

        ColumnDefinition(
            name='player',
            title='',
            width=1.8,
            ),

        ColumnDefinition(
            name='minutesPlayed',
            title='Minutos',
            formatter="{:.0f}",
            width=data_width,
            )
        ]

    if stat_type == 'pass':
        stats_col_defs = [
        ColumnDefinition(
            name='totalPass',
            title='Total',
            formatter="{:.0f}",
            group="Pases",
            width=data_width,
            cmap=cmap1,
            ),  

        ColumnDefinition(
            name='accuratePass',
            title='Completos',
            formatter="{:.0f}",
            group="Pases",
            width=data_width,
            ),

        ColumnDefinition(
            name='PassAccuracy',
            title='Precisión',
            formatter=decimal_to_percent,
            group="Pases",
            cmap=cmap_test,
            width=percent_width,            
            textprops= {"bbox": {"boxstyle": "circle", "pad": 0.05}},
            ) 
        ] 

            
    elif stat_type == 'shot':
        stats_col_defs = [
            ColumnDefinition(
                name='TotalShots',
                title='Total',
                formatter="{:.0f}",
                group="Remates",
                width=data_width,
                cmap=cmap1,
                ),

            ColumnDefinition(
                name='ShotOnTarget',
                title='Al Arco',
                formatter="{:.0f}",
                group="Remates",
                width=data_width,
                ),

            ColumnDefinition(
                name='SoT_percent',
                title='Precisión',
                formatter=decimal_to_percent,
                group="Remates",
                cmap=cmap_test,
                textprops= {"bbox": {"boxstyle": "circle", "pad": 0.05}},
                width=percent_width,
                )
        ]

    for stat in stats_col_defs:
        col_defs.append(stat)

    return col_defs


def add_tables(dfs: dict, axs: dict):
    # ------------------ Passes

    col_defs = get_col_defs('pass')
    # Home
    tab_home = Table(dfs['pass']['home'],
                     column_definitions=col_defs,
                     ax=axs['home'][0],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )

    # Away
    tab_away = Table(dfs['pass']['away'],
                     column_definitions=col_defs,
                     ax=axs['away'][0],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )

    # ------------------ Shots

    col_defs = get_col_defs('shot')
    # Home
    tab_home = Table(dfs['shot']['home'],
                     column_definitions=col_defs,
                     ax=axs['home'][1],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )

    # # Away
    tab_away = Table(dfs['shot']['away'],
                     column_definitions=col_defs,
                     ax=axs['away'][1],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )


if __name__ == "__main__":
    URL5 = (
        'https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
        'RobotoSlab%5Bwght%5D.ttf')
    robotto_bold = FontManager(URL5)

    URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
    robotto_thin = FontManager(URL4)

    df = read_db('ligapro_2024_lineups.csv', )

    home = 'emelec'
    away = 'cumbaya'

    match = [home, away]

    tables_dfs = {'pass': {'home': order_data(df, match, home, 'pass'),
                           'away': order_data(df, match, away, 'pass')
                           },
                  'shot': {'home': order_data(df, match, home, 'shot'),
                           'away': order_data(df, match, away, 'shot')
                           }
                  }

    # --------------------------------------- Figure
    bg_color = '#faf9f4'
    size = 12
    fig = plt.figure(layout='constrained', figsize=(size, size * math.sqrt(2)), dpi=250)
    fig.patch.set_facecolor(bg_color)

    subfigs = fig.subfigures(4, 1,
                         wspace=0.01,
                         hspace=0.01,
                         height_ratios=[0.1, 0.3 , 0.6, 0.05]
                         )

    ax_title = subfigs[0].subplots(1, 1)
    ax_title.axis('off')

    ax_pitch = subfigs[1].subplots(1, 1)
    axs_tables = subfigs[2].subplots(2,2)

    ax_annotate = subfigs[3].subplots(1, 1)
    ax_annotate.axis('off')

    axs_home = [axs_tables[0][0], axs_tables[1][0]]
    axs_away = [axs_tables[0][1], axs_tables[1][1]]

    # --------------------------------------- Add Pitch
    pitch = Pitch()
    pitch.draw(ax=ax_pitch)

    # --------------------- Add shots to Pitch
    add_pitch_shots(pitch, ax_pitch, home, away)

    # --------------------- Add team statistics to Pitch
    add_pitch_stats(ax_pitch, home, away)

    # ---------------------- Add Tables with player data
    add_tables(tables_dfs, {'home': axs_home, 'away': axs_away})

    add_labels(fig, home, away)

    fig.savefig(f"images/match_report.png",
                # bbox_inches='tight',
                dpi=250)
