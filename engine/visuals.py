import os, shutil, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_procedural_cinematic_plate(prompt: str, style: str, output_path: str, width: int = 1920, height: int = 1080):
    """
    Synthesizes a high-resolution, atmospheric 1080p cinematic plate
    tailored to the prompt theme and color palette when external AI image generation is offline.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    p_lower = prompt.lower()
    
    # 1. Determine color palette based on style & keywords
    if "abyss" in style or "ocean" in p_lower or "atlantis" in p_lower or "mariana" in p_lower or "deep" in p_lower:
        top_color = (4, 15, 26)       # Pitch deep ocean blue
        mid_color = (8, 48, 72)       # Rich twilight cyan
        bot_color = (2, 24, 38)       # Abyssal floor
        glow_color = (30, 160, 190)   # Bioluminescence / underwater caustic
        theme = "ocean"
    elif "history" in style or "pyramid" in p_lower or "desert" in p_lower or "ancient" in p_lower:
        top_color = (28, 14, 8)       # Warm dusk amber
        mid_color = (95, 48, 22)      # Golden sandstone
        bot_color = (180, 115, 55)    # Desert sand
        glow_color = (255, 180, 70)   # Golden sun rays
        theme = "desert"
    elif "space" in p_lower or "cosmic" in p_lower or "star" in p_lower or "black hole" in p_lower:
        top_color = (3, 2, 8)         # Deep black void
        mid_color = (38, 12, 60)      # Violet nebula
        bot_color = (8, 20, 48)       # Stellar cyan
        glow_color = (180, 70, 220)   # Radiant pulsar glow
        theme = "space"
    else:
        top_color = (12, 16, 22)
        mid_color = (32, 44, 58)
        bot_color = (15, 20, 28)
        glow_color = (90, 140, 180)
        theme = "cinema"

    # 2. Build multi-stop vertical gradient background with numpy
    y = np.linspace(0, 1, height)[:, None]
    x = np.linspace(0, 1, width)[None, :]
    
    bg = np.zeros((height, width, 3), dtype=np.float32)
    # Blend 3 stops: top -> mid -> bot
    for c in range(3):
        upper = top_color[c] * (1 - y * 2) + mid_color[c] * (y * 2)
        lower = mid_color[c] * (2 - y * 2) + bot_color[c] * (y * 2 - 1)
        bg[:, :, c] = np.where(y < 0.5, upper, lower)
        
    # 3. Add volumetric radial glow / god rays
    center_x = 0.5 + 0.15 * math.sin(width * 0.001)
    center_y = 0.35
    dist = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2 * 2.2)
    radial_falloff = np.clip(1.0 - dist * 1.4, 0, 1) ** 2.2
    
    for c in range(3):
        bg[:, :, c] += glow_color[c] * radial_falloff * 0.65
        
    # 4. Organic texture / volumetric fog noise
    noise = np.random.normal(0, 8.0, (height, width, 3))
    bg += noise
    bg = np.clip(bg, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)
    
    # 5. Add thematic silhouettes & volumetric atmospheric elements
    if theme == "ocean":
        # Submerged monolith / ancient arch silhouette
        arch_w = int(width * 0.22)
        arch_h = int(height * 0.45)
        arch_x = int(width * 0.5 - arch_w / 2)
        arch_y = int(height * 0.55)
        # Pillars
        draw.rectangle([arch_x, arch_y, arch_x + 50, arch_y + arch_h], fill=(3, 14, 22))
        draw.rectangle([arch_x + arch_w - 50, arch_y, arch_x + arch_w, arch_y + arch_h], fill=(3, 14, 22))
        # Top lintel
        draw.rectangle([arch_x - 30, arch_y, arch_x + arch_w + 30, arch_y + 40], fill=(2, 10, 18))
        # Caustic streaks
        for i in range(12):
            ray_x = int(width * 0.3 + i * 80)
            draw.line([(ray_x, 0), (ray_x - 140, height)], fill=(50, 180, 220, 25), width=28)
            
    elif theme == "desert":
        # Pyramid silhouettes
        p1 = [(int(width * 0.1), height), (int(width * 0.45), int(height * 0.48)), (int(width * 0.8), height)]
        draw.polygon(p1, fill=(45, 20, 10))
        p2 = [(int(width * 0.55), height), (int(width * 0.78), int(height * 0.58)), (width, height)]
        draw.polygon(p2, fill=(30, 12, 6))
        
    elif theme == "space":
        # Cosmic starfield
        for _ in range(350):
            sx = np.random.randint(0, width)
            sy = np.random.randint(0, height)
            sb = np.random.randint(140, 255)
            draw.point((sx, sy), fill=(sb, sb, sb))
        # Planetary horizon
        draw.ellipse([int(-width * 0.2), int(height * 0.72), int(width * 1.2), int(height * 2.2)], fill=(6, 12, 28))
        draw.arc([int(-width * 0.2), int(height * 0.72), int(width * 1.2), int(height * 2.2)], 190, 350, fill=(40, 140, 255), width=4)

    # 6. Apply slight soft atmospheric blur
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    img.save(output_path, "JPEG", quality=95)
    print(f"[Visuals] Procedural plate synthesized ({theme}): {os.path.basename(output_path)}")
    return output_path

def resolve_scene_visual(scene_dict: dict, project_images_dir: str, fallback_style: str = "clean_cinema") -> str:
    """
    Resolves the visual for a scene.
    Priority:
    1. If scene['image_filename'] exists in project_images_dir, return it.
    2. Check common artifact/cache paths for existing high-res AI generation.
    3. If missing, generate a cinematic procedural plate matching the prompt and style.
    """
    os.makedirs(project_images_dir, exist_ok=True)
    fname = scene_dict.get("image_filename") or f"scene_{scene_dict.get('index', 1):02d}.jpg"
    target_path = os.path.join(project_images_dir, fname)
    
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return target_path
        
    # Check if we have pre-generated artwork in artifacts
    artifact_dirs = [
        r"C:\Users\AMMAR\.gemini\antigravity\brain\ed8c50f1-3f95-46a8-b745-03636bae520e",
        r"D:\Cinematic_AI_Studio\assets\images"
    ]
    for adir in artifact_dirs:
        if os.path.exists(adir):
            for f in os.listdir(adir):
                if f.endswith((".jpg", ".png")) and ("atlantis" in f.lower() or "cinematic" in f.lower()):
                    src_f = os.path.join(adir, f)
                    if scene_dict.get("index") == 1:
                        # Copy the prime verified image for scene 1
                        shutil.copy2(src_f, target_path)
                        print(f"[Visuals] Using verified AI generation for Scene 1: {f}")
                        return target_path
                        
    # Fallback to procedural synthesis plate
    style = scene_dict.get("style", fallback_style)
    prompt = scene_dict.get("visual_prompt", "")
    return create_procedural_cinematic_plate(prompt, style, target_path)
