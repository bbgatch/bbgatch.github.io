import duckdb
from datetime import datetime

df = duckdb.read_csv('jury-duty.csv')

sql = """
    select
        group_num
        -- ,datepart('dayofweek', date) as dow
        -- ,dayname(date) as day
        ,sum(called) as days_called
        ,count(called) as days_summoned
        ,sum(called) / count(called) as call_pct

    from df
    group by 1
    order by 1
"""

duckdb.sql(sql)

min_date = duckdb.sql("select min(date) from df").fetchone()[0].strftime('%Y-%m-%d')
max_date = duckdb.sql("select max(date) from df").fetchone()[0].strftime('%Y-%m-%d')
