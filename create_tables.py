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
        'macara': 'ma',
        'aucas': 'au',
        'imbabura': 'im',
        'nacional': 'na',
        'liga': 'ldu',
        'barcelona': 'bsc',
        'emelec': 'cse',
        'delfin': 'de',
        'tecnico': 'tu'
    }

    fp = os.path.join(img_path, f'{teams[fn]}.png')
    return fp

def order_data():
   
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
    order_by = 'TotalShots'
    limit = 10

    if order_by not in select:
        select.append(order_by)

    # new_df = new_df[where]
    df = df[select]
    df = df.groupby(group_by).sum()
    df = df.sort_values(order_by, ascending=False)
    df = df.iloc[:limit, :]

    df = df.reset_index(level=0)

    # Add percentages
    # - Pass Accuracy
    pass_accuracy = (df['accuratePass'] / df['totalPass'])
    df.insert(4, 'PassAccuracy', pass_accuracy)

    # - Shot on Target %
    shot_on_target = (df['ShotOnTarget'] / df['TotalShots'])
    df.insert(len(df.columns), 'SoT_percent', shot_on_target)

    # Replace NaNs with 0
    df = df.fillna(0)

    # Change team names to logo images filepaths for plottable
    df['team'] = df['team'].apply(team_name_to_path)

    return df

def plot_table(df):
    cmap = LinearSegmentedColormap.from_list(
        name="bugw", colors=["#ffffff", "#f2fbd2", "#c9ecb4", "#93d3ab", "#35b0ab"], N=256
    )

    col_defs = [

        ColumnDefinition(
            name='player',
            title='',
            ),

        ColumnDefinition(
            name='team',
            title='',
            plot_fn=image,
            ),

        ColumnDefinition(
            name='minutesPlayed',
            title='Minutos',
            formatter="{:.0f}",
            ),

        ColumnDefinition(
            name='totalPass',
            title='Pases',
            formatter="{:.0f}",
            group="Pases",
            ),

        ColumnDefinition(
            name='accuratePass',
            title='Completos',
            formatter="{:.0f}",
            group="Pases",
            ),


        ColumnDefinition(
            name='PassAccuracy',
            title='Precisión %',
            formatter=decimal_to_percent,
            group="Pases",
            cmap=cmap,
            ),

        ColumnDefinition(
            name='TotalShots',
            title='Tiros',
            formatter="{:.0f}",
            group="Disparos",
            ),

        ColumnDefinition(
            name='ShotOnTarget',
            title='Al Arco',
            formatter="{:.0f}",
            group="Disparos",
            ),

        ColumnDefinition(
            name='SoT_percent',
            title='Precisión %',
            formatter=decimal_to_percent,
            group="Disparos",
            cmap=cmap,
            ),
        ]

    # Table
    fig, ax = plt.subplots(figsize=(13, 8))

    tab = Table(df,
                column_definitions=col_defs,)

    fig.savefig("images/top_table.png", facecolor=ax.get_facecolor(), dpi=200)


if __name__ == "__main__":
    df = order_data()
    plot_table(df)