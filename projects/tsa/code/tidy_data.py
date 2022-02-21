import pandas as pd
from datetime import date, timedelta

def tidy_data():
    df = pd.read_csv('data/tsa-orig.csv')
    df['Date'] = pd.to_datetime(df['Date'])

    # Data is not stored in tidy format. We need to separate the "this year" and 
    # "last year" dates into two separate dataframes in order to do this properly.
    df_ly = df[df['Date'].dt.year == 2021].copy()
    df_ty = df[df['Date'].dt.year == 2022].copy()

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
    final.to_csv('data/history/tsa-' + str(date.today()) + '.csv', index=False)
    final.to_csv('data/tsa.csv', index=False)
    print('Data tidied.')

def widen_data_by_year():
    df = pd.read_csv('data/tsa.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
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
    df.to_csv('data/tsa-by-year.csv', index=False)
