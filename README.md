# 🎬 Cinematic AI Studio (Hollywood AI Video Pipeline)

An automated, end-to-end Python pipeline engineered to produce high-end, photorealistic cinematic documentary videos for YouTube (16:9 1080p/4K) and YouTube Shorts / Reels (9:16 vertical).

---

## ✨ Features & Capabilities

- **Photorealistic Visuals:** Built-in integration for 35mm film documentary stills with Panavision anamorphic aesthetics, volumetric lighting, and deep caustic effects.
- **Dynamic 2.5D Camera Moves:** Sub-pixel Ken Burns motion engine (`zoom_in`, `zoom_out`, `pan_left`, `pan_right`, `crane_down`) rendered at 30/60 fps with 35mm organic film grain and 2.39:1 anamorphic letterbox bars.
- **Hollywood Color Grading Presets:**
  - `deep_abyss`: High-contrast oceanic shadows with teal/cyan highlights.
  - `dark_mystery`: High chiaroscuro contrast for true crime and ancient enigmas.
  - `epic_history`: Golden sand tones with warm amber sunlight.
  - `blockbuster`: Teal and orange blockbuster grade.
  - `clean_cinema`: Balanced natural film grade.
- **Dramatic Voiceover Engine:** Neural broadcast voices (`en-US-ChristopherNeural`, `en-GB-RyanNeural`, `en-US-AvaNeural`) enhanced with real-time vocal chain: 80Hz high-pass filter, 2.8kHz presence boost, compression, and loudness normalization.
- **Atmospheric Procedural Sound Design:** Synthesizes 44.1kHz stereo sub-drones with stereo detuning, Hans Zimmer-style Braam impacts, and tension risers with Haas stereo widening.
- **Audio Sidechain Ducking:** FFmpeg compressor dynamically attenuates the music bed by -16dB whenever the voiceover speaks, with a smooth 350ms release.
- **Cinematic Typography:** Styled ASS subtitles rendered in `Cinzel` font with scaled borders, drop-shadows, and vertical safe-margin placement.
- **Automated Cloud Sync:** Automatic upload of final rendered masters to Google Drive and GitHub version control.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- FFmpeg 6.0+ (compiled with `libass`, `cairo`, `fontconfig`)
- Dependencies:
  ```bash
  pip install edge-tts numpy scipy pillow
  ```

### 2. Render a 16:9 Widescreen Documentary
```bash
python pipeline.py --topic "The Lost City of Atlantis" --voice christopher --style deep_abyss
```

### 3. Render a 9:16 Vertical Short
```bash
python pipeline.py --topic "The Lost City of Atlantis" --aspect 9:16 --voice christopher --style deep_abyss
```

### 4. Custom Topics
```bash
python pipeline.py --topic "The James Webb Cosmic Revelation" --voice ryan --style dark_mystery
```

---

## 📁 Architecture
```
D:\Cinematic_AI_Studio\
├── engine/
│   ├── storyboard.py     # Script generator & scene breakdown
│   ├── visuals.py        # Visual resolver & procedural backup generator
│   ├── voiceover.py      # Edge-TTS voiceover & vocal EQ chain
│   ├── soundscape.py     # Procedural sub-drone & Braam hit generator
│   ├── motion.py         # 2.5D camera zoompan, grain & color grading
│   ├── typography.py     # Cinzel ASS subtitle generator
│   └── compositor.py     # Final FFmpeg assembly & sidechain ducking
├── assets/
│   ├── fonts/            # Cinzel.ttf
│   └── images/           # Staged high-res AI images
├── outputs/
│   ├── final/            # Master rendered MP4 videos
│   └── projects/         # Intermediate scene renders & project cache
├── upload_to_drive.ps1   # Google Drive sync script
└── pipeline.py           # Master CLI orchestrator
```
