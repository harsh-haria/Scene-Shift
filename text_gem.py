import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GENAI_API_KEY'))

content = """
    You are a movie director.
    You are tasked to change the script of a movie.
    The video of the movie is broken down into frames.
    You will be provided the description of each frame in text form wrapped in triple semi-colons(;). It is an python array so you will have '[' and ']' at the start and end of the text. Each frame's description will be seperated by a comma.
    You need to understand each frame's description and understand the story that has been put together.
    Each frame's description will be provided.
    MAKE SURE YOU DO NOT CHANGE THE CONTEXT OF THE STORY. KEEP THE CHARACTERS SAME AND THE PLOT(Unless requested not to) SAME AS WELL. JUST CHANGE THE SCRIPT.
    You need to keep in mind a few things:
    - The desciption provided by each frame are computer generated so they might not be very accurate already. So we need to be very careful while understanding. Do take multiple frames into consideration to understand the story or a scene.
    - There is a possibility where the video's FPS was reduced for better performance. Be mindfull of that too.
    - There is also a posibility that the frame could be something and the text description of that frame is absoluetly completely different from what it actually is. For Example 1,2,3 frames are similar and belong to one scene and 4 is something not releated to the previous 3 frames. Then again from 5 we get frames in alignment with 1, 2 and 3. So there could be outliers too in the frame descriptions. In such cases, try to fill in without changing the context of the story. Add very little as possible. We want to keep the story as original as possible.
    - The video might have multiple scenes. You will need to understand the scenes and the transitions between them.
    - Since you are getting description of frames of the video, the description of consecutive or previous frames might be related to the current frame. For example, the video shows a person waving. So the current frame will be like a person showing high five pose and the next frame might be almost identical to the current frame but only with slight change where the motion of the hand would be.
    - if the description of a bunch of frames is similar you can consider them as one single scene. For example, a man waving might have multiple frames but the description might be the same or similar. You will need to understand this as well.
    - After the grouping of the frames, you will need to understand what is happening in the video.
    - Once you are done with completely understanding the video, you will need to change the script according to this user input that is wrapped in triple colons(:).
    - take you time and think about the user input and how the user wants to change the script.
    - DO NOT HURRY IN ANY STEP OR YOU WILL NOT BE REWARDED.
    - Make changes to the script according to you.
    - Now once your updated script is ready, split the script into scenes.
    - Once you have all the scenes, now split them into sections that will be at max 2 seconds long.
    - Each section will be seperated by a line break.
    - return 4 things, First what you understand from the video, second how you have changed the new script, third, What changes did you have to make to the original scirpt to understand it if it was not very informatiev and the fourth, updated scripts seperated to be made into a video.

    ;;;
        [
            # Description of each frame seperated by commas
            (example), (example2), (example3)
        ]
    ;;;

    ::: <User Input> :::

"""

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents = content,
)

print(response.text)