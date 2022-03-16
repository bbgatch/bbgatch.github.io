import requests
import pandas as pd

def pull_data():
    '''
    Pull TSA checkpoint traveler data from https://www.tsa.gov/coronavirus/passenger-throughput
    '''
    # Guided by:
    # https://towardsdatascience.com/a-guide-to-scraping-html-tables-with-pandas-and-beautifulsoup-7fc24c331cf7
    # https://stackoverflow.com/questions/43590153/http-error-403-forbidden-when-reading-html

    # URL that we want to pull TSA data from
    url = "https://www.tsa.gov/coronavirus/passenger-throughput"

    # Read the page using requests.get()
    r = requests.get(url)
    
    # Use pd.read_html() to parse the html text
    df = pd.read_html(r.text)

    # The result is a list of 1 dataframe, we need to select that dataframe from the list
    df = df[0]

    # Changing data types.
    df['Date'] = pd.to_datetime(df['Date'])

    # Sorting by Date.
    df = df.sort_values(by='Date')

    # Save data in original format
    df.to_csv('data/tsa-orig.csv', index=False)
    print('Data pulled.')