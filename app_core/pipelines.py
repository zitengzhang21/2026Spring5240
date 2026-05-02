"""Model-loading and generation helpers.

All heavy Hugging Face pipelines live here so the UI layer stays focused on flow.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Tuple

import numpy as np
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
    """Convert the finished story into speech.

    To make the narration sound more natural, this function splits the story into
    sentences, generates audio for each sentence, and inserts a short silence
    between them before joining everything back together.
    """
    audio_pipeline = load_audio_pipeline()
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", story.strip())
        if sentence.strip()
    ]
    if not sentences:
        sentences = [story.strip()]

    audio_segments = []
    sample_rate = None
    silence = None

    for index, sentence in enumerate(sentences):
        audio_result = audio_pipeline(sentence)
        current_rate = audio_result["sampling_rate"]
        current_audio = np.array(audio_result["audio"]).squeeze().astype(np.float32)

        if sample_rate is None:
            sample_rate = current_rate
            silence_length = int(sample_rate * 0.5)
            silence = np.zeros(silence_length, dtype=np.float32)

        audio_segments.append(current_audio)
        if index < len(sentences) - 1 and silence is not None:
            audio_segments.append(silence)

    combined_audio = np.concatenate(audio_segments)
    return combined_audio, sample_rate
