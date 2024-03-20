import duckdb
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

sql = """
    select
        group_num
        -- ,datepart('dayofweek', date) as dow
        -- ,dayname(date) as day
        ,sum(called) as days_called
        ,count(called) as days_summoned
        -- ,sum(called) / count(called) as call_pct
        ,cast(round((sum(called) / count(called)) * 100, 2) as string) || '%' as call_pct_str

    from read_csv('jury-duty.csv')
    group by 1
    order by 1
"""

duckdb.sql(sql)
df = duckdb.sql(sql).df()

# Plot group call percentage
fig, ax = plt.subplots()
ax = sns.barplot(df, x="group_num", y="call_pct")
ax.bar_label(ax.containers[0], fmt=lambda x: f"{x * 100:.1f}%")
ax.set(xlabel="Group Number", ylabel="Call Percentage", title="Jury Duty Group Call Percentage")
ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
plt.savefig('images/group-probability-plot.png')

min_date = duckdb.sql("select min(date) from df").fetchone()[0].strftime('%Y-%m-%d')
max_date = duckdb.sql("select max(date) from df").fetchone()[0].strftime('%Y-%m-%d')

