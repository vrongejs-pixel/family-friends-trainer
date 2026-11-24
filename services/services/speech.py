import asyncio
import hashlib
import os
import edge_tts

AUDIO_CACHE_DIR = os.path.join("data", "audio_cache")

VOICES = {
    "US (Американский)": "en-US-JennyNeural",
    "UK (Британский)": "en-GB-SoniaNeural",
}


def _ensure_cache_dir():
    if not os.path.exists(AUDIO_CACHE_DIR):
        os.makedirs(AUDIO_CACHE_DIR)


async def _generate_tts_async(text: str, voice: str, rate: str, filepath: str):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(filepath)


def get_audio_bytes(text: str, accent: str = "US (Американский)", slow: bool = False) -> bytes | None:
    """Генерирует или берёт из кэша MP3-озвучку английского текста."""
    if not text or not text.strip():
        return None

    _ensure_cache_dir()
    voice = VOICES.get(accent, "en-US-JennyNeural")
    rate = "-30%" if slow else "+0%"

    key = f"{text.strip()}|{voice}|{rate}".encode("utf-8")
    file_hash = hashlib.md5(key).hexdigest()
    filepath = os.path.join(AUDIO_CACHE_DIR, f"{file_hash}.mp3")

    try:
        if not os.path.exists(filepath):
            asyncio.run(_generate_tts_async(text.strip(), voice, rate, filepath))
        with open(filepath, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка синтеза речи: {e}")
        return None
