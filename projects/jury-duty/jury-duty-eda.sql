select
    group_num
    ,extract(dayofweek from date) as dow
    ,sum(called) as days_called
    ,count(called) as days_summoned
    ,sum(called) / count(called) as call_probability
    ,cast(round((sum(called) / count(called)) * 100, 2) as string) || '%' as call_probability_str

from read_csv('jury-duty.csv')
group by 1, 2
order by 1, 2
;