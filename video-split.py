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
from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering

# Force selection of the dedicated NVIDIA GPU by setting environment variables.
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"  # Ensure only the dedicated GPU is visible

import torch  # Import torch after setting environment variables

# Removed torch.cuda.set_device(0) to avoid AttributeError.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if device.type == "cuda":
    print("Using dedicated GPU:", torch.cuda.get_device_name(device))
else:
    print("Dedicated GPU not available, using CPU.")

# Define directory structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, 'downloaded_videos')
SPLITS_DIR = os.path.join(SCRIPT_DIR, 'splits')
SUBTITLES_DIR = os.path.join(SCRIPT_DIR, 'subtitles')

# Initialize the annotation model and processor once.
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
model.to(device)  # Move the model to GPU if available

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
    subtitle_template = os.path.join(SUBTITLES_DIR, f'{video_id}')
    
    expected_subtitle = subtitle_template + ".vtt"
    if os.path.exists(output_path) and os.path.exists(expected_subtitle):
        print(f"Video and subtitles already downloaded: {output_path}")
        return output_path, video_id
    
    ydl_opts = {
        'format': 'bestvideo/best',
        'outtmpl': output_path,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'outtmpl': {
            'default': output_path,
            'subtitle': subtitle_template
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
    subtitle_path = os.path.join(SUBTITLES_DIR, f'{video_id}.en.vtt')
    if not os.path.exists(subtitle_path):
        print(f"Error: Subtitle file {subtitle_path} does not exist")
        return []
    
    subtitles = []
    for caption in webvtt.read(subtitle_path):
        start = timedelta(hours=int(caption.start[:2]), minutes=int(caption.start[3:5]), seconds=float(caption.start[6:]))
        end = timedelta(hours=int(caption.end[:2]), minutes=int(caption.end[3:5]), seconds=float(caption.end[6:]))
        subtitles.append((start, end, caption.text))
    
    return subtitles

def annotate_frame(frame_path, prompt="Give a detailed description of what is happening in this scene."):
    image = Image.open(frame_path).convert("RGB")
    # Prepare inputs with the question/prompt
    inputs = processor(
        image, 
        prompt,
        return_tensors="pt"
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    output = model.generate(
        **inputs,
        max_length=100,
        num_beams=8,        # Increased from 4 to 8 for better quality
        min_length=20,
        temperature=1.0,    # Added temperature to control randomness
        early_stopping=True
    )
    
    description = processor.decode(output[0], skip_special_tokens=True)
    return description

def extract_frames(video_path, annotation_prompt=None):
    ensure_directories()
    
    target_fps = 8  # Set target FPS
    
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
    
    # Instead of (or in addition to) writing master file, create an annotations array.
    annotations_array = []
    
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
                frame_path = os.path.join(output_dir, f"frame_{safe_timestamp}.jpg")
                
                if cv2.imwrite(frame_path, frame):
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
                    # Generate annotation for the frame.
                    annotation = annotate_frame(frame_path, annotation_prompt or "Give a detailed description of what is happening in this scene.")
                    annotation_output_dir = os.path.join(output_dir, 'annotations')
                    os.makedirs(annotation_output_dir, exist_ok=True)
                    annotation_output_path = os.path.join(annotation_output_dir, f"frame_{safe_timestamp}.txt")
                    with open(annotation_output_path, 'w') as ann_file:
                        ann_file.write(annotation)
                    
                    # Append frame annotation to our array
                    annotations_array.append((f"frame_{safe_timestamp}.jpg", annotation))
                    
                    # (Optional) Also append to a master file if needed.
                else:
                    print(f"Failed to save frame {frame_number}")
                    
            except Exception as e:
                print(f"Error processing frame {frame_number}: {str(e)}")

        frame_number += 1

    video.release()
    print(f"Complete! Saved {saved_frame_count} frames at {target_fps} FPS (processed {frame_number} frames)")
    
    # Import and call a processing function from prompts-video.py with our annotations array.
    try:
        from prompts_video import export_videos
        export_videos(annotations_array)
    except ImportError:
        print("process_annotations function not found in prompts-video.py. Skipping further processing.")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python video-split.py <video_file_or_youtube_url> [annotation_prompt]")
        sys.exit(1)
    
    prompt = sys.argv[2] if len(sys.argv) == 3 else None
    extract_frames(sys.argv[1], prompt)
