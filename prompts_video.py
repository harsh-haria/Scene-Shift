import os
import torch
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video

from combine_videos import combine_videos 

pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")
pipe.enable_model_cpu_offload()

# memory optimization
pipe.enable_vae_slicing()

def export_videos(prompts):
    # Create a directory to store the videos
    os.makedirs("videos", exist_ok=True)
    
    # Loop through the prompts and generate a video for each one
    for i, prompt in enumerate(prompts):
        print(f"Generating video for prompt {i + 1}...")
        video_frames = pipe(prompt, num_inference_steps=25).frames[0]
        output_path = os.path.join("videos", f"video_{i + 1}.mp4")
        export_to_video(video_frames, output_path)
        print(f"Video saved to: {output_path}")
    
    combine_videos()

