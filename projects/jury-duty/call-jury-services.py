import os
import json
import time
import sqlite3
import requests
from dotenv import load_dotenv
from twilio.rest import Client

def make_call(client):
    client = client
    call = client.calls.create(
        twiml='<Response><Record transcribe="true" timeout="10"/></Response>',
        to=to_number,
        from_=from_number,
        send_digits="1",
        trim="trim-silence",
        time_limit=120
        # record=True,  # We're already recording in the response TWIML call above, so including record here will cause duplicate recordings
    )
    print("Making call to jury services")
    print("Waiting four minutes for call to take place and transcription to be generated")
    time.sleep(240)
    
    # Check if call was successful
    call = client.calls(call.sid).fetch()
    print(f"Call placed: {call.date_created}")
    print(f"Status: {call.status}")
    print(f"Duration (secs): {call.duration}")
    if call.status != "completed" or int(call.duration) < 30:
        print("*** Call was not completed successfully! ***")


def save_recordings(db_path):
    print("Saving recordings")
    # SQLite connection
    conn = sqlite3.connect(db_path)
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
        print(f"Inserted {cursor.rowcount} recordings")
    except sqlite3.IntegrityError as e:
        print(f"Some inserts failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_transcriptions(db_path):
    print("Saving transcriptions")
    # SQLite connection
    conn = sqlite3.connect(db_path)
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
        print(f"Inserted {cursor.rowcount} transcriptions")
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
    db_path = os.getenv("DB_PATH")

    client = Client(account_sid, auth_token)

    make_call(client)
    save_recordings(db_path)
    save_transcriptions(db_path)

