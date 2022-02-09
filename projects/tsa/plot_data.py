import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('tsa.csv')
df['Date'] = pd.to_datetime(df['Date'])

def line_plot_full(df):
    # Plot data
    plt.figure(figsize=(9, 5))
    plt.plot(df['Date'], df['Passengers'], color='darkslategray')
    plt.title('U.S. TSA Checkpoint Passengers | data through ' + max(df['Date']).strftime('%Y-%m-%d'))

    plt.savefig('tsa-full.png')
    plt.show()

line_plot_full(df)

print('Data plotted.')