import time
import os
from dotenv import load_dotenv
from google import genai
from IPython.display import Markdown

load_dotenv()
client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

def process_video(fileLocation, userInput):
    # If an upload reference exists, it can be used; otherwise, upload the file.
    uploadVideo = None  # Set to a URL if already uploaded; else, None to upload the file.
    video_file = None

    if uploadVideo:
        print("Using previously uploaded file...")
        video_file = uploadVideo
    else:
        print("Uploading file...")
        video_file = client.files.upload(file=fileLocation)
        print(f"Completed upload: {video_file.uri}")

        # Wait until the file is processed.
        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)
        print('Done')

    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=[
            video_file,
            f"""
            - You are a movie director.
            - The video has already been shot and now you are tasked to change the script of a movie.
            - First and foremost, you need to understand the video completely.
            - Once you are done completely understanding the video, you will need to change the script according to the input i give you wrapped in triple colons(:).
            - take you time and think about my input and how i want to change the script.
            - IF THE OUTPUT IS GREAT YOU WILL BE REWARDED WITH A HUGE BONUS.
            
            In output, I want 4 things from you
            1. Summarize this video.
            2. Give me the changes you are thinking to put in the script based on my input.
            3. Give me scene by scene description of the video that can be used to generate a new video. Each scene should be atmax 2 seconds long. you can create multiple scenes.
            4. Give me the updated/modified script of the video. THIS OUTPUT SHOULD STICTLY BE A JSON OBJECT WITH KEY AS 'scenes' WHICH IS AN ARRAY OF THE scenes! DO NOT CHANGE THE KEY NAME. DO NOT SEND THIS POINT'S OUTPUT OTHER THAN THIS FORMAT. ARRAY ELEMENT WILL BE TEXT ONLY OF THE SCENE. EACH SCENE SHOULD BE VERY DETAILED. EVERY SINGLE DETAIL TO BE ADDED. SCENE TEXT SHOULD BE ATLEAST 40 WORDS LONG. EACH SCENE'S DESCRIPTION SHOULD BE CONNECTED TO ONE ANOTHER SO WE CAN TRANSITION DURING THE GENERATION OF THE VIDEO. THIS CAN BE SKIPPED IF AND ONLY IF THE CURRENT SCENE HAS NO RELATION TO ITS PREVIOUS SCENE.
            
            ::: {userInput} :::
            """
        ]
    )
    print(response.text)
    # Markdown(response.text)
    return response.text