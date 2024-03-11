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


def read_db():
    """
    Load data
    """
    fp = './data/ligapro_2024_lineups.csv'
    with open(fp, 'r') as f:
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

def order_data(by):
   
    df = read_db()

    select = ['player',
            'team',
            'minutesPlayed',
            'totalPass',
            'accuratePass',
            'TotalShots',
            'ShotOnTarget'
    ]

    where = df['player'] == 'Leonar Espinoza'
    group_by = ['team','player']
    order_by = by
    limit = 10

    if order_by not in select:
        select.append(order_by)

    # new_df = new_df[where]
    df = df[select]
    df = df.groupby(group_by).sum()
    df = df.sort_values(order_by, ascending=False)
    df = df.iloc[:limit, :]

    # Drop team and player name from index and add them as col
    df = df.reset_index()
    # Move team to another col for final table aesthetics
    df.insert(1, 'team', df.pop('team'))
    # Start index from 1 so it is a ranking on the table (1-10)
    df.index += 1

    # Add percentages
    # - Pass Accuracy
    pass_accuracy = (df['accuratePass'] / df['totalPass'])
    df.insert(5, 'PassAccuracy', pass_accuracy)

    # - Shot on Target %
    shot_on_target = (df['ShotOnTarget'] / df['TotalShots'])
    df.insert(len(df.columns), 'SoT_percent', shot_on_target)

    # Replace NaNs with 0
    df = df.fillna(0)

    # Change team names to logo images filepaths for plottable
    df['team'] = df['team'].apply(team_name_to_path)

    return df

def plot_table(df, by, output_fn):
    cmap = LinearSegmentedColormap.from_list(
        name="bugw", colors=["#ffffff", "#f2fbd2", "#c9ecb4", "#93d3ab", "#35b0ab"], N=256
    )

    cmap_test = LinearSegmentedColormap.from_list(
        # name="bugw", colors=["#ffffff", "#f2fbd2", "#c9ecb4", "#93d3ab", "#35b0ab"], N=256
        name="bugw", colors=["#FF9C9C", "#FFFFFF", "#53CD76"], N=256
    )

    cmap1 = LinearSegmentedColormap.from_list(
        name="gray", colors=[
            "#f2f2f4",
            "#f2f2f4",
            ], N=256
    )

    percents_cmap = matplotlib.colormaps.get_cmap('RdYlGn')

    data_width = 0.6
    percent_width = 1
    col_defs = (
        [
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
                name='team',
                title='',
                plot_fn=image,
                width=1,
                # border='left',
                ),

            ColumnDefinition(
                name='minutesPlayed',
                title='Minutos',
                formatter="{:.0f}",
                width=data_width,
                # border='left',
                ),

            ColumnDefinition(
                name='totalPass',
                title='Pases',
                formatter="{:.0f}",
                group="Pases",
                width=data_width,
                # border='left',
                ),

            ColumnDefinition(
                name='accuratePass',
                title='Completos',
                formatter="{:.0f}",
                group="Pases",
                width=data_width,
                # border='left',
                ),


            ColumnDefinition(
                name='PassAccuracy',
                title='Precisión',
                formatter=decimal_to_percent,
                group="Pases",
                cmap=cmap_test,
                width=percent_width,            
                textprops= {"bbox": {"boxstyle": "circle", "pad": 0.35}},
                # border='left',
                ),

            ColumnDefinition(
                name='TotalShots',
                title='Total',
                formatter="{:.0f}",
                group="Disparos",
                width=data_width,
                # cmap=cmap1,
                # border='left',
                ),

            ColumnDefinition(
                name='ShotOnTarget',
                title='Al Arco',
                formatter="{:.0f}",
                group="Disparos",
                width=data_width,
                # border='left',
                ),

            ColumnDefinition(
                name='SoT_percent',
                title='Precisión',
                formatter=decimal_to_percent,
                group="Disparos",
                cmap=cmap_test,
                textprops= {"bbox": {"boxstyle": "circle", "pad": 0.35}},
                width=percent_width,
                ),
        ] 
        + [
            ColumnDefinition(
                name=by,
                cmap=cmap1,
                )
        ]
    )

    # col_defs.


    # Table
    fig, ax = plt.subplots(figsize=(13, 8))
    
    bg_color = '#faf9f4'
    # fig.patch.set_facecolor('red')
    ax.set_facecolor(bg_color)

    tab = Table(df,
                column_definitions=col_defs,
                # cell_kw={'facecolor': 'red'}
                textprops={
                    "ha": "center",
                    },
                )

    fig.suptitle('Top 10 Jugadores con mas disparos', fontsize=17)
    ax.set_title('LigaPro 2024 - 2 Fechas')

    fig.savefig(f"images/{output_fn}", facecolor=ax.get_facecolor(), dpi=200)


if __name__ == "__main__":

    top_stat = 'TotalShots'
    filename = 'total_shots.png'
    df = order_data(top_stat)
    plot_table(df, top_stat, filename)

    top_stat = 'totalPass'
    filename = 'total_passes.png'
    df = order_data(top_stat)
    plot_table(df, top_stat, filename)

