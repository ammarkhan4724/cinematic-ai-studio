import os, subprocess, json

def compose_final_cinematic_video(
    shot_video_paths,
    voiceover_path,
    soundscape_path,
    subtitle_ass_path,
    output_path,
    crossfade_sec=0.5,
    ducking_db=16.0
):
    """
    Assembles video shots, voiceover, soundscape, and burned-in subtitles into a finished 1080p MP4.
    Applies audio sidechain ducking to dip the music whenever speech occurs.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 1. Create concat list for video shots
    concat_txt = output_path.replace(".mp4", "_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for vp in shot_video_paths:
            # Escape path for ffmpeg concat
            fpath = vp.replace("\\", "/")
            f.write(f"file '{fpath}'\n")
            
    print(f"[Compositor] Concat list created with {len(shot_video_paths)} shots.")
    
    # Escape font path and ass path for ffmpeg filtergraph on Windows
    sub_clean = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
    fonts_dir = "D\\:/Cinematic_AI_Studio/assets/fonts"
    
    # Subtitle filter with font directory
    sub_filter = f"subtitles='{sub_clean}':fontsdir='{fonts_dir}'"
    
    # 2. Audio mixing with Sidechain Ducking:
    # [1:a] is voiceover, [2:a] is soundscape bed
    # We use sidechaincompress: soundscape is ducked whenever voiceover exceeds -32dB
    # voiceover is boosted and centered
    audio_filter = (
        f"[2:a]volume=0.85[music];"
        f"[music][1:a]sidechaincompress=threshold=0.08:ratio=6:attack=20:release=350[ducked_music];"
        f"[ducked_music][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", voiceover_path,
        "-i", soundscape_path,
        "-filter_complex", f"[0:v]{sub_filter}[vout];{audio_filter}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "44100",
        "-shortest",
        output_path
    ]
    
    print(f"[Compositor] Muxing and rendering final cinematic video -> {output_path}...")
    subprocess.run(cmd, check=True)
    
    if os.path.exists(concat_txt):
        os.remove(concat_txt)
        
    print(f"\n=======================================================")
    print(f"  CINEMATIC VIDEO GENERATED: {output_path}")
    print(f"=======================================================\n")
    return output_path
