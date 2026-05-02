import streamlit as st
from app_core.audio_utils import audio_array_to_wav_bytes, render_audio_story_player
from app_core.config import APP_TITLE, MAX_STORY_WORDS
from app_core.pipelines import (
    generate_audio,
    generate_image_caption,
    generate_story_from_caption,
    save_uploaded_file,
)
from app_core.story_utils import generate_image_title
from app_core.ui import (
    apply_app_styles,
    render_image_input,
    render_intro,
    render_result_header,
    render_sidebar_controls,
)


def main() -> None:
    # Page config must run before most Streamlit elements.
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    apply_app_styles()
    render_intro()
    controls = render_sidebar_controls()
    uploaded_file = render_image_input(controls["input_mode"])

    # Stop early until the user provides an image source.
    if uploaded_file is None:
        st.stop()

    st.image(uploaded_file, use_container_width=True)

    # Run the full multimedia pipeline only when the user clicks the main button.
    if st.button("Create story and audio", type="primary"):
        temp_image_path = save_uploaded_file(uploaded_file)
        try:
            with st.spinner("Looking at the image..."):
                caption = generate_image_caption(temp_image_path)
                image_title = generate_image_title(caption, controls["lesson_theme"])

            with st.spinner("Writing a child-friendly story..."):
                story = generate_story_from_caption(
                    caption=caption,
                    lesson_theme=controls["lesson_theme"],
                    mood=controls["mood"],
                    word_target=controls["word_target"],
                    child_name=controls["child_name"],
                    max_words=MAX_STORY_WORDS,
                )

            with st.spinner("Creating audio..."):
                audio_array, sample_rate = generate_audio(story)
                wav_bytes = audio_array_to_wav_bytes(audio_array, sample_rate)

            render_result_header(image_title, caption)
            st.caption(f"Story length: {len(story.split())} words")
            st.subheader("Story")
            render_audio_story_player(
                title=image_title,
                story=story,
                wav_bytes=wav_bytes,
            )
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
