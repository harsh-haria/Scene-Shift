import time
import os
from dotenv import load_dotenv
from google import genai
from IPython.display import Markdown

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

# (Optional) Mention your uploaded video file here. If you don't have one, the script will upload it for you.
uploadVideo = "https://generativelanguage.googleapis.com/v1beta/files/<xyz>"
uplaodVideo = None # becuase we are uploading the video. Remove this line if already uploaded.

video_file = None

fileLocation = "/path/to/your/video.mp4"

if 'uploadVideo' in globals() and uploadVideo:
    print("Using previously uploaded file...")
    video_file = uploadVideo
else:
    print("Uploading file...")
    video_file = client.files.upload(file=fileLocation)
    print(f"Completed upload: {video_file.uri}")

    # Check whether the file is ready to be used.
    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(1)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    print('Done')

# Pass the video file reference like any other media part.
response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=[
        video_file,
        """
            - You are a movie director.
            - The video has already been shot and now you are tasked to change the script of a movie.
            - First and foremost, you need to understand the video completely.
            - Once you are done with completely understanding the video, you will need to change the script according to the input i give you wrapped in triple colons(:).
            - take you time and think about my input and how i want to change the script.
            - IF THE OUTPUT IS GREAT YOU WILL BE REWARDED WITH A HUGE BONUS.
            
            In output, I want 4 things from you
            1. Summarize this video.
            2. Give me the changes you are thinking to put in the script based on my input.
            3. Give me scene by scene description of the video that can be used to generate a new video. Each scene should be atmax 2 seconds long. you can create multiple scenes.
            4. Give me the updated/modified script of the video. THIS OUTPUT SHOULD STICTLY BE A JSON OBJECT WITH KEY AS 'scenes' WHICH IS AN ARRAY OF THE scenes! DO NOT CHANGE THE KEY NAME. DO NOT SEND THIS POINT'S OUTPUT OTHER THAN THIS FORMAT. ARRAY ELEMENT WILL BE TEXT ONLY OF THE SCENE. EACH SCENE SHOULD BE VERY DETAILED. EVERY SINGLE DETAIL TO BE ADDED. SCENE TEXT SHOULD BE ATLEAST 40 WORDS LONG. EACH SCENE'S DESCRIPTION SHOULD BE CONNECTED TO ONE ANOTHER SO WE CAN TRANSITION DURING THE GENERATION OF THE VIDEO. THIS CAN BE SKIPPED IF AND ONLY IF THE CURRENT SCENE HAS NO RELATION TO ITS PREVIOUS SCENE.

            ::: here the video shows that the person just passes a day in and out. Not doing anything productive. Although i want you to change the script in a way that the person realises that there is more to just passing days in life and starts doing something meaningful. :::
        """
    ]
)

print(response.text)

# Print the response, rendering any Markdown
Markdown(response.text)