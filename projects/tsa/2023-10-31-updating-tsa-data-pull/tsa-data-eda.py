import pandas as pd
from datetime import timedelta

df = pd.read_csv('data/tsa-orig.csv')

# If we combine all these dates, will we be missing any days?

# Create explicit date columns for each year
df['Date'] = pd.to_datetime(df['Date'])
df = df.rename(columns={'Date':'Date_2023'})
df['Date_2022'] = df['Date_2023'] - timedelta(days=364)
df['Date_2021'] = df['Date_2022'] - timedelta(days=364)
df['Date_2020'] = df['Date_2021'] - timedelta(days=364)
df['Date_2019'] = df['Date_2020'] - timedelta(days=364)

df = df[['Date_2023', 'Date_2022', 'Date_2021', 'Date_2020', 'Date_2019']]

df = pd.melt(df, value_vars=['Date_2023', 'Date_2022', 'Date_2021', 'Date_2020', 'Date_2019'])

df = df.sort_values(by='value', ascending=False)

# This will be including more dates than we actually have data for, because the 
# 2023 column doesn't contain a full year of data. So these dates get added as 
# extra "2023 dates" instead "2022 dates" the way we're checking this.

# Do we have a unique list of dates?
len(df)
len(df['value'].unique())

# Are we missing any dates?
df['Date_Diff'] = df['value'] - df['value'].shift(-1)
df.sort_values('Date_Diff', ascending=False)
# No! We have a 1 day gap between each row, we're not missing any days.

