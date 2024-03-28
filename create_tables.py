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
    with open(fp, 'r', encoding="utf8") as f:
        dataframe = pd.read_csv(f)
    return dataframe


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
        'mushuc-runa': 'mr',
        'nacional': 'na',
        'orense': 'or',
        'catolica': 'uc',
    }

    fp = os.path.join(img_path, f'{teams[fn]}.png')
    return fp


def order_data(df, stat_type):
    select = [
        'player', 'team', 'minutesPlayed', 'matchweek'
    ]



    if stat_type == 'totalPass':
        select.append('totalPass')
        select.append('accuratePass')
        select.append('goalAssist')

        order_by = 'totalPass'

    elif stat_type == 'TotalShots':
        select.append('TotalShots')
        select.append('ShotOnTarget')
        select.append('goals')

        order_by = 'TotalShots'

    group_by = ['team', 'player']
    limit = 10

    df = df[select]

    # List of stats columns excluding those to exclude
    stats_columns = [col for col in df.columns if col not in ['player', 'team', 'matchweek']]

    # Construct aggregation dictionary
    agg_dict = {col: 'sum' for col in stats_columns}
    agg_dict['matchweek'] = 'max'

    df = df.groupby(group_by).agg(agg_dict)
    df = df.sort_values(order_by, ascending=False)
    df = df.iloc[:limit, :]

    # Drop team and player name from index and add them as col
    df = df.reset_index()
    # Move team to another col for final table aesthetics
    df.insert(1, 'team', df.pop('team'))
    # Start index from 1, so it is a ranking on the table (1-10)
    df.index += 1

    # Add percentages
    if stat_type == 'totalPass':
        # - Pass Accuracy
        pass_accuracy = (df['accuratePass'] / df['totalPass'])
        df.insert(len(df.columns)-1, 'PassAccuracy', pass_accuracy)
    elif stat_type == 'TotalShots':
        # - Shot on Target %
        shot_on_target = (df['ShotOnTarget'] / df['TotalShots'])
        df.insert(len(df.columns)-1, 'SoT_percent', shot_on_target)

    # Replace NaNs with 0
    df = df.fillna(0)

    # Change team names to logo images filepaths for plottable
    df['team'] = df['team'].apply(team_name_to_path)

    df['minutesPlayed'] = df['minutesPlayed'] / 90

    return df


def plot_table(df, stat_type, output_fn):

    # --------------------------------------- Figure
    bg_color = '#faf9f4'

     # Table
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(11, 8))
    ax.set_facecolor(bg_color)

    # Axis for title
    h = 0.1
    ax_title = fig.add_axes([0, 0.9, 1, h], zorder=1)
    ax_title.axis('off')

    col_defs = get_col_defs(stat_type)

    mw = df['matchweek'].max()

    # Exclude matchweek column from table

    exclude = ['matchweek']
    df = (df.loc[:, df.columns != 'matchweek'])

    tab = Table(df,
                ax=ax,
                column_definitions=col_defs,
                textprops={
                    "ha": "center",
                    },
                )
    
    if stat_type=='shot':
        fig.suptitle('Top 10 Jugadores con más disparos', fontsize=17)
    elif stat_type=='pass':
        fig.suptitle('Top 10 Jugadores con más pases', fontsize=17)


    ax.set_title(f'LigaPro 2024 - {mw} Fechas', fontsize=15)

    # -- Transformation functions (thanks Son of a corner)
    DC_to_FC = ax_title.transData.transform
    FC_to_NFC = fig.transFigure.inverted().transform
    # Transform for title axes
    ax_title_tf = lambda x: FC_to_NFC(DC_to_FC(x))

    # Add team logo
    ax_coords = ax_title_tf((0.205, 0.1))
    ax_size = 0.155
    image = Image.open(os.path.join('data', 'logos', 'lp.png'))
    newax = fig.add_axes(
        [ax_coords[0]-ax_size/2, ax_coords[1]-ax_size/2, ax_size, ax_size],
        anchor='W', zorder=1
    )
    newax.imshow(image)
    newax.axis('off')

    fig.savefig(f"images/{output_fn}", facecolor=ax.get_facecolor(), dpi=200)


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
            width=1.5,
            ),

        ColumnDefinition(
            name='team',
            title='',
            plot_fn=image,
            width=1,
            ),

        ColumnDefinition(
            name='minutesPlayed',
            title='90s',
            formatter="{:.1f}",
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
            ),

        ColumnDefinition(
            name='goalAssist',
            title='Asistencias',
            formatter="{:.0f}",
            group="Pases",
            width=data_width,
            ) 
        ] 

            
    elif stat_type == 'shot':
        stats_col_defs = [
            ColumnDefinition(
                name='TotalShots',
                title='Total',
                formatter="{:.0f}",
                group="Tiros",
                width=data_width,
                cmap=cmap1,
                ),

            ColumnDefinition(
                name='ShotOnTarget',
                title='Al Arco',
                formatter="{:.0f}",
                group="Tiros",
                width=data_width,
                ),

            ColumnDefinition(
                name='SoT_percent',
                title='Precisión',
                formatter=decimal_to_percent,
                group="Tiros",
                cmap=cmap_test,
                textprops= {"bbox": {"boxstyle": "circle", "pad": 0.05}},
                width=percent_width,
                ),

            ColumnDefinition(
                    name='goals',
                    title='Goles',
                    formatter="{:.0f}",
                    group="Tiros",
                    width=data_width,
                    ) 
        ]

    for stat in stats_col_defs:
        col_defs.append(stat)

    return col_defs    


if __name__ == "__main__":

    df = read_db()

    # --------------------------------------- Add Tables
    df_pass = order_data(df, 'totalPass')
    plot_table(df_pass, 'pass', 'total_passes.png')

    df_shot = order_data(df, 'TotalShots')
    plot_table(df_shot, 'shot', 'total_shots.png')
