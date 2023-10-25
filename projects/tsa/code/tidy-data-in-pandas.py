import pandas as pd
from datetime import date, timedelta

df = pd.read_csv('data/tsa-orig.csv')

df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%y")

df = pd.melt(df, id_vars=['Date'], value_name='passengers')

end = df['Date'].max().date()
start = end - timedelta(days=df.shape[0] - 1)

df['date'] = pd.date_range(start, end)[::-1]
df
df[['date', 'passengers']]

df.to_csv('data/history/tsa-' + str(date.today()) + '.csv', index=False)
df.to_csv('data/tsa.csv', index=False)