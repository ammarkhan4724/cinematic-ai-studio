import os

FONT_PATH = "D:/Cinematic_AI_Studio/assets/fonts/Cinzel.ttf"

def format_timestamp_ass(seconds):
    """Convert float seconds to ASS format: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_cinematic_ass_subtitles(subtitle_events, output_ass, aspect_ratio="16:9"):
    """
    Generates a broadcast-quality ASS subtitle file with Cinzel typography,
    subtle letter-spacing, elegant drop shadows, and cinematic positioning.
    
    subtitle_events = [
        {"start": 0.5, "end": 4.2, "text": "Beneath the crushing pressure of the ocean..."},
        ...
    ]
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_ass)), exist_ok=True)
    
    if aspect_ratio == "9:16":
        play_res_x, play_res_y = 1080, 1920
        font_size = 54
        margin_v = 380
    else:
        play_res_x, play_res_y = 1920, 1080
        font_size = 46
        margin_v = 150  # Placed above the 2.39:1 scope bar
        
    header = f"""[Script Info]
Title: Cinematic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cinematic,Cinzel,{font_size},&H00F5F8FA,&H000000FF,&H00120B05,&H80000000,-1,0,0,0,100,100,2,0,1,3.2,1.5,2,90,90,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for ev in subtitle_events:
        t_start = format_timestamp_ass(ev["start"])
        t_end = format_timestamp_ass(ev["end"])
        txt = ev["text"].strip().replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{t_start},{t_end},Cinematic,,0,0,0,,{txt}\n")
        
    with open(output_ass, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    print(f"[Typography] Generated ASS subtitles: {output_ass}")
    return output_ass
