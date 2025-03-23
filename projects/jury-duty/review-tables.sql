select
    recording_sid
    ,date_created
    ,jury_duty_date
    -- ,date_updated
    ,duration
    -- ,price
    ,status
    -- ,call_sid
    ,recording_transcription
    ,jury_duty_group_csv
from recordings
order by date_created desc
limit 5
;

-- select
--     sid
--     ,date_created
--     ,date_updated
--     -- ,duration
--     ,price
--     -- ,status
--     ,transcription_text
--     ,jury_duty_group_data
-- from transcriptions
-- order by date_created desc
-- limit 5
-- ;