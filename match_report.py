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


def order_data(df, match_teams, team):
   
    select = ['player',
            'team',
            'minutesPlayed',
            'totalPass',
            'accuratePass',
            'TotalShots',
            'ShotOnTarget'
    ]

    home = match_teams[0]
    away = match_teams[1]

    where = (
        (df['home'] == home)
        & (df['away'] == away)
        & (df['minutesPlayed'] > 0)
        & (df['team'] == team)
        )

    
    # group_by = ['team','player']
    order_by = 'totalPass'
    limit = 16

    if order_by not in select:
        select.append(order_by)


    df = df[where]
    df = df[select]
    # df = df.groupby(group_by).sum()
    df = df.sort_values(order_by, ascending=False, ignore_index=True)
    df = df.iloc[:limit, :]

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


def col_defs_highlight_pass():
       
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
            name='team',
            title='',
            plot_fn=image,
            width=1,
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
            title='Total',
            formatter="{:.0f}",
            group="Pases",
            width=data_width,
            cmap=cmap1,
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
            textprops= {"bbox": {"boxstyle": "circle", "pad": 0.05}},
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
                textprops= {"bbox": {"boxstyle": "circle", "pad": 0.05}},
                width=percent_width,
                ),   
        ]
       
    return col_defs

if __name__ == "__main__":
    df = read_db()

    home = 'imbabura'
    away = 'delfin'

    match = [home, away]

    df_home = order_data(df, match, home)
    df_away = order_data(df, match, away)

    # Table
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(11, 13))
    ax_home = axs[0]
    ax_away = axs[1]
    
    bg_color = '#faf9f4'
    fig.set_facecolor(bg_color)
    ax_home.set_facecolor('white')

    # Home table
    col_defs = col_defs_highlight_pass()
    tab_home = Table(df_home,
                     column_definitions=col_defs,
                     ax=ax_home,
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )
    
    col_defs = col_defs_highlight_pass()
    tab_away = Table(df_away,
                     column_definitions=col_defs,
                     ax=ax_away,
                     textprops={"ha": "center"},
                     # cell_kw={'facecolor': 'red'}
                     )
            

    fig.savefig(f"images/match_report.png", dpi=600)
