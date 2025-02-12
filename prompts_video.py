import os
import torch
import cv2
import numpy as np  # Added import for numpy
from datetime import datetime
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video

from combine_videos import combine_videos 

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the text-to-video pipeline from Hugging Face.
print("Loading text-to-video model...")
model_id = "damo-vilab/text-to-video-ms-1.7b"
pipe = DiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

def export_videos(prompts):
    # Create a directory to store the videos
    os.makedirs("videos", exist_ok=True)
    
    # Loop through the prompts and generate a video for each one
    for i, prompt in enumerate(prompts):
        print(f"Generating video for prompt {i + 1}...")
        video = pipe(prompt, num_inference_steps=30).frames
        output_path = os.path.join("videos", f"video_{i + 1}.mp4")
        export_to_video(video, output_path)
        print(f"Video saved to: {output_path}")
    
    combine_videos()

