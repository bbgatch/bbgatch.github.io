import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

# TODO:
# Convert timestamps to Eastern time zone
# Add lists of recording and transcription IDs already saved to avoid duplicates
# Add process to delete recordings and transcriptions after saving

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_PHONE_NUMBER")
to_number = os.getenv("DESTINATION_PHONE_NUMBER")

client = Client(account_sid, auth_token)

call = client.calls.create(
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

# Download recordings
recordings = client.recordings.list()
for recording in recordings:
    # Download the recording
    recording_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording.sid}.mp3'
    recording_response = requests.get(recording_url, auth=(account_sid, auth_token))
    if int(recording.duration) < 20:
        print("Recording is too short, check for issues or rerun.")
    
    # Save date and duration of recording in file name
    file_name = recording.date_created.strftime('%Y-%m-%d') + '-' + recording.duration + 'sec-' + recording.sid + '.mp3'
    
    with open(f'recordings/{file_name}', 'wb') as f:
        f.write(recording_response.content)
        
    print(f'Downloaded recording {file_name}')


# Download transcriptions
transcriptions = client.transcriptions.list()
for transcription in transcriptions:
    transcription_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions/{transcription.sid}.txt'
    transcription_response = requests.get(transcription_url, auth=(account_sid, auth_token))
    if int(transcription.duration) < 20:
        print("Recording is too short, check for issues or rerun.")
    # Save date and duration of transcription in file name
    file_name = transcription.date_created.strftime('%Y-%m-%d') + '-' + transcription.duration + 'sec-' + transcription.sid + '.txt'
    with open(f'transcriptions/{file_name}', 'w') as f:
        f.write(transcription_response.text)
    print(f'Downloaded transcription {file_name}')



