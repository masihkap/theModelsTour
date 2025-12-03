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
    df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if tour == 'ErasTour':
        total_row = df[df.apply(lambda row: 
                                row.astype(str).str.contains('Total', case=False).any(), 
                                axis=1)]
        if not total_row.empty:
            total_attendance = float(total_row['Attendance'].iloc[0])
            total_shows = df['Date'].nunique()
            total_cities = df['City'].nunique()

        else:
            concert_rows = df[df['Attendance'].notna()]
            total_attendance = concert_rows['Attendance'].sum()
            total_shows = df['Date'].nunique()
            total_cities = df['City'].nunique()
    else:
        # use calc for other tours
        concert_rows = df[df['Attendance'].notna()]

        total_attendance = concert_rows['Attendance'].sum()
        total_shows = df['Date'].nunique()
        total_cities = df['City'].nunique()

    # Average attendance per show
    avg_attendance_show = total_attendance / total_shows if total_shows else 0
   
    tour_summary.append({
        'Tour': tour
        , 'Total_Attendance': total_attendance
        , 'Total_Shows': total_shows
        , 'Total_Cities': total_cities
        , 'Avg_Attendance_Per_Show': avg_attendance_show
    })


tour_summary_df = pd.DataFrame(tour_summary)
tour_summary_df['Attendance_Growth_Previous_Tour'] = tour_summary_df['Avg_Attendance_Per_Show'].pct_change() * 100
tour_summary_df['Attendance_Growth_Previous_Tour'] = tour_summary_df['Attendance_Growth_Previous_Tour'].round(2)
tour_summary_df['Tour'] = tour_summary_df['Tour'].replace({'Tour1989': '1989Tour'})
print(tour_summary_df)
print()

# Sort by tour chronological order
tour_order = ['FearlessTour', 'SpeakNowTour', 'RedTour', '1989Tour', 'ReputationTour', 'ErasTour']
tour_summary_df['Tour'] = pd.Categorical(tour_summary_df['Tour'], categories=tour_order, ordered=True)
tour_summary_df = tour_summary_df.sort_values('Tour')

# # Plot total attendance growth
eras_colors = ['#D8B372', '#A088A2', '#7A2E39', "#8AC9E4", "#746F70", "#242E47"]
plt.figure(figsize=(10,6))
sns.barplot(x='Tour', y='Total_Attendance', data=tour_summary_df, palette=eras_colors, hue = 'Tour')
plt.title('Total Attendance per Tour', fontsize=16)
plt.ylabel('Total Attendance')
plt.ticklabel_format(style='plain', axis='y') # Disable scientific notation
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}')) #add comma seperator
plt.xlabel('Tour')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"Total_Attendance_per_Tour", dpi=300, bbox_inches='tight')
plt.show()

# Plot average attendance per show growth
plt.figure(figsize=(10,6))
sns.barplot(x='Tour', y='Avg_Attendance_Per_Show', data=tour_summary_df, palette=eras_colors, hue = 'Tour')
plt.title('Average Attendance per Show per Tour', fontsize=16)
plt.ylabel('Average Attendance per Show')
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}')) #add comma seperator
plt.xlabel('Tour')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"Avg_Attendance_per_Show_per_Tour", dpi=300, bbox_inches='tight')
plt.show()