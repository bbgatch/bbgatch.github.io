import duckdb
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

sql = """
    select
        group_num
        ,sum(called) as days_called
        ,count(called) as days_summoned
        ,sum(called) / count(called) as call_probability
        ,cast(round((sum(called) / count(called)) * 100, 2) as string) || '%' as call_probability_str

    from read_csv('jury-duty.csv')
    group by 1
    order by 1
"""

duckdb.sql(sql)
df = duckdb.sql(sql).df()

# Plot group call probability
fig, ax = plt.subplots()
ax = sns.barplot(df, x="group_num", y="call_probability")
ax.bar_label(ax.containers[0], fmt=lambda x: f"{x * 100:.1f}%")
ax.set(xlabel="Group Number", ylabel="Call Probability", title="Jury Duty Group Call Probability")
ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
plt.savefig('images/group-probability-plot.png')

