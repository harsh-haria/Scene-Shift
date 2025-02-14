# Scene Shift Project

## Overview

Scene Shift is a multi-module project for processing and generating videos using AI models. The project includes video splitting, annotation, video generation from text prompts, and video concatenation. The primary interactive interface is provided through the `scene_shift.ipynb` Jupyter Notebook.  
**Note:** An interactive frontend is currently in development.

## File Structure

- **scene_shift.ipynb**: Main notebook with the complete interactive code.
- **video_gem.py**: Processes videos using Google GenAI based on user inputs.
- **video_split.py**: Splits videos into frames and generates annotations.
- **combine_videos.py**: Combines individual video clips into one final video.
- **prompts-video.py**: Generates videos from text prompts using a diffusion pipeline.
- **text_to_video.py**: Converts detailed text descriptions into video clips.
- **requirements.txt**: Lists all Python package dependencies.

## Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd Scene-Shift
   ```
2. **Create a Virtual Environment and Install Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**
   Create a `.env` file in the project root and add your API keys, for example:
   ```
   GENAI_API_KEY=your_genai_api_key_here
   ```

## Usage

- **Interactive Mode:**  
  Open `scene_shift.ipynb` in Jupyter Notebook to run and test all project functionalities interactively.

- **Command-line Mode:**  
  You can run individual scripts. For example, to process a video using GenAI:
  ```bash
  python video_gem.py <file_location> "<user_input>"
  ```
  Replace `<file_location>` with the path or URL to your video and `<user_input>` with your text input.

## Contributing

Contributions are welcome! Feel free to fork the repository, work on enhancements, and submit pull requests.

## License

This project is licensed under the MIT License.
