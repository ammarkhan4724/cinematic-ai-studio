import os, sys, argparse, json, re, time, wave, subprocess
import numpy as np

# Ensure engine is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from engine import (
    CinematicStoryboard,
    resolve_scene_visual,
    synthesize_narration,
    generate_sub_drone,
    generate_cinematic_hit,
    generate_riser,
    save_wav,
    build_motion_clip,
    generate_cinematic_ass_subtitles,
    compose_final_cinematic_video
)

def run_pipeline(
    topic: str,
    slug: str = None,
    voice: str = "christopher",
    style: str = "auto",
    aspect_ratio: str = "16:9",
    letterbox: bool = True,
    fps: int = 30,
    upload_drive: bool = False,
    push_git: bool = False
):
    start_time = time.time()
    if not slug:
        slug = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower()).strip('_')[:30]
        
    project_dir = os.path.join(SCRIPT_DIR, "outputs", "projects", slug)
    images_dir = os.path.join(project_dir, "images")
    audio_dir = os.path.join(project_dir, "audio")
    video_dir = os.path.join(project_dir, "video")
    final_dir = os.path.join(SCRIPT_DIR, "outputs", "final")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)
    
    print("\n" + "=" * 65)
    print(f"🎬 CINEMATIC AI VIDEO PIPELINE")
    print(f"   Topic: {topic}")
    print(f"   Voice: {voice.upper()} | Style: {style} | Aspect: {aspect_ratio}")
    print(f"   Project Directory: {project_dir}")
    print("=" * 65 + "\n")
    
    # -------------------------------------------------------------
    # 1. STORYBOARD & SCRIPT GENERATION
    # -------------------------------------------------------------
    print("[Step 1/6] 📜 Generating Cinematic Storyboard...")
    storyboard = CinematicStoryboard(topic=topic, style=style).generate()
    storyboard_path = os.path.join(project_dir, "storyboard.json")
    with open(storyboard_path, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2)
    print(f"✓ Storyboard written: {len(storyboard['scenes'])} scenes ({storyboard['title']})\n")
    
    # -------------------------------------------------------------
    # 2. VOICEOVER SYNTHESIS & TIMELINE MAPPING
    # -------------------------------------------------------------
    print("[Step 2/6] 🎙️ Synthesizing Voiceover & Building Timecode Map...")
    scene_timings = []
    current_time = 0.5  # 0.5s initial breath room
    shot_durations = []
    vo_audio_parts = []
    subtitle_events = []
    
    # Generate 0.5s initial silence
    init_silence = np.zeros(int(44100 * 0.5), dtype=np.float32)
    master_vo_samples = [init_silence]
    
    for sc in storyboard["scenes"]:
        idx = sc["index"]
        vo_path = os.path.join(audio_dir, f"vo_scene_{idx:02d}.wav")
        duration = synthesize_narration(sc["narration"], vo_path, profile_name=voice)
        
        # Load WAV samples
        with wave.open(vo_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            master_vo_samples.append(samples)
            
        start_t = current_time
        end_t = current_time + duration
        subtitle_events.append({
            "start": start_t,
            "end": end_t,
            "text": sc["narration"]
        })
        
        # Inter-scene pause (0.7s silence)
        pause_samples = np.zeros(int(44100 * 0.7), dtype=np.float32)
        master_vo_samples.append(pause_samples)
        
        shot_dur = duration + 0.7 + (0.5 if idx == 1 else 0.0)
        shot_durations.append(shot_dur)
        current_time += duration + 0.7
        
    # Combine full voiceover WAV
    total_vo_array = np.concatenate(master_vo_samples)
    total_vo_path = os.path.join(audio_dir, "vo_master.wav")
    # Save as 16-bit mono 44.1kHz
    with wave.open(total_vo_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        int16_vo = (np.clip(total_vo_array, -1.0, 1.0) * 32767.0).astype(np.int16)
        wf.writeframes(int16_vo.tobytes())
        
    total_duration = len(total_vo_array) / 44100.0
    print(f"✓ Master Voiceover assembled: {total_duration:.2f}s total duration.\n")
    
    # -------------------------------------------------------------
    # 3. SOUND DESIGN & ATMOSPHERIC SOUNDSCAPE SYNTHESIS
    # -------------------------------------------------------------
    print("[Step 3/6] 🎼 Synthesizing Procedural Stereo Soundscape & Sub-Bass...")
    soundscape_len = total_duration + 2.0  # Room for reverb tail
    sub_drone = generate_sub_drone(soundscape_len, base_freq=50.0)
    
    # Insert SFX cues
    cue_time = 0.2
    for i, sc in enumerate(storyboard["scenes"]):
        cue = sc.get("sfx_cue", "drone")
        sample_idx = int(cue_time * 44100)
        if cue == "cinematic_hit":
            hit = generate_cinematic_hit(duration_sec=3.8, peak_freq=85.0)
            hit_len = min(hit.shape[1], sub_drone.shape[1] - sample_idx)
            if hit_len > 0:
                sub_drone[:, sample_idx:sample_idx + hit_len] += hit[:, :hit_len] * 0.85
        elif cue == "riser":
            riser = generate_riser(duration_sec=3.5)
            riser_len = min(riser.shape[1], sub_drone.shape[1] - sample_idx)
            if riser_len > 0:
                sub_drone[:, sample_idx:sample_idx + riser_len] += riser[:, :riser_len] * 0.70
        cue_time += shot_durations[i]
        
    soundscape_path = os.path.join(audio_dir, "soundscape_master.wav")
    save_wav(sub_drone, soundscape_path)
    print(f"✓ Procedural Soundscape mixed & mastered: {soundscape_path}\n")
    
    # -------------------------------------------------------------
    # 4. VISUAL RESOLUTION & 2.5D CAMERA MOTION RENDERING
    # -------------------------------------------------------------
    print("[Step 4/6] 🎥 Resolving Visuals & Rendering Dynamic 2.5D Camera Moves...")
    shot_video_paths = []
    for i, sc in enumerate(storyboard["scenes"]):
        idx = sc["index"]
        shot_dur = shot_durations[i]
        # 1. Resolve image (AI generated or procedural plate)
        img_path = resolve_scene_visual(sc, images_dir, fallback_style=storyboard["style"])
        
        # 2. Render 2.5D Motion clip with FFmpeg zoompan + color grading + grain + letterbox
        clip_path = os.path.join(video_dir, f"shot_{idx:02d}.mp4")
        build_motion_clip(
            image_path=img_path,
            output_mp4=clip_path,
            duration_sec=shot_dur,
            motion_type=sc.get("motion_type", "zoom_in"),
            style=sc.get("style", storyboard["style"]),
            aspect_ratio=aspect_ratio,
            letterbox=letterbox,
            fps=fps
        )
        shot_video_paths.append(clip_path)
    print(f"✓ All {len(shot_video_paths)} cinematic motion shots rendered.\n")
    
    # -------------------------------------------------------------
    # 5. SUBTITLE TYPOGRAPHY & FINAL BROADCAST COMPOSITING
    # -------------------------------------------------------------
    print("[Step 5/6] 💎 Generating ASS Typography & Compositing with Audio Ducking...")
    ass_path = os.path.join(project_dir, "subtitles.ass")
    generate_cinematic_ass_subtitles(subtitle_events, ass_path, aspect_ratio=aspect_ratio)
    
    # Clean output title filename
    clean_title = re.sub(r'[^a-zA-Z0-9_\-\s]', '', storyboard["title"]).replace(" ", "_")
    final_output_mp4 = os.path.join(final_dir, f"{clean_title}_{aspect_ratio.replace(':', 'x')}.mp4")
    
    compose_final_cinematic_video(
        shot_video_paths=shot_video_paths,
        voiceover_path=total_vo_path,
        soundscape_path=soundscape_path,
        subtitle_ass_path=ass_path,
        output_path=final_output_mp4
    )
    
    elapsed = time.time() - start_time
    print(f"✨ RENDERING COMPLETE in {elapsed:.1f}s!")
    print(f"   Final Master File: {final_output_mp4}")
    
    # -------------------------------------------------------------
    # 6. AUTOMATED SYNC (GOOGLE DRIVE & GITHUB)
    # -------------------------------------------------------------
    if upload_drive:
        print("\n[Step 6/6] ☁️ Uploading to Google Drive...")
        _upload_to_google_drive(final_output_mp4)
        
    if push_git:
        print("\n[Step 6/6] 🐙 Committing & Pushing to GitHub...")
        _sync_to_github(f"Rendered cinematic episode: {storyboard['title']}")
        
    return final_output_mp4

def _upload_to_google_drive(file_path: str):
    """Uploads file to Google Drive via authenticated gdrive CLI / script."""
    cmd = [
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", "D:/Cinematic_AI_Studio/upload_to_drive.ps1",
        "-FilePath", file_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Uploaded to Google Drive successfully!\n{res.stdout}")
    except Exception as e:
        print(f"⚠️ Google Drive upload note: {e}")

def _sync_to_github(commit_msg: str):
    """Commits and pushes code updates to GitHub."""
    try:
        subprocess.run(["git", "add", "."], cwd=SCRIPT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=SCRIPT_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=SCRIPT_DIR, check=True)
        print("✓ Code synchronized to GitHub.")
    except Exception as e:
        print(f"⚠️ Git sync note: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cinematic AI Video Pipeline")
    parser.add_argument("--topic", type=str, default="The Lost City of Atlantis", help="Documentary Topic or Title")
    parser.add_argument("--slug", type=str, default=None, help="Project slug")
    parser.add_argument("--voice", type=str, default="christopher", choices=["christopher", "ryan", "brian", "ava"], help="Narrator vocal profile")
    parser.add_argument("--style", type=str, default="auto", choices=["auto", "deep_abyss", "dark_mystery", "epic_history", "blockbuster", "clean_cinema"], help="Color grading and visual style")
    parser.add_argument("--aspect", type=str, default="16:9", choices=["16:9", "9:16"], help="Aspect ratio (16:9 widescreen or 9:16 vertical shorts)")
    parser.add_argument("--no-letterbox", action="store_true", help="Disable 2.39:1 anamorphic letterbox")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--drive", action="store_true", help="Upload result to Google Drive")
    parser.add_argument("--git", action="store_true", help="Sync project to GitHub")
    
    args = parser.parse_args()
    run_pipeline(
        topic=args.topic,
        slug=args.slug,
        voice=args.voice,
        style=args.style,
        aspect_ratio=args.aspect,
        letterbox=not args.no_letterbox,
        fps=args.fps,
        upload_drive=args.drive,
        push_git=args.git
    )
