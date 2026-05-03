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
    close_story_card,
    open_story_card,
    render_image_input,
    render_intro,
    render_result_header,
    render_sidebar_controls,
)


def main() -> None:
    # Page config must run before most Streamlit elements.
    # Deployment note: keep this file touched when we need Streamlit Cloud to refresh.
    st.set_page_config(page_title=APP_TITLE, layout="centered")

    # Apply the custom visual theme, then render the intro and sidebar controls.
    apply_app_styles()
    render_intro()
    controls = render_sidebar_controls()

    # Let the child or parent provide an image either by upload or camera.
    uploaded_file = render_image_input(controls["input_mode"])

    # Stop early until the user provides an image source.
    if uploaded_file is None:
        st.stop()

    # Show the selected image before running any model work.
    st.image(uploaded_file, use_container_width=True)

    # Run the full multimedia pipeline only when the user clicks the main button.
    if st.button("Create story and audio", type="primary"):
        temp_image_path = save_uploaded_file(uploaded_file)
        try:
            # Step 1: understand the image and create a short title.
            with st.spinner("Looking at the image..."):
                caption = generate_image_caption(temp_image_path)
                image_title = generate_image_title(caption, controls["lesson_theme"])

            # Step 2: turn the caption into a short story for ages 3 to 5.
            with st.spinner("Writing a child-friendly story..."):
                story = generate_story_from_caption(
                    caption=caption,
                    lesson_theme=controls["lesson_theme"],
                    mood=controls["mood"],
                    word_target=controls["word_target"],
                    child_name=controls["child_name"],
                    max_words=MAX_STORY_WORDS,
                )

            # Step 3: convert the story into read-aloud audio.
            with st.spinner("Creating audio..."):
                audio_array, sample_rate = generate_audio(story)
                wav_bytes = audio_array_to_wav_bytes(audio_array, sample_rate)

            # Step 4: show the title, caption, and custom audio player.
            render_result_header(image_title, caption)
            open_story_card()
            render_audio_story_player(
                story=story,
                wav_bytes=wav_bytes,
                word_count=len(story.split()),
            )
            close_story_card()
        except Exception as error:
            st.error(
                "Something went wrong while generating the story or audio. "
                "Please try another image or run the app again."
            )
            st.exception(error)
        finally:
            # Clean up the temporary local image after generation finishes.
            temp_image_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
