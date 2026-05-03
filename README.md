## Story Garden

Story Garden is a Streamlit app that turns a child-friendly image into:

- a short title
- a mini story for ages 3 to 5
- a read-aloud audio version

The app is designed for the ISOM5240 assignment and focuses on a simple user flow, modular code structure, and a child-safe storytelling style.

## Features

- Upload an image or take a photo with the camera
- Generate an image caption automatically
- Turn the caption into a 50-100 word children's story
- Choose a lesson theme such as kindness, sharing, curiosity, courage, or friendship
- Choose a story mood such as playful, gentle, funny, calm, or bedtime
- Generate read-aloud audio from the story
- Insert short pauses between sentences so the narration sounds more natural
- Highlight the approximate current word while the audio is playing
- Control playback speed with 0.5x, 1x, 1.5x, and 2x buttons

## Project Structure

```text
2026Spring5240-git/
|- app.py
|- requirements.txt
|- README.md
|- app_core/
|  |- __init__.py
|  |- audio_utils.py
|  |- config.py
|  |- pipelines.py
|  |- story_utils.py
|  |- ui.py
```

## Main Files

- `app.py`: Streamlit entry point and top-level app flow
- `app_core/config.py`: shared settings such as model names and word limits
- `app_core/pipelines.py`: image captioning, story generation, audio generation, and file handling
- `app_core/story_utils.py`: prompt design, story cleanup, fallback story logic, and title generation
- `app_core/audio_utils.py`: WAV conversion and custom audio player with transcript highlighting
- `app_core/ui.py`: sidebar controls, page layout, and custom styles

## Models Used

- Image captioning: `Salesforce/blip-image-captioning-base`
- Story generation: `google/flan-t5-small`
- Text-to-speech: `Matthijs/mms-tts-eng`

## Requirements

- Python 3.11 recommended
- Streamlit
- Transformers
- Torch
- Pillow
- SentencePiece
- Accelerate
- NumPy

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run the App Locally

```bash
streamlit run app.py
```

After the app opens in the browser:

1. Upload an image or take a photo.
2. Choose a lesson theme and story mood.
3. Adjust the target story length if needed.
4. Click `Create story and audio`.

## Deployment

This project is intended to be deployed on Streamlit Cloud.

Recommended deployment settings:

- Repository: your GitHub repository
- Branch: `main`
- Main file path: `app.py`

## Notes for the Assignment

This project was organized into multiple Python files for better readability and modularity. Because of that, the app does not rely on `app.py` alone. The `app_core` folder is also required for the application to run correctly.

## What to Submit

For the assignment, the safe submission package should include:

- `app.py`
- `requirements.txt`
- the full `app_core/` folder
- `README.md`
- the Streamlit Cloud URL

If your instructor asks for a zip file or source package, include all source files above in the same project folder.

## Suggested Final Submission Checklist

- The app runs locally without errors
- The app is deployed successfully on Streamlit Cloud
- The Streamlit link is accessible
- All required Python files are included
- `requirements.txt` is up to date
- `README.md` explains the project clearly
