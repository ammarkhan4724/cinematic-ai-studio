import os, math, wave, struct
import numpy as np

SR = 44100  # 44.1 kHz broadcast audio

def generate_sub_drone(duration_sec, base_freq=55.0):
    """Generate a rich, warm cinematic sub-drone with stereo detuning and LFO."""
    t = np.linspace(0, duration_sec, int(SR * duration_sec), endpoint=False)
    
    # Left channel: base frequency + slow LFO
    lfo_left = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)
    left = (
        0.55 * np.sin(2 * np.pi * base_freq * t) +
        0.30 * np.sin(2 * np.pi * (base_freq * 1.5) * t) * lfo_left +
        0.20 * np.sin(2 * np.pi * (base_freq * 2.0) * t) +
        0.10 * np.sin(2 * np.pi * (base_freq * 3.0) * t)
    )
    
    # Right channel: slightly detuned (+0.4 Hz) for massive stereo width
    lfo_right = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t + np.pi / 3)
    right = (
        0.55 * np.sin(2 * np.pi * (base_freq + 0.4) * t) +
        0.30 * np.sin(2 * np.pi * (base_freq * 1.5 - 0.3) * t) * lfo_right +
        0.20 * np.sin(2 * np.pi * (base_freq * 2.0 + 0.5) * t) +
        0.10 * np.sin(2 * np.pi * (base_freq * 3.0 - 0.2) * t)
    )
    
    # Add subtle organic tape warmth / low-passed noise
    noise = np.random.normal(0, 0.02, len(t))
    left += noise
    right += noise
    
    # Apply slow master fade in and fade out
    fade_len = int(SR * 2.0)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    left[:fade_len] *= fade_in
    right[:fade_len] *= fade_in
    left[-fade_len:] *= fade_out
    right[-fade_len:] *= fade_out
    
    return np.vstack((left, right))

def generate_cinematic_hit(duration_sec=3.5, peak_freq=85.0):
    """Generate a heavy cinematic sub-bass impact (Braam / hit) for transitions."""
    n_samples = int(SR * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    
    # Exponential pitch drop from peak_freq down to 32Hz
    freq_sweep = 32.0 + (peak_freq - 32.0) * np.exp(-4.5 * t)
    phase = 2 * np.pi * np.cumsum(freq_sweep) / SR
    
    # Impact envelope: explosive attack, long decaying sub tail
    envelope = np.exp(-1.8 * t)
    
    # Rich harmonics with soft clipping distortion for punch
    raw = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    distorted = np.tanh(raw * 1.6) * envelope
    
    # Stereo widening: slight phase delay on right channel
    left = distorted
    delay_samples = int(SR * 0.015)  # 15ms Haas effect
    right = np.zeros_like(left)
    right[delay_samples:] = left[:-delay_samples]
    
    return np.vstack((left, right))

def generate_riser(duration_sec=4.0):
    """Generate a rising tension riser with swirling noise for climactic transitions."""
    n_samples = int(SR * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    
    # Exponential frequency rise from 100Hz to 2400Hz
    freq = 100.0 * np.exp(math.log(24.0) * (t / duration_sec))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    
    # Rising envelope
    env = (t / duration_sec) ** 2.2
    
    # White noise filtered and modulated
    noise = np.random.normal(0, 0.2, n_samples) * env
    tone = np.sin(phase) * env * 0.6
    
    stereo = tone + noise
    # Pan slowly from left to right
    pan_l = np.cos((t / duration_sec) * (np.pi / 2))
    pan_r = np.sin((t / duration_sec) * (np.pi / 2))
    
    return np.vstack((stereo * pan_l, stereo * pan_r))

def save_wav(stereo_data, output_path):
    """Save 2D numpy array [2, N] as 16-bit 44.1kHz stereo WAV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    # Normalize with headroom (-1dB)
    peak = np.max(np.abs(stereo_data))
    if peak > 0:
        norm = (stereo_data / peak) * 0.89
    else:
        norm = stereo_data
        
    int16_data = (norm * 32767).astype(np.int16)
    interleaved = np.empty((int16_data.shape[1] * 2,), dtype=np.int16)
    interleaved[0::2] = int16_data[0]
    interleaved[1::2] = int16_data[1]
    
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(interleaved.tobytes())

def build_soundscape(duration_sec, scene_cuts, output_path, style="dark_mystery"):
    """
    Construct a complete, multi-layered cinematic audio bed:
    - Base atmospheric drone (customized by style)
    - Cinematic impacts / Braams at major scene cuts
    - Risers leading up to reveals
    """
    print(f"[Soundscape] Synthesizing {style} soundscape ({duration_sec:.1f}s)...")
    
    freq_map = {
        "dark_mystery": 48.0,
        "deep_abyss": 42.0,
        "cosmic_exploration": 55.0,
        "epic_history": 65.0,
        "cyberpunk_future": 58.0
    }
    base_freq = freq_map.get(style, 50.0)
    
    # 1. Base atmospheric drone
    drone = generate_sub_drone(duration_sec, base_freq=base_freq)
    
    # 2. Add cinematic impacts at major transition timestamps
    hit = generate_cinematic_hit(duration_sec=3.5, peak_freq=base_freq * 1.6)
    hit_len = hit.shape[1]
    
    for cut_time in scene_cuts:
        start_idx = int(cut_time * SR)
        end_idx = min(drone.shape[1], start_idx + hit_len)
        chunk_len = end_idx - start_idx
        if chunk_len > 0:
            drone[:, start_idx:end_idx] += hit[:, :chunk_len] * 0.65
            
    # 3. Add climax riser before the final third
    if len(scene_cuts) >= 2 and duration_sec > 15:
        climax_cut = scene_cuts[-2]
        riser_len_sec = 4.0
        riser = generate_riser(duration_sec=riser_len_sec)
        riser_samples = riser.shape[1]
        start_r = max(0, int((climax_cut - riser_len_sec) * SR))
        end_r = min(drone.shape[1], start_r + riser_samples)
        drone[:, start_r:end_r] += riser[:, :(end_r - start_r)] * 0.45
        
    save_wav(drone, output_path)
    print(f"[Soundscape] Ready -> {output_path}")
    return output_path
