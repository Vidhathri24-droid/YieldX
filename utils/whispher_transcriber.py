from openai import OpenAI

client = OpenAI()  # Make sure API key is set in env

def transcribe_audio(file_path):
    """Call OpenAI Whisper API"""
    with open(file_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
        return resp.text if hasattr(resp, "text") else ""
