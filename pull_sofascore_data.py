import PySimpleGUI as sg
import json
import os


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
    results_w = 30

    rt = 'Results will show here'  # Results Text

    # 1. Define the window's contents

    # Create columns to show results
    column_lineups = [
        [t('Lineups')],
        [sg.Multiline(s=(results_w, 5), k='-LINEUPS-', default_text=rt, font=results_font)]
    ]

    column_statistics = [
        [t('Statistics')],
        [sg.Multiline(s=(results_w, 5), k='-STATISTICS-', default_text=rt, font=results_font)]
    ]

    column_shotmap = [
        [t('Shotmap')],
        [sg.Multiline(s=(results_w, 5), k='-SHOTMAP-', default_text=rt, font=results_font)]
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
        [sg.Column(column_lineups), sg.VSeparator(),
         sg.Column(column_statistics), sg.VSeparator(),
         sg.Column(column_shotmap)],
        [t('')],
        [sg.Button('Load')],

        # [t('Please select files:')],
        # [t('Transcript (.docx)',        s=(w1, 1)), i(s=(w2, 1), enable_events=True, k="-TRANSCRIPT-"), fb('Browse')],
        # [t('STT File - AWS',            s=(w1, 1)), i(s=(w2, 1), enable_events=True, k="-AWS-"), fb('Browse')],
        #
        # [t('')],
        # [sg.Submit(), sg.Cancel()],
        # [t('')],
        # [sg.Column(column1)],
        # [sg.Column(column2)],
        # [t('')]
    ]

    # 2. Create the window
    window = sg.Window('STT Accuracy Benchmark', layout, font=base_font)

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
            for data in ['lineups', 'statistics', 'shotmap']:

                home = values["-HOME-"]
                away = values["-AWAY-"]
                mw = values["-MW-"]

                file = f'{home}_{away}_{data}.json'
                mw_dir = os.path.join('data', 'matches', f'mw{mw}')
                fp = os.path.join(mw_dir, file)

                vals = values[f'-{data.swapcase()}-']

                with open(fp, 'w') as f:
                    f.write(vals)

                print(f'{data} data saved at {fp}')

        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

    # 4. Remove from the screen
    window.close()


if __name__ == "__main__":
    main()
