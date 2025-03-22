import io
import os
import json
import time
import sqlite3
import whisper
import requests
import tempfile
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from twilio.rest import Client

def make_call(client, from_number, to_number):
    client = client
    call = client.calls.create(
        twiml='<Response><Record transcribe="true" timeout="10"/></Response>',
        from_=from_number,
        to=to_number,
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


def extract_group_data(transcript, openai_api_key):
    # Connect to OpenAI API
    client = OpenAI(api_key=openai_api_key)
    # Instructions for processing the transcript
    instructions = """
        You are an AI assistant extracting information from transcripts of an automated recording about jury duty assignments.

        Please extract the following:
        1. The date of the jury duty in YYYY-MM-DD format.
        2. Which groups need to come in for jury duty.
        3. Which groups do not need to come in for jury duty.

        Format the data in CSV format like this, with a 1 indicating that the group needs to come in and 0 indicating that the group does not need to come in:
        date,group_num,called
        2024-01-17,1,1
        2024-01-17,2,1
        2024-01-17,3,1
        2024-01-17,4,1
        2024-01-17,5,0
        2024-01-17,6,0
        2024-01-17,7,0

        Read carefully to check which groups are required to come in (marked as 1) and which groups are excused (marked as 0).
        Include only the CSV data output without the header line. Don't include backticks or extra text.
        Make sure the groups are ordered in ascending order by group number.
    """
    # Call the OpenAI API to process the transcript
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=transcript
    )
    # Save and print initial output
    output = response.output_text
    # print("OpenAI output:")
    # print(output)
    
    # Sometimes the API does not return the results sorted by group number
    # Try to convert to Pandas DataFrame and sort by group number so that output is consistently sorted
    try:
        df = pd.read_csv(io.StringIO(output), header=None, names=["date", "group_num", "called"])
        df.sort_values(by="group_num", inplace=True)
        return df.to_csv(index=False, header=False)
    except:
        return output


def save_recordings(db_path, openai_api_key):
    print("Saving recordings")
    # SQLite connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all recordings from Twilio
    all_recordings = client.recordings.list()
    # Get list of existing recording IDs so we don't spend time trying to re-download them
    previously_downloaded_recordings = cursor.execute("select recording_sid from recordings;").fetchall()
    previously_downloaded_recordings = [recording[0] for recording in previously_downloaded_recordings]  # Convert row tuples to list of strings
    # Remove any recordings that have already been downloaded
    new_recordings = [recording for recording in all_recordings if recording.sid not in previously_downloaded_recordings]
    
    print(f"Total recordings on Twilio: {len(all_recordings)}")
    print(f"New recordings to process: {len(new_recordings)}")

    # Load whisper model for transcribing audio recording
    whisper_model = whisper.load_model("medium.en")

    data_to_insert = []
    for recording in new_recordings:
        # Get the recording
        recording_mp3 = requests.get(recording.media_url, auth=(account_sid, auth_token)).content
        
        try:
            # Create a temporary file to store the MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(recording_mp3)
                temp_file_path = temp_file.name

            # Transcribe recording with whisper
            transcription = whisper_model.transcribe(temp_file_path, fp16=False)["text"]

            # Extract jury duty group data from transcription
            jury_duty_group_csv = extract_group_data(transcription, openai_api_key)

            # Gather all fields that we want to save to the database
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
                recording_mp3,  # Actual recording MP3 data we'll save in BLOB format
                transcription,  # Transcribed recording text
                jury_duty_group_csv,
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
            print(f"Recording {recording.sid} processed")

        finally:
            # Delete the temporary file
            os.unlink(temp_file_path)

    insert_query = """
        -- INSERT OR IGNORE will insert any new records but ignore any that already exist
        INSERT OR IGNORE INTO recordings (
            recording_sid,
            date_created,
            date_updated,
            duration,
            price,
            price_unit,
            start_time,
            status,
            recording,
            recording_transcription,
            jury_duty_group_csv,
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
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        # cursor.rowcount is the number of records inserted
        print(f"Inserted {cursor.rowcount} recordings into the database")
    except Exception as e:
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    db_path = os.getenv("DB_PATH")

    client = Client(account_sid, auth_token)

    # make_call(client, from_number, to_number)
    save_recordings(db_path, openai_api_key)
    # save_transcriptions(db_path, openai_api_key)



# def save_transcriptions(db_path, openai_api_key):
#     print("Saving transcriptions")
#     # SQLite connection
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     transcriptions = client.transcriptions.list()
#     data_to_insert = []
#     for transcription in transcriptions:
#         # Map Twilio recording attributes to your table columns
#         # Twilio gives datetime objects; convert to ISO strings
#         record = (
#             transcription.sid,
#             transcription.date_created.isoformat(),
#             transcription.date_updated.isoformat(),
#             transcription.duration,
#             float(transcription.price),
#             transcription.price_unit,
#             transcription.status,
#             transcription.transcription_text,
#             extract_group_data(transcription.transcription_text, openai_api_key),
#             transcription.account_sid,
#             transcription.type,
#             transcription.recording_sid,
#             transcription.uri,
#             transcription.api_version
#         )
#         data_to_insert.append(record)
#     insert_query = """
#         -- INSERT OR IGNORE will insert any new records but ignore any that already exist
#         INSERT OR IGNORE INTO transcriptions (
#             sid,
#             date_created,
#             date_updated,
#             duration,
#             price,
#             price_unit,
#             status,
#             transcription_text,
#             jury_duty_group_data,
#             account_sid,
#             type,
#             recording_sid,
#             uri,
#             api_version
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """
#     try:
#         cursor.executemany(insert_query, data_to_insert)
#         conn.commit()
#         # cursor.rowcount is the number of records inserted
#         print(f"Inserted {cursor.rowcount} transcriptions")
#     except sqlite3.IntegrityError as e:
#         print(f"Some inserts failed: {e}")
#         conn.rollback()
#     finally:
#         conn.close()