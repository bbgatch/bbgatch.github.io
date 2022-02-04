import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('tsa.csv')

df['Date'] = pd.to_datetime(df['Date'])

# Plot data
plt.figure(figsize=(9, 5))
plt.plot(df['Date'], df['Passengers'], color='darkslategray')
plt.title('U.S. TSA Checkpoint Passengers | data through ' + max(df['Date']).strftime('%Y-%m-%d'))

plt.savefig('tsa.png')
plt.show()
