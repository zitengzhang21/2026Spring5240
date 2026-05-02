"""Shared configuration values for the Streamlit storytelling app."""

APP_TITLE = "Story Garden"
APP_TAGLINE = "Turn a picture into a story, title, and read-aloud adventure."

MIN_STORY_WORDS = 50
DEFAULT_STORY_WORDS = 70
MAX_STORY_WORDS = 100

SUPPORTED_FILE_TYPES = ["png", "jpg", "jpeg"]
SPEED_OPTIONS = [0.5, 1.0, 1.5, 2.0]

DEFAULT_LESSON = "kindness"
DEFAULT_MOOD = "playful"

CAPTION_MODEL_NAME = "Salesforce/blip-image-captioning-base"
STORY_MODEL_NAME = "google/flan-t5-small"
AUDIO_MODEL_NAME = "Matthijs/mms-tts-eng"
