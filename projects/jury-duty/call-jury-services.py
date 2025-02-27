import os
import json
import sqlite3
import requests
from dotenv import load_dotenv
from twilio.rest import Client

# TODO:
# Convert timestamps to Eastern time zone?
# Add process to delete recordings and transcriptions after saving?

def make_call(client):
    client = client
    client.calls.create(
        twiml='<Response><Record transcribe="true" timeout="10"/></Response>',
        to=to_number,
        from_=from_number,
        send_digits="1",
        trim="trim-silence",
        time_limit=120
        # record=True,  # We're already recording in the response TWIML call above, so including record here will cause duplicate recordings
        # recording_track="inbound",
        # recording_channels="mono",
    )
    # print(call.sid)

def save_recordings():
    # SQLite connection
    conn = sqlite3.connect('jury_duty.db')
    cursor = conn.cursor()

    recordings = client.recordings.list()
    data_to_insert = []
    for recording in recordings:
        # Map Twilio recording attributes to your table columns
        # Twilio gives datetime objects; convert to ISO strings
        record = (
            recording.sid,
            recording.date_created.isoformat(),
            recording.date_updated.isoformat(),
            recording.duration,
            float(recording.price),
            recording.price_unit,
            recording.start_time.isoformat(),
            recording.status,
            requests.get(recording.media_url, auth=(account_sid, auth_token)).content,  # Get actual recording MP3
            recording.call_sid,
            recording.account_sid,
            recording.conference_sid,
            recording.channels,
            recording.source,
            recording.error_code,
            recording.uri,
            json.dumps(recording.encryption_details) if recording.encryption_details else None,
            json.dumps(recording.subresource_uris) if recording.subresource_uris else None,
            recording.media_url,
            recording.api_version
        )
        data_to_insert.append(record)


    insert_query = """
        -- INSERT OR IGNORE will insert any new records but ignore any that already exist
        INSERT OR IGNORE INTO recordings (
            sid,
            date_created,
            date_updated,
            duration,
            price,
            price_unit,
            start_time,
            status,
            recording,
            call_sid,
            account_sid,
            conference_sid,
            channels,
            source,
            error_code,
            uri,
            encryption_details,
            subresource_uris,
            media_url,
            api_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        # cursor.rowcount is the number of records inserted
        print(f"Inserted {cursor.rowcount} recordings!")
    except sqlite3.IntegrityError as e:
        print(f"Some inserts failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def save_transcriptions():
    # SQLite connection
    conn = sqlite3.connect('jury_duty.db')
    cursor = conn.cursor()

    transcriptions = client.transcriptions.list()
    data_to_insert = []
    for transcription in transcriptions:
        # Map Twilio recording attributes to your table columns
        # Twilio gives datetime objects; convert to ISO strings
        record = (
            transcription.sid,
            transcription.date_created.isoformat(),
            transcription.date_updated.isoformat(),
            transcription.duration,
            float(transcription.price),
            transcription.price_unit,
            transcription.status,
            transcription.transcription_text,
            transcription.account_sid,
            transcription.type,
            transcription.recording_sid,
            transcription.uri,
            transcription.api_version
        )
        data_to_insert.append(record)

    insert_query = """
        -- INSERT OR IGNORE will insert any new records but ignore any that already exist
        INSERT OR IGNORE INTO transcriptions (
            sid,
            date_created,
            date_updated,
            duration,
            price,
            price_unit,
            status,
            transcription_text,
            account_sid,
            type,
            recording_sid,
            uri,
            api_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        # cursor.rowcount is the number of records inserted
        print(f"Inserted {cursor.rowcount} transcriptions!")
    except sqlite3.IntegrityError as e:
        print(f"Some inserts failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    load_dotenv()

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    to_number = os.getenv("DESTINATION_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    make_call(client)
    save_recordings()
    save_transcriptions()

################################################################################

# for recording in recordings:
#     if recording.sid in saved_recording_ids:
#         print(f'Recording {recording.sid} already saved')
#     else:
#         # Download the recording
#         recording_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording.sid}.mp3'
#         recording_response = requests.get(recording_url, auth=(account_sid, auth_token))
#         # if int(recording.duration) < 20:
#         #     print(f"Recording is too short, check for issues or rerun: {recording.sid}")
#         # Save date and duration of recording in file name
#         file_name = recording.date_created.strftime('%Y-%m-%d') + '-' + recording.duration + 'sec-' + recording.sid + '.mp3'
#         with open(f'recordings/{file_name}', 'wb') as f:
#             f.write(recording_response.content)
#         print(f'Downloaded recording {file_name}')
#         # Save downloaded recording ID to file of stored IDs
#         with open('recordings/stored-recordings.txt', 'a') as f:
#             f.write(recording.sid + '\n')


# def save_recordings(client):
#     # Read in saved recording IDs
#     saved_recording_ids = read_saved_ids(type="recordings")
#     # Download recordings
#     client = client
#     recordings = client.recordings.list()
#     for recording in recordings:
#         if recording.sid in saved_recording_ids:
#             print(f'Recording {recording.sid} already saved')
#         else:
#             # Download the recording
#             recording_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording.sid}.mp3'
#             recording_response = requests.get(recording_url, auth=(account_sid, auth_token))
#             # if int(recording.duration) < 20:
#             #     print(f"Recording is too short, check for issues or rerun: {recording.sid}")
#             # Save date and duration of recording in file name
#             file_name = recording.date_created.strftime('%Y-%m-%d') + '-' + recording.duration + 'sec-' + recording.sid + '.mp3'
#             with open(f'recordings/{file_name}', 'wb') as f:
#                 f.write(recording_response.content)
#             print(f'Downloaded recording {file_name}')
#             # Save downloaded recording ID to file of stored IDs
#             with open('recordings/stored-recordings.txt', 'a') as f:
#                 f.write(recording.sid + '\n')

# save_recordings(client)

# # Download transcriptions
# def save_transcriptions(client):
#     # Read in saved transcription IDs
#     saved_transcription_ids = read_saved_ids(type="transcriptions")
#     # Download transcriptions
#     client = client
#     transcriptions = client.transcriptions.list()
#     for transcription in transcriptions:
#         if transcription.sid in saved_transcription_ids:
#             print(f'Transcription {transcription.sid} already saved')
#         else:
#             # Download the transcription
#             transcription_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions/{transcription.sid}.txt'
#             transcription_response = requests.get(transcription_url, auth=(account_sid, auth_token))
#             # if int(transcription.duration) < 20:
#             #     print(f"Recording seems too short, check for issues or rerun: {transcription.sid}")
#             # Save date and duration of transcription in file name
#             file_name = transcription.date_created.strftime('%Y-%m-%d') + '-' + transcription.duration + 'sec-' + transcription.sid + '.txt'
#             with open(f'transcriptions/{file_name}', 'w') as f:
#                 f.write(transcription_response.text)
#             print(f'Downloaded transcription {file_name}')
#             # Save downloaded transcription ID to file of stored IDs
#             with open('transcriptions/stored-transcriptions.txt', 'a') as f:
#                 f.write(transcription.sid + '\n')

# save_transcriptions(client)


# # Save IDs to a txt file
# recordings = [recording.sid for recording in recordings]
# with open('recordings/stored-recordings.txt', 'w') as f:
#     for recording in recordings:
#         f.write(recording + '\n')

# transcriptions = [transcription.sid for transcription in transcriptions]
# with open('transcriptions/stored-transcriptions.txt', 'w') as f:
#     for transcription in transcriptions:
#         f.write(transcription + '\n')

