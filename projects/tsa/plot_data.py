import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm


def line_plot_full():
    df = pd.read_csv('tsa.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Passengers'], color='darkslategray')
    plt.title('U.S. TSA Checkpoint Passengers | data through ' + max(df['Date']).strftime('%Y-%m-%d'))

    # Convert axis labels to commas and remove scientific notation
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])

    plt.savefig('tsa-full-trend.png')
    plt.show()



def line_plot_by_year():
    df = pd.read_csv('tsa.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    latest_date = max(df['Date']).strftime('%Y-%m-%d')
    lag_1 = df.shift(periods=-364).rename(columns={'Passengers' : '2020',
                                                   'Date' : 'Date_2020'})
    lag_2 = df.shift(periods=-364 * 2).rename(columns={'Passengers' : '2021',
                                                       'Date' : 'Date_2021'})
    lag_3 = df.shift(periods=-364 * 3).rename(columns={'Passengers' : '2022',
                                                       'Date' : 'Date_2022'})   
    df = df.rename(columns={'Passengers' : '2019',
                            'Date' : 'Date_2019'})

    df = pd.concat([df, lag_1, lag_2, lag_3], axis=1)
    df['Date'] = pd.date_range(start="2022-01-01", periods=len(df), freq='D')
    df = df[df['Date'] <= '2022-12-31']

    df = df.drop(columns=['Date_2019', 'Date_2020', 'Date_2021', 'Date_2022'])

    df = df[['Date', '2019', '2020', '2021', '2022']]

    # Get year labels from columns
    years = df.columns[1:].sort_values()
    num_years = len(years)

    # Create colors for each year
    cmap = cm.get_cmap('Blues')
    colors = [0.2, 0.4, 0.6, 0.95]

    plt.figure(figsize=(10, 5))
    for i in range(num_years):
        plt.plot(df['Date'],
                df[years[i]],
                label=years[i],
                color=cmap(colors[i])
                )
    plt.legend()
    plt.title('U.S. TSA Checkpoint Passengers by Year | data through ' + latest_date)
    
    # Convert axis labels to commas and remove scientific notation
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
    
    plt.savefig('tsa-by-year.png')
    plt.show()


line_plot_full()
line_plot_by_year()
print('Data plotted.')