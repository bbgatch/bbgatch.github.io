import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

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


# Plot data by year
df = pd.read_csv('tsa-orig.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Get year labels from columns
years = df.columns[1:].sort_values()
num_years = len(years)

# Need to figure out the coloring so that it makes sense.
# Create colors for each year
cmap = cm.get_cmap('Blues', 10)
colors = cmap(range(num_years))
colors = cmap(range(10))

plt.figure(figsize=(9, 5))
for i in range(num_years):
    plt.plot(df['Date'],
             df[years[i]],
             label=years[i],
             color=colors[-i])
plt.legend()
plt.show()
print('Data plotted.')