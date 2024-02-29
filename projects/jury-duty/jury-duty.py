import duckdb

df = duckdb.read_csv('jury-duty.csv')

sql = """
    select
        group_num
        -- ,datepart('dayofweek', date) as dow
        -- ,dayname(date) as day
        ,sum(called)
        ,count(called)
        ,sum(called) / count(called) as call_pct

    from df
    where group_num <= 6
    group by 1
    order by 1
"""

duckdb.sql(sql)