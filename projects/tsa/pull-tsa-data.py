import requests
import pandas as pd
from io import StringIO

def pull_tsa_data(year, current_year):
    # The current year is only shown on the main TSA page
    if year != current_year:
        # URL that we want to pull TSA data from
        url = "http://www.tsa.gov/travel/passenger-volumes/" + str(year)
    else:
        url = "http://www.tsa.gov/travel/passenger-volumes/"
        
    # Read the page using requests.get()
    r = requests.get(url)

    # Use pd.read_html() to parse the html text
    df = pd.read_html(StringIO(r.text))

    # The result is a list of 1 dataframe, select that dataframe from the list
    df = df[0]

    # Current year site shows numbers for this year and last year. We're already
    # pulling last year from the site for last year. Select just the current 
    # year's YTD data.
    if year == current_year:
        df = df.iloc[:, 0:2]
    
    # Name columns and convert to date
    df.columns = ['date', 'passengers']
    df['date'] = pd.to_datetime(df['date'])
    
    print(str(year) + ' data pulled.')
    return df


# Available years to pull
years = [2024, 2023, 2022, 2021, 2020, 2019]
df_list = []

# Loop through all available years. Current year will be identified as the max 
# year. This assumes the current year will always be featured on the main TSA
# page and historical years will be stored on their own separate pages.
for year in years:
    df_list.append(
        pull_tsa_data(year = year, current_year = max(years))
    )

df = pd.concat(df_list)
df = df.sort_values(by='date')

# Save data
df.to_csv('tsa.csv', index=False)
print('🛫 Data pulled successfully! 🛬')

