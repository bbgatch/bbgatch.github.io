import pandas as pd
from datetime import date, timedelta
# Some records have null values, need to figure out
df = pd.read_csv('data/tsa-orig.csv')

df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%Y")

df = pd.melt(df, id_vars=['Date'], value_name='passengers')

# We still have some nulls!
df[df['passengers'].isnull()]

df = df[df['passengers'].notnull()]

end = df['Date'].max().date()
start = end - timedelta(days=df.shape[0] - 1)

df['date'] = pd.date_range(start, end)[::-1]
df
df[['date', 'passengers']]

df.to_csv('data/history/tsa-' + str(date.today()) + '.csv', index=False)
df.to_csv('data/tsa.csv', index=False)