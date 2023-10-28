import polars as pl
from datetime import timedelta

df = pl.read_csv('data/tsa-orig.csv', )

df = df.with_columns(
    pl.col("Date").str.to_date("%m/%d/%Y"),
    pl.col("2023").cast(pl.Int64)
)

df = df.melt(id_vars=['Date'], value_name='passengers', variable_name="Year_Column")

df = df.filter(
    pl.col("passengers").is_not_null()
)

end = df.select(pl.max("Date")).item()
start = end - timedelta(days=df.shape[0] - 1)

df = df.with_columns(
    date = pl.date_range(start, end, "1d", eager=True).reverse()
)
df
df = df.select("date", "passengers")
df

# df.to_csv('data/history/tsa-' + str(date.today()) + '.csv', index=False)
# df.to_csv('data/tsa.csv', index=False)