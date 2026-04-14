import gradio as gr
import edge_tts
import asyncio
import os
from pydub import AudioSegment, effects

# ---------- CORE AUDIO ENGINE ----------
async def generate_audio(text, voice):

    speed = "-10%"
    pitch = "-3Hz"
    volume = "+100%"

    chunk_size = 4000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    files = []

    for i, chunk in enumerate(chunks):
        file_name = f"chunk_{i}.mp3"

        tts = edge_tts.Communicate(
            text=chunk,
            voice=voice,
            rate=speed,
            pitch=pitch
        )

        await tts.save(file_name)
        files.append(file_name)

    # Merge audio
    combined = AudioSegment.empty()

    for f in files:
        audio = AudioSegment.from_mp3(f)
        audio = audio + 6
        combined += audio
        os.remove(f)

    final = effects.normalize(combined)

    output_file = "urdu_audiobook.mp3"
    final.export(output_file, format="mp3", bitrate="192k")

    return output_file


# ---------- WRAPPER (fix async for Gradio) ----------
def tts_app(text, voice):

    if not text.strip():
        return None, "❌ Please enter text"

    file_path = asyncio.run(generate_audio(text, voice))

    return file_path, "✅ Done! Download ready"


# ---------- MODERN UI ----------
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="Urdu AI Voice Studio"
) as app:

    gr.Markdown("""
    # 🎙️ Urdu AI Voice Studio
    ### High-quality professional audiobook generator
    """)

    with gr.Row():
        text = gr.Textbox(
            label="📖 Paste Your Text",
            placeholder="Enter Urdu or English text here...",
            lines=12
        )

    voice = gr.Dropdown(
        choices=[
            ("Urdu Male (Asad)", "ur-PK-AsadNeural"),
            ("Urdu Female (Uzma)", "ur-PK-UzmaNeural")
        ],
        value="ur-PK-AsadNeural",
        label="🎤 Select Voice"
    )

    btn = gr.Button("🚀 Generate Audio", variant="primary")

    audio_output = gr.Audio(label="🎧 Output Audio")
    status = gr.Textbox(label="Status")

    btn.click(
        fn=tts_app,
        inputs=[text, voice],
        outputs=[audio_output, status]
    )

# ---------- RUN SERVER ----------
app.launch(
    share=True  # 🌍 gives LIVE public link instantly
)
