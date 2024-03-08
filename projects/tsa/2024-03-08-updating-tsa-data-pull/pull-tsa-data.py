import requests
import pandas as pd
from io import StringIO

# URL that we want to pull TSA data from
url = "http://www.tsa.gov/travel/passenger-volumes"

# Read the page using requests.get()
r = requests.get(url)

# Use pd.read_html() to parse the html text
df = pd.read_html(StringIO(r.text))

# The result is a list of 1 dataframe, we need to select that dataframe from the list
df = df[0]

# Save data
df.to_csv('data/tsa-orig.csv', index=False)
print('Data pulled.')