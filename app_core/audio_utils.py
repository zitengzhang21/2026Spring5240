"""Audio helper functions for the storytelling app."""

from __future__ import annotations

import base64
import html
import io
import json
import wave

import numpy as np
import streamlit.components.v1 as components


def audio_array_to_wav_bytes(audio_array, sample_rate: int) -> bytes:
    """Convert model output into WAV bytes so we can build a custom HTML player."""
    samples = np.array(audio_array).squeeze()
    samples = np.clip(samples, -1.0, 1.0)
    pcm16 = (samples * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16.tobytes())
    return buffer.getvalue()


def render_audio_story_player(
    story: str,
    wav_bytes: bytes,
    word_count: int,
) -> None:
    """Render a custom HTML player with speed controls and transcript highlighting.

    The highlight is approximate: it maps playback progress to word position.
    """
    audio_base64 = base64.b64encode(wav_bytes).decode("utf-8")
    words = story.split()
    words_html = " ".join(
        f"<span class='story-word'>{html.escape(word)}</span>" for word in words
    )
    speeds_json = json.dumps([0.5, 1.0, 1.5, 2.0])

    html_block = f"""
    <div class="storybook-player">
      <div id="story-text" class="story-text">{words_html}</div>
      <audio id="story-audio" controls preload="metadata">
        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
      </audio>
      <div class="speed-row">
        <span class="speed-label">Speed:</span>
        <div id="speed-buttons" class="speed-buttons"></div>
      </div>
      <div class="story-meta">Story length: {word_count} words</div>
    </div>

    <style>
      .storybook-player {{
        background: rgba(255, 255, 255, 0.92);
        border-radius: 24px;
        padding: 1.2rem 1.25rem 1rem 1.25rem;
        border: 1px solid rgba(255, 196, 108, 0.35);
        box-shadow: 0 18px 42px rgba(44, 35, 19, 0.09);
      }}
      .speed-row {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 0.85rem 0 0.45rem 0;
        flex-wrap: wrap;
      }}
      .speed-label {{
        font-weight: 600;
        color: #714000;
      }}
      .speed-buttons {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
      }}
      .speed-btn {{
        border: none;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        background: #ffe4a8;
        color: #6f4200;
        font-weight: 700;
        cursor: pointer;
      }}
      .speed-btn.active {{
        background: #ffaf3f;
        color: white;
      }}
      .story-text {{
        line-height: 2.05;
        font-size: 1.03rem;
        color: #3b2a15;
        margin-bottom: 0.9rem;
      }}
      .story-meta {{
        color: #8a7b61;
        font-size: 0.95rem;
        margin-top: 0.25rem;
        text-align: right;
      }}
      .story-word {{
        transition: all 0.18s ease;
        padding: 0.06rem 0.08rem;
        border-radius: 0.4rem;
      }}
      .story-word.active {{
        background: #ffe08a;
        color: #713b00;
        box-shadow: 0 0 0 1px rgba(255, 171, 36, 0.28);
      }}
    </style>

    <script>
      const audio = document.getElementById("story-audio");
      const wordNodes = Array.from(document.querySelectorAll(".story-word"));
      const speeds = {speeds_json};
      const buttonHost = document.getElementById("speed-buttons");

      function setSpeed(speed) {{
        audio.playbackRate = speed;
        document.querySelectorAll(".speed-btn").forEach((button) => {{
          button.classList.toggle("active", Number(button.dataset.speed) === speed);
        }});
      }}

      speeds.forEach((speed) => {{
        const button = document.createElement("button");
        button.type = "button";
        button.className = "speed-btn";
        button.dataset.speed = speed;
        button.textContent = `${{speed}}x`;
        button.onclick = () => setSpeed(speed);
        buttonHost.appendChild(button);
      }});

      setSpeed(1.0);

      function updateHighlight() {{
        if (!audio.duration || !wordNodes.length) return;
        const activeIndex = Math.min(
          wordNodes.length - 1,
          Math.floor((audio.currentTime / audio.duration) * wordNodes.length)
        );
        wordNodes.forEach((node, index) => {{
          node.classList.toggle("active", index === activeIndex);
        }});
      }}

      audio.addEventListener("timeupdate", updateHighlight);
      audio.addEventListener("play", updateHighlight);
      audio.addEventListener("seeked", updateHighlight);
      audio.addEventListener("ended", () => {{
        wordNodes.forEach((node) => node.classList.remove("active"));
      }});
    </script>
    """

    components.html(html_block, height=360, scrolling=False)
