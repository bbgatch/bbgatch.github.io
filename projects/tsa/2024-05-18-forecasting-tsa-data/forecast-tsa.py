import os
import duckdb
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import (AutoARIMA, HoltWinters)
from statsforecast.utils import AirPassengersDF
import matplotlib.pyplot as plt
import matplotlib

os.environ['NIXTLA_ID_AS_COL'] = '1'

# df = pd.read_csv('../2024-05-07-revisiting-tsa-data-pull/tsa.csv')
df = duckdb.sql("""
    select
        'tsa_passengers' as unique_id
        ,date_trunc('month', Date) as ds
        ,sum(Passengers) as y
    from '../2024-05-07-revisiting-tsa-data-pull/tsa.csv'
    where Date between '2019-01-01' and '2024-04-30'
    group by 1, 2
    order by ds
""").to_df()

sf = StatsForecast(
    models = [AutoARIMA(season_length = 12),
              HoltWinters(season_length = 12)],
    freq = 'M'
)

sf.fit(df)
forecast_df = sf.predict(h=9, level=[90])

sf.plot(df, forecast_df, level=[90])
# plt.savefig('tsa-monthly-forecast.png')
plt.show()



