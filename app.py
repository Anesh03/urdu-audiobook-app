import streamlit as st
import edge_tts
import asyncio
import os
from pydub import AudioSegment, effects
from tempfile import NamedTemporaryFile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Urdu AI Audiobook Generator",
    page_icon="🎙️",
    layout="wide"
)

# ---------------- UI HEADER ----------------
st.title("🎙️ Professional Urdu AI Audiobook Generator")
st.caption("Convert your Urdu text into high-quality natural speech with AI voices")

# ---------------- SIDEBAR CONTROLS ----------------
st.sidebar.header("⚙️ Voice Settings")

voice = st.sidebar.selectbox(
    "Choose Voice",
    [
        ("Urdu Male - Asad", "ur-PK-AsadNeural"),
        ("Urdu Female - Uzma", "ur-PK-UzmaNeural")
    ],
    format_func=lambda x: x[0]
)[1]

rate = st.sidebar.slider("Speed (Rate)", -50, 50, -10)
pitch = st.sidebar.slider("Pitch (Hz)", -20, 20, -3)
volume = st.sidebar.slider("Volume (%)", 0, 100, 100)

chunk_size = st.sidebar.number_input("Chunk Size", 1000, 6000, 4000)

# ---------------- INPUT SECTION ----------------
st.subheader("📥 Input Text")

uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])
text_input = st.text_area("Or paste your Urdu text here", height=250)

text = ""

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
else:
    text = text_input

# ---------------- CORE FUNCTION ----------------
async def generate_audio(text, voice, rate, pitch, volume, chunk_size, progress_bar, status):

    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    temp_files = []

    for i, chunk in enumerate(chunks):
        status.write(f"🎙️ Processing chunk {i+1}/{len(chunks)}")

        communicate = edge_tts.Communicate(
            text=chunk,
            voice=voice,
            rate=f"{rate}%",
            pitch=f"{pitch}Hz",
            volume=f"{volume}%"
        )

        temp_file = f"chunk_{i}.mp3"
        await communicate.save(temp_file)
        temp_files.append(temp_file)

        progress_bar.progress((i + 1) / len(chunks))

    status.write("🎚️ Combining and normalizing audio...")

    combined = AudioSegment.empty()

    for file in temp_files:
        audio = AudioSegment.from_mp3(file)
        audio = audio + 6  # boost
        combined += audio
        os.remove(file)

    final_audio = effects.normalize(combined)

    output_file = "urdu_audiobook.mp3"
    final_audio.export(output_file, format="mp3", bitrate="192k")

    return output_file

# ---------------- ACTION BUTTON ----------------
if st.button("🚀 Generate Audiobook"):

    if not text.strip():
        st.warning("Please enter or upload text first!")
    else:
        progress = st.progress(0)
        status = st.empty()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        output_file = loop.run_until_complete(
            generate_audio(text, voice, rate, pitch, volume, chunk_size, progress, status)
        )

        st.success("✅ Audiobook generated successfully!")

        # ---------------- AUDIO PLAYER ----------------
        st.audio(output_file)

        # ---------------- DOWNLOAD BUTTON ----------------
        with open(output_file, "rb") as f:
            st.download_button(
                label="⬇️ Download Audiobook",
                data=f,
                file_name="urdu_audiobook.mp3",
                mime="audio/mp3"
            )

        st.info("🎧 Your professional Urdu narration is ready!")
