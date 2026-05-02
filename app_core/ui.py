"""UI helpers for the Streamlit storytelling app."""

from __future__ import annotations

import streamlit as st

from app_core.config import (
    APP_TAGLINE,
    APP_TITLE,
    DEFAULT_LESSON,
    DEFAULT_MOOD,
    DEFAULT_STORY_WORDS,
    MAX_STORY_WORDS,
    MIN_STORY_WORDS,
    SUPPORTED_FILE_TYPES,
)


def apply_app_styles() -> None:
    """Inject custom CSS so the app feels more playful and less default."""
    st.markdown(
        """
        <style>
          .stApp {
            background:
              radial-gradient(circle at top left, rgba(255, 224, 138, 0.65), transparent 28%),
              radial-gradient(circle at top right, rgba(122, 207, 255, 0.28), transparent 24%),
              linear-gradient(180deg, #fff8ec 0%, #fff2d2 42%, #f7fbff 100%);
          }
          .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1100px;
          }
          .hero-card {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(255, 190, 75, 0.35);
            border-radius: 28px;
            padding: 1.5rem 1.5rem 1rem 1.5rem;
            box-shadow: 0 24px 60px rgba(80, 58, 13, 0.12);
            backdrop-filter: blur(8px);
          }
          .hero-badges {
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
            margin-bottom: 0.85rem;
          }
          .hero-badge {
            display: inline-block;
            background: #fff0bf;
            color: #7c4b00;
            border-radius: 999px;
            padding: 0.35rem 0.72rem;
            font-weight: 700;
            font-size: 0.92rem;
          }
          .hero-title {
            font-size: 2.5rem;
            line-height: 1.05;
            color: #7b4300;
            margin: 0 0 0.5rem 0;
            font-weight: 800;
          }
          .hero-text {
            color: #594220;
            font-size: 1.02rem;
            margin-bottom: 0.2rem;
          }
          .section-card {
            background: transparent;
            border-radius: 0;
            padding: 0;
            border: none;
            box-shadow: none;
          }
          .story-card {
            background: transparent;
            border-radius: 0;
            padding: 0;
            border: none;
            box-shadow: none;
          }
          .result-title {
            color: #8a4d00;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.4rem;
          }
          .soft-note {
            color: #75542b;
            font-size: 1rem;
          }
          .story-body {
            color: #3b2a15;
            font-size: 1.04rem;
            line-height: 1.9;
            margin-bottom: 1rem;
          }
          .story-meta {
            color: #8a7b61;
            font-size: 0.95rem;
            margin-top: 0.2rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_intro() -> None:
    """Render the top hero area with a friendlier, more child-focused look."""
    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-badges">
            <span class="hero-badge">&#127752; Kid-Friendly</span>
            <span class="hero-badge">&#128214; Story + Title</span>
            <span class="hero-badge">&#128266; Read-Aloud Audio</span>
          </div>
          <div class="hero-title">{APP_TITLE}</div>
          <p class="hero-text">{APP_TAGLINE}</p>
          <p class="hero-text">Upload a picture or take a photo, and the app will turn it into a playful mini story for ages 3 to 5.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls():
    """Collect all creator options from the sidebar."""
    with st.sidebar:
        st.markdown("## Story Controls")
        input_mode = st.radio(
            "Choose image source",
            options=["Upload image", "Take photo"],
            help="Use upload for saved pictures, or use the camera for a live photo.",
        )
        lesson_theme = st.selectbox(
            "Lesson theme",
            options=["kindness", "sharing", "curiosity", "courage", "friendship"],
            index=["kindness", "sharing", "curiosity", "courage", "friendship"].index(
                DEFAULT_LESSON
            ),
        )
        mood = st.selectbox(
            "Story mood",
            options=["playful", "gentle", "funny", "calm", "bedtime"],
            index=["playful", "gentle", "funny", "calm", "bedtime"].index(DEFAULT_MOOD),
        )
        word_target = st.slider(
            "Story length target",
            min_value=MIN_STORY_WORDS,
            max_value=MAX_STORY_WORDS,
            value=DEFAULT_STORY_WORDS,
            step=5,
        )
        child_name = st.text_input(
            "Optional child character name",
            placeholder="For example: Mia",
        )

    return {
        "input_mode": input_mode,
        "lesson_theme": lesson_theme,
        "mood": mood,
        "word_target": word_target,
        "child_name": child_name,
    }


def render_image_input(input_mode: str):
    """Render either the uploader or the camera input based on the user choice."""
    if input_mode == "Upload image":
        return st.file_uploader(
            "Choose an image",
            type=SUPPORTED_FILE_TYPES,
            help="Accepted formats: PNG, JPG, JPEG",
        )

    return st.camera_input("Take a photo")


def render_result_header(image_title: str, caption: str) -> None:
    """Render the generated title and the caption summary."""
    cleaned_caption = caption.strip()
    if cleaned_caption:
        cleaned_caption = cleaned_caption[0].upper() + cleaned_caption[1:]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="result-title">&#10024; {image_title}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="soft-note">{cleaned_caption}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def open_story_card() -> None:
    """Open the main story result container."""
    st.markdown('<div class="story-card">', unsafe_allow_html=True)


def close_story_card() -> None:
    """Close the main story result container."""
    st.markdown("</div>", unsafe_allow_html=True)
