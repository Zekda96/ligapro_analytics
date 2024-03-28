# Data 
import json
import pandas as pd
import os

# Plot
from plottable import ColumnDefinition, Table
from plottable.formatters import decimal_to_percent
from plottable.plots import *

import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import Pitch

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

    limit = 16

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


def add_pitch_stats(ax, df, stats):

    stat_names = [
        'Goles',
        'Posesion',
        'Tiros',
        'Al Arco',
        'Pases',
    ]

    dist = 8
    n = len(stat_names) - 1
    border = (80 - n*dist)/2

    data_diff = 16

    tags_size = 14
    for i, stat in enumerate(stat_names):
        ax.text(x=60, y=(border + dist*i), s=stat, size=tags_size, ha='center', va='center')

    # Home
    ax.text(x=60-data_diff, y=(border + dist*1), s=f'{df["home"][stats[0]]}%',
            size=tags_size, ha='center', va='center'
            )
    # Away
    ax.text(x=60+data_diff, y=(border + dist*1), s=f'{df["away"][stats[0]]}%',
            size=tags_size, ha='center', va='center'
            )


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
                group="Disparos",
                width=data_width,
                cmap=cmap1,
                ),

            ColumnDefinition(
                name='ShotOnTarget',
                title='Al Arco',
                formatter="{:.0f}",
                group="Disparos",
                width=data_width,
                ),

            ColumnDefinition(
                name='SoT_percent',
                title='Precisión',
                formatter=decimal_to_percent,
                group="Disparos",
                cmap=cmap_test,
                textprops= {"bbox": {"boxstyle": "circle", "pad": 0.05}},
                width=percent_width,
                )
        ]

    for stat in stats_col_defs:
        col_defs.append(stat)

    return col_defs


if __name__ == "__main__":
    df = read_db('ligapro_2024_lineups.csv', )

    home = 'aucas'
    away = 'nacional'

    match = [home, away]

    df_home_pass = order_data(df, match, home, 'pass')
    df_away_pass = order_data(df, match, away, 'pass')

    df_home_shot = order_data(df, match, home, 'shot')
    df_away_shot = order_data(df, match, away, 'shot')

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

    # --------------------------------------- Add Tables
    # ------------------ Passes

    # Home
    col_defs = get_col_defs('pass')
    tab_home = Table(df_home_pass,
                     column_definitions=col_defs,
                     ax=axs_home[0],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )
    
    # Away
    tab_away = Table(df_away_pass,
                     column_definitions=col_defs,
                     ax=axs_away[0],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )

    # ------------------ Passes

    # Home
    col_defs = get_col_defs('shot')
    tab_home = Table(df_home_shot,
                     column_definitions=col_defs,
                     ax=axs_home[1],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )
    
    # # Away
    tab_away = Table(df_away_shot,
                     column_definitions=col_defs,
                     ax=axs_away[1],
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )
    add_labels(fig, home, away)

    # --------------------- Add team statistics
    df = read_db('ligapro_2024_statistics.csv')

    def get_team_stats(df: pd.DataFrame, stats: list, home, away):
        df = df[(df['home'] == home) & (df['away'] == away)]
        data = {'home': {},
                'away': {}}

        for stat in stats:
            data['home'][stat] = df[stat].iloc[0]
            print(df[stat].iloc[0])
            data['away'][stat] = df[stat].iloc[1]

        return data

    stats = ['ball_possession']
    df_stats = get_team_stats(df, stats, home, away)

    add_pitch_stats(ax_pitch, df_stats, stats)

    fig.savefig(f"images/match_report.png",
                # bbox_inches='tight',
                dpi=250)
