import os
import io
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

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


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Different transcripts to try
# transcript = "Transferring to jury services, Please listen to the entire message for important tre, service information. As some options have changed, although you will hear a beep after this message, please do not leave a voice mail if we are unable to retrieve these at this time. Instead, please email us at info dot jerry services at fulton County, ga dot gov. You can also request a deferral or excusal, upload documents, and opt in to receive techs and E mails by scanning the q r code or typing in the you are url and Blue under summons. At fulton courts dot j teacher access dot com. This message is for jurors scheduled for service. On Wednesday, march 19th, 2025. At 8 30 AM groups one and 2. You must report groups 3 through 10 are not required to report groups 3 through 10 years service is excused and there is nothing further you need to groups one and 2 must report at 8 30 AM to the jury assembly room located on the 7th floor of the justice center tower at 185 central avenue, Southwest atlanta, Georgia, 30303. Please complete your online questionnaire before you report for service by scanning the q r code on your summons. Free parking is provided for jurors at the red and yellow lights at 593 central avenue, Southwest atlanta, Georgia, 30312. Gerry services does not validate paid parking please. So your parking pass included with your summons or visit fulton court dot org for directions and parking information. There's a free fulton County shuttle service that will bring you to the justice center tower from the red and yellow parking lots. Jos using marta should go to w W."
# transcript = "To be transferring to jury services Please listen to the entire message for an important geri service information. And some options have changed. Although you will hear beat afterthis message. Please do not leave a voice mail if we are unable to retrieve the use at this time. Instead, please email us at info dot jerry services at fulton County, ga dot G O V. You can also request a deferral or excusal, upload documents and opt in to receive techs and emails by scanning the q r code or typing in the U R L in blue on your findings. At fulton courts dot G p g R A S S dot com. This message is for juris scheduled for service. On Thursday, march 20th 2025 at 8 30 AM. Groups 2 and 3. You must report. Group one and 4 through 10 are not required to report. Group one and 4 through 10. Your service is excused and there was nothing further you need to do. Group 2 and 3 must report at 8 30 AM. So the drury assembly room, located on the 7th floor of the justice center tower at 185 central avenue, Southwest atlanta, Georgia, 30303. Please complete your online questionnaire before you report for service by scanning the q r code on your assignments. Free parking is provided for tourist at the red and yellow lights at 593. Central avenue, Southwest atlanta, Georgia, 303. 12. Gerry services does not validate paid for."
transcript = "Transferring to jury services Please listen to this entire message for important, gerry service information I some options have changed. Although you will hear a beep after this message, please did not leave voice mails as we are unable to retrieve them at this time. Instead, please email us at info dot jerry services at fulton County, ga dot com. You can also request a deferral or excusal, upload documents, an opt in to receive text and emails by scanning the q r code or typing the U R L in blue under simmons at fulton court dot ga peacher access dot com. This message is for drew, scheduled for service. On March, 13th, 2025. At 8, 30 AM groups 2 and 3. You must report groups one and 4 through 12. You are not required to report groups one and 4 through 12, your services, excused. And there's nothing further you need to do. Good 2 and 3 must report at 8 30 AM to the jury assembly room. Located on the 7th floor at the justice center tower. At 185 central avenue, Southwest atlanta, Georgia, 30303. Please complete your online questionnaire before you report for service by scanning the q r code on your southern free parking is provided for jurors at the red and yellow locked at 593 central avenue, Southwest atlanta, Georgia, 30312, to re services does not validate paid parking. Please see your parking pass included in your statements or visit fulton court dot org for directions and parking information. There's a free fulton County shuttle service that will bring you from the justice center tower to the red and yellow parking lot. And the red and yellow parking lots to the justice center tower. Jose using marta should go to w W. W dot. It's smarter, dot com for more information. Again, this message is for juris scheduled for march 3rd."

output = extract_group_data(transcript, OPENAI_API_KEY)
print(output)