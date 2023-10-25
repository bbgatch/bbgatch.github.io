import duckdb

tsa = duckdb.sql("""
    select * from read_csv_auto('data/tsa-orig.csv', types={'2023':'int64'})
;""")

duckdb.sql()