import os, sys, asyncio, subprocess, wave
import numpy as np

DEFAULT_VOICE = "en-US-ChristopherNeural"  # Deep, authoritative cinematic baritone
UK_VOICE = "en-GB-RyanNeural"              # Sophisticated British documentary narrator
FEMALE_VOICE = "en-US-AvaNeural"           # Evocative, mysterious female narrator

VOICE_PROFILES = {
    "christopher": {"voice": "en-US-ChristopherNeural", "rate": "-8%", "pitch": "-4Hz"},
    "ryan": {"voice": "en-GB-RyanNeural", "rate": "-6%", "pitch": "-2Hz"},
    "brian": {"voice": "en-US-BrianMultilingualNeural", "rate": "-7%", "pitch": "-3Hz"},
    "ava": {"voice": "en-US-AvaNeural", "rate": "-8%", "pitch": "-1Hz"}
}

async def _synthesize_edge_tts(text, output_wav, profile_name="christopher"):
    import edge_tts
    profile = VOICE_PROFILES.get(profile_name, VOICE_PROFILES["christopher"])
    temp_mp3 = output_wav.replace(".wav", ".tmp.mp3")
    
    communicate = edge_tts.Communicate(
        text=text,
        voice=profile["voice"],
        rate=profile["rate"],
        pitch=profile["pitch"]
    )
    await communicate.save(temp_mp3)
    
    # Convert MP3 to 44.1kHz mono WAV with broadcast vocal EQ
    # EQ: High-pass at 80Hz (cuts sub rumble), slight boost at 2.8kHz (intelligibility), vocal compression
    af_filter = "highpass=f=80,equalizer=f=2800:width_type=o:width=1.2:g=2.2,acompressor=threshold=-18dB:ratio=3:attack=10:release=120,loudnorm=I=-16:TP=-1.5:LRA=11"
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", temp_mp3,
        "-af", af_filter,
        "-ar", "44100", "-ac", "1",
        output_wav
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

def synthesize_narration(text, output_wav, profile_name="christopher"):
    """
    Synthesizes dramatic, cinematic narration.
    Uses edge-tts neural voices, post-processed with broadcast EQ & compression.
    Returns: float duration in seconds.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
    asyncio.run(_synthesize_edge_tts(text, output_wav, profile_name))
    
    # Measure duration
    with wave.open(output_wav, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
        
    print(f"[Voiceover] Synthesized ({profile_name}): {duration:.2f}s -> {os.path.basename(output_wav)}")
    return duration
