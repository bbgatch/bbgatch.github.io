create table recordings (
    sid                text primary key,
    date_created       text,
    date_updated       text,
    duration           integer,
    price              real,
    price_unit         text,
    start_time         text,
    status             text,
    recording          blob
    call_sid           text,
    account_sid        text,
    conference_sid     text,
    channels           integer,
    source             text,
    error_code         text,
    uri                text,
    encryption_details text,
    subresource_uris   text,
    media_url          text,
    api_version        text,
)

create table transcriptions (
    sid                      text primary key,
    date_created             text,
    date_updated             text,
    duration                 integer,
    price                    real,
    price_unit               text,
    status                   text,
    transcription_text       text,
    account_sid              text,
    type                     text,
    recording_sid            text,
    uri                      text,
    api_version              text
)