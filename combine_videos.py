import os
from moviepy import VideoFileClip, concatenate_videoclips

# Directory where individual videos are stored
VIDEOS_DIR = os.path.join(os.getcwd(), "videos")
# Output combined video path
OUTPUT_VIDEO = os.path.join(os.getcwd(), "combined_video.mp4")

def get_video_files(directory):
    # Get all mp4 files, sorted by name (adjust as needed)
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".mp4")]
    return sorted(files)

def combine_videos():
    video_files = get_video_files(VIDEOS_DIR)
    if not video_files:
        print("No video files found in", VIDEOS_DIR)
        return

    clips = []
    for video_file in video_files:
        print("Loading", video_file)
        clip = VideoFileClip(video_file)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(OUTPUT_VIDEO, codec="libx264")
    
    # Cleanup clips
    for clip in clips:
        clip.close()
    final_clip.close()
    print("Combined video saved to:", OUTPUT_VIDEO)

if __name__ == "__main__":
    combine_videos()
