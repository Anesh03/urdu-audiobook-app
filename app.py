import streamlit as st
import edge_tts
import asyncio
import os

st.set_page_config(page_title="Urdu Audiobook AI", layout="wide")

st.title("🎙️ Urdu AI Audiobook Generator")

voice = st.selectbox(
    "Voice",
    ["ur-PK-AsadNeural", "ur-PK-UzmaNeural"]
)

text = st.text_area("Enter Urdu text", height=300)

async def generate(text, voice):
    output_file = "output.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="-10%",
        pitch="-3Hz"
    )

    await communicate.save(output_file)
    return output_file


if st.button("Generate Audio"):
    if not text.strip():
        st.warning("Please enter text")
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        file = loop.run_until_complete(generate(text, voice))

        st.success("Done!")

        st.audio(file)

        with open(file, "rb") as f:
            st.download_button(
                "Download MP3",
                f,
                file_name="urdu_audiobook.mp3"
            )
