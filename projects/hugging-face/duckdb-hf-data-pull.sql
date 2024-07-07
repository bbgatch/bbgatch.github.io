select *
from 'hf://datasets/bbgatch/tsa-passengers/tsa.csv';

select *
from 'hf://datasets/bbgatch/tsa-passengers/tsa.csv'
order by passengers desc
;


-- duckdb -s "COPY (select date_trunc('month', date) as date, sum(passengers) from 'hf://datasets/bbgatch/tsa-passengers/tsa.csv' group by 1 order by 1) TO '/dev/stdout' WITH (FORMAT 'csv', HEADER)" \
--      | uplot line -d, -H -t "TSA Checkpoint Passenger Volumes"