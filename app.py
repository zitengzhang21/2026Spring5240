import re
import tempfile
from pathlib import Path
from typing import Tuple

import streamlit as st
from transformers import pipeline


APP_TITLE = "Image to Story Audio App"
MIN_STORY_WORDS = 50
MAX_STORY_WORDS = 100
SUPPORTED_FILE_TYPES = ["png", "jpg", "jpeg"]
STORY_MODEL_NAME = "google/flan-t5-small"
CAPTION_MODEL_NAME = "Salesforce/blip-image-captioning-base"
AUDIO_MODEL_NAME = "Matthijs/mms-tts-eng"


@st.cache_resource(show_spinner=False)
def load_caption_pipeline():
    return pipeline("image-to-text", model=CAPTION_MODEL_NAME)


@st.cache_resource(show_spinner=False)
def load_story_pipeline():
    return pipeline("text2text-generation", model=STORY_MODEL_NAME)


@st.cache_resource(show_spinner=False)
def load_audio_pipeline():
    return pipeline("text-to-audio", model=AUDIO_MODEL_NAME)


def save_uploaded_file(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def generate_image_caption(image_path: Path) -> str:
    caption_pipeline = load_caption_pipeline()
    result = caption_pipeline(str(image_path))
    caption = result[0]["generated_text"].strip()
    return caption


def build_story_prompt(caption: str) -> str:
    return (
        f"Write a warm and playful children's story in simple English for ages 3 to 5. "
        f"Use {MIN_STORY_WORDS} to {MAX_STORY_WORDS}. "
        "Make it gentle, safe, easy to understand, and include a small positive lesson "
        "about kindness, sharing, curiosity, or courage. "
        "Do not list instructions. Do not explain. Return only the story. "
        f"Image description: {caption}"
    )


def normalize_story(text: str) -> str:
    cleaned = text.replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r'^(story|output)\s*:\s*', "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" \"'")
    return cleaned


def trim_story_to_limit(story: str, max_words: int = MAX_STORY_WORDS) -> str:
    words = story.split()
    if len(words) <= max_words:
        return story

    trimmed = " ".join(words[:max_words]).rstrip(",;:")
    if not trimmed.endswith((".", "!", "?")):
        trimmed += "."
    return trimmed


def build_fallback_story(caption: str) -> str:
    fallback = (
        f"One sunny day, a little friend saw {caption}. "
        "The friend looked closely, smiled, and took a gentle step forward. "
        "Everything felt bright, calm, and full of wonder. "
        "Soon, a small adventure began with kindness, curiosity, and happy teamwork. "
        "At the end, everyone felt proud, safe, and ready to explore again tomorrow."
    )
    return trim_story_to_limit(normalize_story(fallback))


def is_valid_story(story: str) -> bool:
    invalid_markers = [
        "use simple",
        "return only the story",
        "image description",
        "include a simple positive lesson",
        "keep the tone",
        "do not list instructions",
        "requirements:",
    ]
    lowered = story.lower()
    if any(marker in lowered for marker in invalid_markers):
        return False
    words = story.split()
    if len(words) < MIN_STORY_WORDS:
        return False

    unique_ratio = (
        len({word.lower().strip(".,!?") for word in words}) / max(len(words), 1)
    )
    if unique_ratio < 0.45:
        return False

    repeated_phrase = "they are sitting on a bench"
    if lowered.count(repeated_phrase) >= 2:
        return False

    return True


def generate_story_from_caption(caption: str) -> str:
    story_pipeline = load_story_pipeline()
    prompt = build_story_prompt(caption)
    result = story_pipeline(
        prompt,
        max_new_tokens=140,
        min_new_tokens=70,
        do_sample=True,
        temperature=0.9,
        top_p=0.95,
    )
    story = normalize_story(result[0]["generated_text"])
    story = trim_story_to_limit(story)

    if not is_valid_story(story):
        return build_fallback_story(caption)
    return story


def generate_audio(story: str) -> Tuple[object, int]:
    audio_pipeline = load_audio_pipeline()
    audio_result = audio_pipeline(story)
    return audio_result["audio"], audio_result["sampling_rate"]


def render_intro() -> None:
    st.title("Turn a Picture into a Story")
    st.write(
        "Upload a picture and this app will create a short, child-friendly story "
        "for children aged 3 to 5, then read it aloud."
    )
    st.info(
        "Best results come from clear photos or illustrations with one main scene."
    )


def render_results(caption: str, story: str, audio_array, sample_rate: int) -> None:
    with st.expander("Image caption", expanded=False):
        st.write(caption)

    st.subheader("Story")
    st.write(story)
    st.caption(f"Story length: {len(story.split())} words")

    st.subheader("Audio")
    st.audio(audio_array, sample_rate=sample_rate)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    render_intro()

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=SUPPORTED_FILE_TYPES,
        help="Accepted formats: PNG, JPG, JPEG",
    )

    if uploaded_file is None:
        st.stop()

    st.image(uploaded_file, caption="Uploaded image", use_container_width=True)

    if st.button("Create story and audio", type="primary"):
        temp_image_path = save_uploaded_file(uploaded_file)
        try:
            with st.spinner("Looking at the image..."):
                caption = generate_image_caption(temp_image_path)

            with st.spinner("Writing a child-friendly story..."):
                story = generate_story_from_caption(caption)

            with st.spinner("Creating audio..."):
                audio_array, sample_rate = generate_audio(story)

            render_results(caption, story, audio_array, sample_rate)
        except Exception as error:
            st.error(
                "Something went wrong while generating the story or audio. "
                "Please try another image or run the app again."
            )
            st.exception(error)
        finally:
            temp_image_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
