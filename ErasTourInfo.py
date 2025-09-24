import pandas as pd
import wikipedia as wp
import re

# clean out footnote references
def clean_string(df):
    return df.apply(
        lambda col: col.astype(str).str.replace(r'\[.*?\]', '', regex=True).str.strip()
        if col.dtype == 'object' else col
    )

#split the attendance column into attendance and venue capacity
def attendance_split(df):
    if 'Attendance' in df.columns:
        df['Attendance'] = df['Attendance'].str.replace(r'\[.*?\]', '', regex=True).str.strip()
        split_cols = df['Attendance'].str.split('/', n=1, expand=True)
        df['Attendance'] = (
            split_cols[0]
            .str.replace(',', '', regex=False)
            .replace('—', '')
            .str.strip()
        )
        df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')
        
        df['Venue Capacity'] = (
            split_cols[1]
            .str.replace(',', '', regex=False)
            .replace('—', '')
            .str.strip()
        )
        df['Venue Capacity'] = pd.to_numeric(df['Venue Capacity'], errors='coerce')
    return df


title = 'The Eras Tour'
try:
    html_content = wp.page(title).html()
except wp.exceptions.PageError:
    print(f'Error: Page not found.')
    exit()

tables = pd.read_html(html_content)

if tables:
    Dates2023 = clean_string(tables[8])
    Dates2023['Date (2023)'] = Dates2023['Date (2023)'] + ", 2023"
    Dates2023['Date (2023)'] = pd.to_datetime(Dates2023['Date (2023)'], format='%B %d, %Y', errors='coerce')
    Dates2023 = attendance_split(Dates2023)
    Eras2023 = Dates2023.rename(columns={'Date (2023)': 'Date'})

    Dates2024 = clean_string(tables[9])
    Dates2024['Date (2024)'] = Dates2024['Date (2024)'] + ", 2024"
    Dates2024['Date (2024)'] = pd.to_datetime(Dates2024['Date (2024)'], format='%B %d, %Y', errors='coerce')
    Dates2024 = attendance_split(Dates2024)
    Eras2024 = Dates2024.rename(columns={'Date (2024)': 'Date'})

    ErasTour = pd.concat([Eras2023, Eras2024], axis=0)

#assign tour ID generated in TourAlbumInfo.py
    PrePostCutoff_Date = pd.to_datetime('2024-05-09')
    ErasTour['Tour_ID'] = ErasTour['Date'].apply(lambda x: 6 if x < PrePostCutoff_Date else 7)

    ErasTour.to_csv('ErasTour.csv', index=False, encoding="utf-8")
else:
    print('No tables found.')

