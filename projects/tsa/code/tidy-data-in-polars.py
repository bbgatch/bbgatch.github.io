import polars as pl

df = pl.read_csv('data/tsa-orig.csv', )

df = df.with_columns(
    pl.col("Date").str.to_date("%m/%d/%Y"),
    pl.col("2023").cast(pl.Int64)
)

df = df.melt(id_vars=['Date'], value_name='passengers', variable_name="Year_Column")

df = df.filter(
    pl.col("passengers").is_not_null()
)

end = df.select(pl.max("Date"))
################################################################################
start = end - timedelta(days=df.shape[0] - 1)

df['date'] = pd.date_range(start, end)[::-1]
df
df[['date', 'passengers']]

df.to_csv('data/history/tsa-' + str(date.today()) + '.csv', index=False)
df.to_csv('data/tsa.csv', index=False)