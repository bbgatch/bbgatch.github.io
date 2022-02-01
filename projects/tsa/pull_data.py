import requests
import lxml.html as lh
import pandas as pd
import datetime as dt
from datetime import date, timedelta

# Guided by:
# https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059

url = "https://www.tsa.gov/coronavirus/passenger-throughput"

# Create handle for the site contents.
page = requests.get(url)

# Store the contents of the website.
doc = lh.fromstring(page.content)

# Parse data stored between <tr>..</tr> in HTML
tr_elements = doc.xpath('//tr')

# Pulling out the header names
colnames = []
for t in tr_elements[0]:
    name = t.text_content()
    colnames.append(name)

# Creating lists of table data.
data = [[], [], [], [], []]
for row in tr_elements[1:]:
    i = 0
    for cell in row.iterchildren():
        datum = cell.text_content()
        datum = str(datum)
        # print(datum)
        datum = datum.strip()
        data[i].append(datum)
        i += 1

# Converting to dictionary for easier transition to Pandas dataframe.
df = dict(zip(colnames, data))

# Converting from dictionary to Pandas dataframe.
df = pd.DataFrame(df)

# Changing data types.
df['Date'] = pd.to_datetime(df['Date'])
df['2022'] = pd.to_numeric(df['2022'].str.replace(',', ''))
df['2021'] = pd.to_numeric(df['2021'].str.replace(',', ''))
df['2020'] = pd.to_numeric(df['2020'].str.replace(',', ''))
df['2019'] = pd.to_numeric(df['2019'].str.replace(',', ''))

# Sorting by Date.
df = df.sort_values(by = 'Date')

# Data is not stored in tidy format. We need to separate the "this year" and 
# "last year" dates into two separate dataframes in order to do this properly.
df_ly = df[df['Date'].dt.year == 2021]
df_ty = df[df['Date'].dt.year == 2022]

# The '2022' column has blank values for the 2021 dates, so we will delete that
# from the 'last year' dataframe. We can create dates for the 2020 and 2019 
# columns by subtracting 364 days from the 2021 dates. I'm assuming the dates
# are day-matched (matched to the same day of week) instead of day-matched 
# (matched) to the same numeric date.
df_ly = df_ly.drop(columns='2022')
df_ly['Date_2020'] = df_ly['Date'] - timedelta(364)
df_ly['Date_2019'] = df_ly['Date_2020'] - timedelta(364)

df_ty['Date_2021'] = df_ty['Date'] - timedelta(364)
df_ty['Date_2020'] = df_ty['Date_2021'] - timedelta(364)
df_ty['Date_2019'] = df_ty['Date_2020'] - timedelta(364)

# Now separate out the individual date and passenger volume fields for each 
# group.
df_ly_2019 = df_ly[['Date_2019', '2019']]
df_ly_2020 = df_ly[['Date_2020', '2020']]
df_ly_2021 = df_ly[['Date', '2021']]

df_ty_2019 = df_ty[['Date_2019', '2019']]
df_ty_2020 = df_ty[['Date_2020', '2020']]
df_ty_2021 = df_ty[['Date_2021', '2021']]
df_ty_2022 = df_ty[['Date', '2022']]

# Rename everything to just 'Date' and 'Passengers'
df_ly_2019 = df_ly_2019.rename(columns={'Date_2019' : 'Date', '2019' : 'Passengers'})
df_ly_2020 = df_ly_2020.rename(columns={'Date_2020' : 'Date', '2020' : 'Passengers'})
df_ly_2021 = df_ly_2021.rename(columns={'2021' : 'Passengers'})
df_ty_2019 = df_ty_2019.rename(columns={'Date_2019' : 'Date', '2019' : 'Passengers'})
df_ty_2020 = df_ty_2020.rename(columns={'Date_2020' : 'Date', '2020' : 'Passengers'})
df_ty_2021 = df_ty_2021.rename(columns={'Date_2021' : 'Date', '2021' : 'Passengers'})
df_ty_2022 = df_ty_2022.rename(columns={'2022' : 'Passengers'})

# Combine all of the separate dataframes and sort by date
final = pd.concat([df_ly_2019,
           df_ly_2020,
           df_ly_2021,
           df_ty_2019,
           df_ty_2020,
           df_ty_2021,
           df_ty_2022], ignore_index=True)
final = final.sort_values(by='Date')

# Save history and current results
final.to_csv('history/tsa-' + str(date.today()) + '.csv', index=False)
final.to_csv('tsa.csv', index=False)