"""Story-related helper functions.

This module keeps all text rules in one place so the app logic stays readable.
"""

from __future__ import annotations

import re

from app_core.config import MIN_STORY_WORDS


def build_story_prompt(
    caption: str,
    lesson_theme: str,
    mood: str,
    word_target: int,
    child_name: str,
) -> str:
    """Build a short, instruction-focused prompt for the story model."""
    # Add the optional child name only when the user provides one.
    child_part = (
        f"The main child character is named {child_name}. " if child_name.strip() else ""
    )
    return (
        "Write one short children's story in simple English for ages 3 to 5. "
        f"{child_part}"
        f"Use about {word_target} words. "
        f"The mood should feel {mood}. "
        f"The story should gently teach {lesson_theme}. "
        "Make the story safe, warm, easy to understand, and fun to hear aloud. "
        "Do not list instructions. Return only the story. "
        f"Image description: {caption}"
    )


def normalize_story(text: str) -> str:
    """Clean model output so the UI always receives tidy text."""
    cleaned = text.replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"^(story|output|title)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" \"'")


def trim_story_to_limit(story: str, max_words: int) -> str:
    """Trim overly long generations while keeping the ending natural enough."""
    words = story.split()
    if len(words) <= max_words:
        return story

    trimmed = " ".join(words[:max_words]).rstrip(",;:")
    if not trimmed.endswith((".", "!", "?")):
        trimmed += "."
    return trimmed


def build_fallback_story(caption: str, lesson_theme: str, child_name: str) -> str:
    """Return a safe backup story when the text model behaves poorly."""
    hero = child_name.strip() or "a little friend"
    fallback = (
        f"One sunny day, {hero} saw {caption}. "
        f"{hero.capitalize()} smiled and took a gentle step closer. "
        "The world felt bright, calm, and full of wonder. "
        f"Soon, a tiny adventure began, and everyone practiced {lesson_theme} together. "
        "By the end, the friends felt proud, safe, and ready for another happy day."
    )
    return normalize_story(fallback)


def is_valid_story(story: str) -> bool:
    """Reject prompt-echoes, repeated loops, and very short outputs."""
    invalid_markers = [
        "use simple",
        "return only the story",
        "image description",
        "the story should gently teach",
        "do not list instructions",
        "write one short children's story",
        "main child character",
    ]
    lowered = story.lower()
    if any(marker in lowered for marker in invalid_markers):
        return False

    words = story.split()
    if len(words) < MIN_STORY_WORDS:
        return False

    unique_ratio = len({word.lower().strip(".,!?") for word in words}) / max(
        len(words), 1
    )
    if unique_ratio < 0.45:
        return False

    repeated_chunks = [
        "they are sitting on a bench",
        "in a park",
        "in the sandbox",
    ]
    if any(lowered.count(chunk) >= 3 for chunk in repeated_chunks):
        return False

    return True


def generate_image_title(caption: str, lesson_theme: str) -> str:
    """Turn the caption into a short title for the uploaded image/story card."""
    # Remove very common filler words so the title focuses on key image objects.
    stop_words = {
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "with",
        "and",
        "at",
        "to",
        "for",
        "is",
        "are",
    }
    words = re.findall(r"[A-Za-z]+", caption.lower())
    keywords = [word for word in words if word not in stop_words][:3]
    if not keywords:
        keywords = ["happy", "little", "adventure"]

    title_bits = [word.capitalize() for word in keywords]
    suffix = lesson_theme.capitalize()
    return " ".join(title_bits + [suffix, "Story"])
