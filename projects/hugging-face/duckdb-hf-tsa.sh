duckdb -s \
     "copy ( \
          select sum(passengers) as passengers \
          from 'hf://datasets/bbgatch/tsa-passengers/tsa.csv' \
          group by date_trunc('month', date) \
          order by date_trunc('month', date) asc \
     ) to '/dev/stdout' with (FORMAT 'csv', HEADER)" \
     | uplot line -d, -H -t "TSA Checkpoint Passenger Volumes"
