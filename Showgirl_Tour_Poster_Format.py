import pandas as pd

# Load file
df = pd.read_csv('Predicted_Showgirl_Tour_Paper.csv')

# Clean text columns
for col in ['City','State','Country']:
    df[col] = df[col].astype(str).str.strip()

# Parse dates and sort properly
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(['City','State','Country','Date'])

# Detect consecutive days
df['date_diff'] = df.groupby(['City','State','Country'])['Date'] \
                    .diff().dt.days

df['new_group'] = (df['date_diff'] != 1).cumsum()

# Aggregate groups
out = df.groupby(['City','State','Country','new_group']).agg(
    start_date=('Date','min'),
    end_date=('Date','max')
).reset_index()

# Sort final output by date
out = out.sort_values('start_date')

# Format text
def format_range(row):
    start = row['start_date']
    end = row['end_date']

    if start == end:
        date_str = start.strftime("%B %d, %Y")
    elif start.month == end.month:
        date_str = f"{start.strftime('%B %d')} – {end.strftime('%d, %Y')}"
    else:
        date_str = f"{start.strftime('%B %d')} – {end.strftime('%B %d, %Y')}"
    
    return f"{date_str}  {row['City']}  {row['State']}  {row['Country']}"

out['Formatted'] = out.apply(format_range, axis=1)

for x in out['Formatted']:
    print(x)

