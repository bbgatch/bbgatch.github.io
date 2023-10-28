import duckdb

tsa = duckdb.sql("""
    select * from read_csv_auto('data/tsa-orig.csv', types={'2023':'int64'})
;""")

tsa_1 = duckdb.sql("""
    unpivot tsa
    -- on 2023, 2022, 2021, 2020, 2019
    on columns(* exclude (Date))
        into
           name year
           value passengers
    order by year desc, date desc
;""")

duckdb.sql("""
    select *
    -- select year, count(*)
    from tsa_1
    where year = 2023
    -- group by 1        
;""")

duckdb.sql("""
    select "2023" from tsa
    union all
    select "2022" from tsa
    union all
    select "2021" from tsa
    union all
    select "2020" from tsa
    union all
    select "2019" from tsa          
;""")

tsa_2 = duckdb.sql("""
    select 
        *
        ,row_number() over () - 1 as num_days_back
    from tsa_1          
;""")

duckdb.sql("""
    select
        *
        ,(select max(Date) from tsa_2) - cast(num_days_back as int) as date_new
    from tsa_2
;""")


