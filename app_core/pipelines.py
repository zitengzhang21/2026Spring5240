"""Model-loading and generation helpers.

All heavy Hugging Face pipelines live here so the UI layer stays focused on flow.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Tuple

import streamlit as st
from transformers import pipeline

from app_core.config import AUDIO_MODEL_NAME, CAPTION_MODEL_NAME, STORY_MODEL_NAME
from app_core.story_utils import (
    build_fallback_story,
    build_story_prompt,
    is_valid_story,
    normalize_story,
    trim_story_to_limit,
)


@st.cache_resource(show_spinner=False)
def load_caption_pipeline():
    """Load the image captioning model once per Streamlit server."""
    return pipeline("image-to-text", model=CAPTION_MODEL_NAME)


@st.cache_resource(show_spinner=False)
def load_story_pipeline():
    """Load the text generation model once per Streamlit server."""
    return pipeline("text2text-generation", model=STORY_MODEL_NAME)


@st.cache_resource(show_spinner=False)
def load_audio_pipeline():
    """Load the TTS model once per Streamlit server."""
    return pipeline("text-to-audio", model=AUDIO_MODEL_NAME)


def save_uploaded_file(uploaded_file) -> Path:
    """Store the uploaded image in a temporary file for model inference."""
    suffix = Path(uploaded_file.name).suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def generate_image_caption(image_path: Path) -> str:
    """Generate a short factual caption from the image."""
    caption_pipeline = load_caption_pipeline()
    result = caption_pipeline(str(image_path))
    return result[0]["generated_text"].strip()


def generate_story_from_caption(
    caption: str,
    lesson_theme: str,
    mood: str,
    word_target: int,
    child_name: str,
    max_words: int,
) -> str:
    """Generate a child-friendly story and fall back if the model output is weak."""
    story_pipeline = load_story_pipeline()
    prompt = build_story_prompt(caption, lesson_theme, mood, word_target, child_name)
    result = story_pipeline(
        prompt,
        max_new_tokens=170,
        min_new_tokens=70,
        do_sample=True,
        temperature=0.9,
        top_p=0.95,
    )

    story = normalize_story(result[0]["generated_text"])
    story = trim_story_to_limit(story, max_words=max_words)
    if not is_valid_story(story):
        story = build_fallback_story(caption, lesson_theme, child_name)
        story = trim_story_to_limit(story, max_words=max_words)
    return story


def generate_audio(story: str) -> Tuple[object, int]:
    """Convert the finished story into speech."""
    audio_pipeline = load_audio_pipeline()
    audio_result = audio_pipeline(story)
    return audio_result["audio"], audio_result["sampling_rate"]
