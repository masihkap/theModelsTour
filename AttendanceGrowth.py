import pandas as pd
from datetime import date
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns

#attendance growth
##sum all concert attendance per tour/individual concerts 

Tours = {
    'FearlessTour': pd.read_csv('FearlessTour.csv')
    , 'SpeakNowTour': pd.read_csv('SpeakNowTour.csv')
    , 'RedTour': pd.read_csv('RedTour.csv')
    , 'Tour1989': pd.read_csv('1989Tour.csv')
    , 'ReputationTour': pd.read_csv('ReputationTour.csv')
    , 'ErasTour': pd.read_csv('ErasTour_Post.csv')
}

# #**see about dictionary prior and insert**
# Tour_Attendances = {}
# Tour_Attendances['Tour_ID'] = 1
# Tour_Attendances['Total_Attendance'] = FearlessTour['Attendance'].sum(skipna = True)
# Tour_Attendances['Total_Shows'] = FearlessTour['Date'].sum()
# Tour_Attendances['Per_Show_Attend'] = Tour_Attendances['Total_Attendance']/Tour_Attendances['Total_Shows']


tour_summary = []

for tour, df in Tours.items():
    total_row = df[df.apply(lambda row: row.astype(str).str.contains('Total', case = False).any(), axis = 1)]
    if not total_row.empty:
        total_attendance = total_row['Attendance'].astype(float).values[0]
        total_shows = total_row['Date'].astype(str).str.isnumeric().sum()
    else:
        concert_attendance = df[df['Attendance'].notna()]
        total_attendance = concert_attendance['Attendance'].sum()
        df['Date'] = pd.to_datetime(df['Date'])
        total_shows = df['Date'].nunique()


    df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')  # convert invalid entries to NaN
    concert_attendance = df[df['Attendance'].notna()]
    total_attendance = concert_attendance['Attendance'].sum()
    total_shows = df['Date'].nunique()
    avg_attendance_show = total_attendance / total_shows if total_shows > 0 else 0

    tour_summary.append({
        'Tour': tour
        , 'Total_Attendance': total_attendance
        , 'Total_Shows': total_shows
        , 'Avg_Attendance_Per_Show': avg_attendance_show
    })


tour_summary_df = pd.DataFrame(tour_summary)
tour_summary_df['Attendance_Growth_Previous_Tour'] = tour_summary_df['Avg_Attendance_Per_Show'].pct_change() * 100
tour_summary_df['Attendance_Growth_Previous_Tour'] = tour_summary_df['Attendance_Growth_Previous_Tour'].round(2)
print(tour_summary_df)
print()

tour_summary_df = pd.DataFrame(tour_summary)

# Sort by tour chronological order
tour_order = ['FearlessTour', 'SpeakNowTour', 'RedTour', 'Tour1989', 'ReputationTour', 'ErasTour']
tour_summary_df['Tour'] = pd.Categorical(tour_summary_df['Tour'], categories=tour_order, ordered=True)
tour_summary_df = tour_summary_df.sort_values('Tour')

# Plot total attendance growth
plt.figure(figsize=(10,6))
sns.barplot(x='Tour', y='Total_Attendance', data=tour_summary_df, palette='Blues_d')
plt.title('Total Attendance per Tour', fontsize=16)
plt.ylabel('Total Attendance')
plt.xlabel('Tour')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Total_Attendance_per_Tour.png', dpi=300)
plt.show()

# Plot average attendance per show growth
plt.figure(figsize=(10,6))
sns.barplot(x='Tour', y='Avg_Attendance_Per_Show', data=tour_summary_df, palette='Greens_d')
plt.title('Average Attendance per Show per Tour', fontsize=16)
plt.ylabel('Average Attendance per Show')
plt.xlabel('Tour')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Avg_Attendance_Per_Show_per_Tour.png', dpi=300)
plt.show()