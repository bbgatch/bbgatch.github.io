select
    sid
    ,date_created
    ,date_updated
    ,duration
    ,price
    ,status
    ,call_sid
from recordings
order by date_created desc
limit 5
;

select
    sid
    ,date_created
    ,date_updated
    ,duration
    ,price
    ,status
    ,transcription_text
from transcriptions
order by date_created desc
limit 5
;