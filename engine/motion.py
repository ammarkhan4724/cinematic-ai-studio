import os, subprocess

COLOR_GRADES = {
    "deep_abyss": "eq=contrast=1.18:saturation=1.12:brightness=-0.04,vignette=PI/4.2",
    "dark_mystery": "eq=contrast=1.22:saturation=0.92:brightness=-0.05,vignette=PI/3.8",
    "epic_history": "eq=contrast=1.14:saturation=1.05:brightness=-0.02,colorbalance=rs=0.08:gs=0.02:bs=-0.06:rm=0.05:gm=0.01:bm=-0.04,vignette=PI/4.5",
    "blockbuster": "eq=contrast=1.16:saturation=1.15:brightness=-0.02,colorbalance=rs=0.04:gs=-0.02:bs=0.06:rm=-0.02:gm=0.02:bm=-0.04,vignette=PI/4.5",
    "clean_cinema": "eq=contrast=1.08:saturation=1.05:brightness=0.0,vignette=PI/5.0"
}

def build_motion_clip(
    image_path,
    output_mp4,
    duration_sec,
    motion_type="zoom_in",
    style="dark_mystery",
    aspect_ratio="16:9",
    letterbox=True,
    fps=30
):
    """
    Renders a photorealistic still image into a dynamic, 2.5D camera move
    with cinematic color grading, 35mm organic film grain, and anamorphic letterbox.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)
    n_frames = int(duration_sec * fps)
    
    if aspect_ratio == "9:16":
        out_w, out_h = 1080, 1920
        # Vertical Short: scale/crop to 9:16 then slow subtle zoom
        if motion_type == "zoom_in":
            zoom_expr = f"min(zoom+0.0008,1.15)"
        else:
            zoom_expr = f"max(1.15-0.0008*on,1.0)"
        zoom_filter = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s=1080x1920:fps={fps}"
        bars_filter = ""
    else:
        out_w, out_h = 1920, 1080
        # 16:9 Landscape
        nf = max(1, n_frames)
        if motion_type == "zoom_in":
            zoom_expr = "min(zoom+0.0009,1.18)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion_type == "zoom_out":
            zoom_expr = "max(1.18-0.0009*on,1.0)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion_type == "pan_left":
            zoom_expr = "1.14"
            x_expr = f"(iw-iw/zoom)*(1-on/{nf})"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion_type == "pan_right":
            zoom_expr = "1.14"
            x_expr = f"(iw-iw/zoom)*(on/{nf})"
            y_expr = "ih/2-(ih/zoom/2)"
        elif motion_type == "crane_down":
            zoom_expr = "min(zoom+0.0006,1.12)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = f"(ih-ih/zoom)*(on/{nf})"
        else:
            zoom_expr = "min(zoom+0.0008,1.15)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
            
        zoom_filter = f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={n_frames}:s=1920x1080:fps={fps}"
        bars_filter = ",drawbox=x=0:y=0:w=iw:h=ih*0.10:color=black:t=fill,drawbox=x=0:y=ih-ih*0.10:w=iw:h=ih*0.10:color=black:t=fill" if letterbox else ""
        
    grade = COLOR_GRADES.get(style, COLOR_GRADES["clean_cinema"])
    
    # Combined filter chain:
    # Zoompan -> Color Grade -> 35mm Film Grain -> Scope Bars -> Color space
    filter_chain = f"{zoom_filter},{grade}{bars_filter},noise=c0s=6:allf=t+u,format=yuv420p"
    
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1",
        "-i", image_path,
        "-vf", filter_chain,
        "-t", str(duration_sec),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        output_mp4
    ]
    
    print(f"[Motion] Rendering {motion_type} ({duration_sec:.2f}s, {style}) -> {os.path.basename(output_mp4)}...")
    subprocess.run(cmd, check=True)
    return output_mp4
