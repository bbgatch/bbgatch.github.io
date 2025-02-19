import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

# TODO:
# Convert timestamps to Eastern time zone
# Add process to delete recordings and transcriptions after saving
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_PHONE_NUMBER")
to_number = os.getenv("DESTINATION_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def make_call(client):
    client = client
    client.calls.create(
        twiml='<Response><Record transcribe="true"/></Response>',
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

def read_saved_ids():
    with open("recordings/stored-recordings.txt", "r") as file:
        saved_recording_ids = [line.strip() for line in file.readlines()]
    with open("transcriptions/stored-transcriptions.txt", "r") as file:
        saved_transcription_ids = [line.strip() for line in file.readlines()]
    return saved_recording_ids, saved_transcription_ids

saved_recording_ids, saved_transcription_ids = read_saved_ids()

def save_recordings(client, saved_recording_ids):
    client = client
    recordings = client.recordings.list()
    for recording in recordings:
        if recording.sid in saved_recording_ids:
            print(f'Recording {recording.sid} already saved')
        else:
            # Download the recording
            recording_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording.sid}.mp3'
            recording_response = requests.get(recording_url, auth=(account_sid, auth_token))
            if int(recording.duration) < 20:
                print(f"Recording is too short, check for issues or rerun: {recording.sid}")
            # Save date and duration of recording in file name
            file_name = recording.date_created.strftime('%Y-%m-%d') + '-' + recording.duration + 'sec-' + recording.sid + '.mp3'
            with open(f'recordings/{file_name}', 'wb') as f:
                f.write(recording_response.content)
            print(f'Downloaded recording {file_name}')
            # Save downloaded recording ID to file of stored IDs
            with open('recordings/stored-recordings.txt', 'w') as f:
                f.write(recording.sid + '\n')

save_recordings(client, saved_recording_ids)

# Download transcriptions
def save_transcriptions(client, saved_transcription_ids):
    client = client
    transcriptions = client.transcriptions.list()
    for transcription in transcriptions:
        if transcription.sid in saved_transcription_ids:
            print(f'Transcription {transcription.sid} already saved')
        else:
            # Download the transcription
            transcription_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions/{transcription.sid}.txt'
            transcription_response = requests.get(transcription_url, auth=(account_sid, auth_token))
            if int(transcription.duration) < 20:
                print(f"Recording seems too short, check for issues or rerun: {transcription.sid}")
            # Save date and duration of transcription in file name
            file_name = transcription.date_created.strftime('%Y-%m-%d') + '-' + transcription.duration + 'sec-' + transcription.sid + '.txt'
            with open(f'transcriptions/{file_name}', 'w') as f:
                f.write(transcription_response.text)
            print(f'Downloaded transcription {file_name}')
            # Save downloaded transcription ID to file of stored IDs
            with open('transcriptions/stored-transcriptions.txt', 'w') as f:
                f.write(transcription.sid + '\n')

save_transcriptions(client, saved_transcription_ids)


# # Save IDs to a txt file
# recordings = [recording.sid for recording in recordings]
# with open('recordings/stored-recordings.txt', 'w') as f:
#     for recording in recordings:
#         f.write(recording + '\n')

# transcriptions = [transcription.sid for transcription in transcriptions]
# with open('transcriptions/stored-transcriptions.txt', 'w') as f:
#     for transcription in transcriptions:
#         f.write(transcription + '\n')

