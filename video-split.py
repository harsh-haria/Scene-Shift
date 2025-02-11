# take a input of a file which will be a video file, split the entire video in frames and then store the frames in a folder
# The folder will be created in the same directory as the video file and will have the same name as the video file along with the frame rate of the video
# The frames will be stored in the folder with the name of the frame and the timestamp of the frame

import cv2
import os
import sys
from datetime import timedelta
from urllib.parse import urlparse
import yt_dlp
import webvtt

# Define directory structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, 'downloaded_videos')
SPLITS_DIR = os.path.join(SCRIPT_DIR, 'splits')
SUBTITLES_DIR = os.path.join(SCRIPT_DIR, 'subtitles')

def ensure_directories():
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    os.makedirs(SPLITS_DIR, exist_ok=True)
    os.makedirs(SUBTITLES_DIR, exist_ok=True)

def is_youtube_url(url):
    try:
        parsed = urlparse(url)
        return 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc
    except:
        return False

def download_youtube_video(url):
    ensure_directories()
    video_id = url.split('watch?v=')[-1] if 'watch?v=' in url else url.split('/')[-1]
    output_path = os.path.join(DOWNLOADS_DIR, f'{video_id}.mp4')
    subtitle_path = os.path.join(SUBTITLES_DIR, f'{video_id}.en.vtt.en.vtt')
    
    if os.path.exists(output_path) and os.path.exists(subtitle_path):
        print(f"Video and subtitles already downloaded: {output_path}")
        return output_path, video_id
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'outtmpl': {
            'default': output_path,
            'subtitle': subtitle_path
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return output_path, video_id

def sanitize_filename(filename):
    # Replace invalid filename characters
    invalid_chars = [':', '/', '\\', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def load_subtitles(video_id):
    subtitle_path = os.path.join(SUBTITLES_DIR, f'{video_id}.en.vtt.en.vtt')
    print("subtitle path is: ",subtitle_path)
    if not os.path.exists(subtitle_path):
        print(f"Error: Subtitle file {subtitle_path} does not exist")
        return []
    
    subtitles = []
    for caption in webvtt.read(subtitle_path):
        start = timedelta(hours=int(caption.start[:2]), minutes=int(caption.start[3:5]), seconds=float(caption.start[6:]))
        end = timedelta(hours=int(caption.end[:2]), minutes=int(caption.end[3:5]), seconds=float(caption.end[6:]))
        subtitles.append((start, end, caption.text))
    
    return subtitles

def extract_frames(video_path):
    ensure_directories()
    
    target_fps = 10  # Set target FPS
    
    if is_youtube_url(video_path):
        print("Downloading YouTube video...")
        video_path, video_id = download_youtube_video(video_path)
        video_filename = f"youtube_{video_id}"
        subtitles = load_subtitles(video_id)
    else:
        if not os.path.exists(video_path):
            print(f"Error: File {video_path} does not exist")
            return
        video_filename = os.path.splitext(os.path.basename(video_path))[0]
        subtitles = []

    output_dir = os.path.join(SPLITS_DIR, video_filename)
    # if os.path.exists(output_dir) and os.listdir(output_dir):
    #     print(f"Splits already exist for video: {output_dir}")
    #     return
    
    os.makedirs(output_dir, exist_ok=True)

    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    original_fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame skip rate
    skip_rate = max(1, round(original_fps / target_fps))
    print(f"Original FPS: {original_fps}, Target FPS: {target_fps}, Skip rate: {skip_rate}")

    frame_number = 0
    saved_frame_count = 0

    while True:
        success, frame = video.read()
        if not success:
            break

        # Process only frames that match target FPS
        if frame_number % skip_rate == 0:
            try:
                if frame is None or frame.size == 0:
                    print(f"Invalid frame data at frame {frame_number}")
                    continue
                
                # Calculate correct timestamp based on video time
                timestamp = timedelta(seconds=(frame_number / original_fps))
                safe_timestamp = str(timestamp).replace(":", "_")
                output_path = os.path.join(output_dir, f"frame_{safe_timestamp}.jpg")
                
                if cv2.imwrite(output_path, frame):
                    saved_frame_count += 1
                    if saved_frame_count % 10 == 0:
                        print(f"Saved {saved_frame_count} frames at {target_fps} FPS")
                    
                    # Associate frame with subtitle
                    for start, end, text in subtitles:
                        if start <= timestamp <= end:
                            subtitle_output_dir = os.path.join(output_dir, 'subtitles')
                            os.makedirs(subtitle_output_dir, exist_ok=True)
                            subtitle_output_path = os.path.join(subtitle_output_dir, f"frame_{safe_timestamp}.txt")
                            with open(subtitle_output_path, 'w') as subtitle_file:
                                subtitle_file.write(text)
                            break
                else:
                    print(f"Failed to save frame {frame_number}")
                    
            except Exception as e:
                print(f"Error processing frame {frame_number}: {str(e)}")

        frame_number += 1

    video.release()
    print(f"Complete! Saved {saved_frame_count} frames at {target_fps} FPS (processed {frame_number} frames)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python video-split.py <video_file_or_youtube_url>")
        sys.exit(1)
    
    extract_frames(sys.argv[1])
