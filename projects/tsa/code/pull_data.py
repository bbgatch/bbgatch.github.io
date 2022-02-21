import requests
import lxml.html as lh
import pandas as pd
import datetime as dt
from datetime import date, timedelta

def pull_data():
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

    # Save data in original format
    df.to_csv('data/tsa-orig.csv', index=False)
    print('Data pulled.')