import os, json, re
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class Scene:
    index: int
    title: str
    narration: str
    visual_prompt: str
    motion_type: str = "zoom_in"
    style: str = "clean_cinema"
    sfx_cue: str = "drone"
    image_filename: Optional[str] = None

PRESET_DOCUMENTARIES = {
    "atlantis": {
        "title": "The Lost City of Atlantis: Earth's Sunken Empire",
        "style": "deep_abyss",
        "scenes": [
            Scene(
                index=1,
                title="The Ancient Legend",
                narration="For over two thousand years, human history has whispered of an empire that vanished in a single cataclysmic night.",
                visual_prompt="Cinematic documentary photograph of submerged ancient Atlantis citadel ruins, monumental stone columns wrapped in bioluminescent deep sea coral, beams of twilight piercing down through crystalline ocean water, anamorphic 35mm film still, National Geographic cinematography, photorealistic 8k.",
                motion_type="zoom_in",
                style="deep_abyss",
                sfx_cue="cinematic_hit",
                image_filename="scene_01_atlantis_citadel.jpg"
            ),
            Scene(
                index=2,
                title="The Sinking of the Titans",
                narration="Plato described an advanced civilization beyond the Pillars of Hercules—blessed with boundless wealth, sacred architecture, and mastery over the elements.",
                visual_prompt="Majestic golden statues and colossal Greco-Roman marble palaces on ocean floor, schools of manta rays gliding past sunken amphitheater, dramatic volumetric god rays, dark turquoise ocean depths, atmospheric haze, ultra-detailed 35mm film still.",
                motion_type="pan_right",
                style="deep_abyss",
                sfx_cue="drone",
                image_filename="scene_02_atlantis_palace.jpg"
            ),
            Scene(
                index=3,
                title="The Submerged Monolith",
                narration="Yet hubris was their downfall. Earthquakes shattered their foundations, and the black ocean swallowed their towers into the abyss.",
                visual_prompt="Massive cracked stone monolith on seabed inscribed with glowing concentric circular runes, deep ocean trench precipice, submersible exploration submarine lights illuminating the ancient megalith, cinematic sci-fi documentary, ultra-realistic.",
                motion_type="crane_down",
                style="deep_abyss",
                sfx_cue="riser",
                image_filename="scene_03_atlantis_monolith.jpg"
            ),
            Scene(
                index=4,
                title="The Unsolved Enigma",
                narration="Today, hidden thousands of meters beneath uncharted waves, the silent ruins wait... waiting for the day their truth will rise once more.",
                visual_prompt="Wide establishing shot of vast sunken metropolis under dark oceanic trench, ancient concentric rings of canals carved into bedrock, tiny exploratory ROV drone hovering in distance, haunting epic mood, IMAX 70mm cinematic scale.",
                motion_type="zoom_out",
                style="deep_abyss",
                sfx_cue="cinematic_hit",
                image_filename="scene_04_atlantis_abyss.jpg"
            )
        ]
    },
    "mariana": {
        "title": "The Mariana Trench: Journey into the Void",
        "style": "deep_abyss",
        "scenes": [
            Scene(
                index=1,
                title="Descent into Darkness",
                narration="Thirty-six thousand feet beneath the surface of the Pacific lies the Challenger Deep—the darkest and most unforgiving realm on Earth.",
                visual_prompt="High-tech deep sea exploration submersible descending through pitch black ocean water, powerful halogen searchlights cutting through particle marine snow, extreme depths, cinematic BBC Blue Planet documentary style, 8k.",
                motion_type="crane_down",
                style="deep_abyss",
                sfx_cue="cinematic_hit",
                image_filename="scene_01_mariana_descent.jpg"
            ),
            Scene(
                index=2,
                title="Crushing Atmospheric Pressure",
                narration="Here, the pressure exceeds one thousand atmospheres—a crushing force equivalent to fifty jumbo jets stacked upon a human body.",
                visual_prompt="Macro close-up of titanium submarine hull with condensation droplets, warning depth gauge reading 10920 meters, through circular reinforced viewport revealing pitch black abyss, volumetric interior glow, hyper-realistic.",
                motion_type="zoom_in",
                style="deep_abyss",
                sfx_cue="drone",
                image_filename="scene_02_mariana_pressure.jpg"
            ),
            Scene(
                index=3,
                title="Alien Ecosystems",
                narration="Yet against all scientific belief, life does not merely survive here—it thrives in forms stranger than science fiction.",
                visual_prompt="Ghostly translucent ethereal snailfish swimming gracefully beside volcanic hydrothermal vents, shimmering mineral towers venting black smoke, strange glowing bioluminescent anemones, otherworldly deep sea photography.",
                motion_type="pan_left",
                style="deep_abyss",
                sfx_cue="drone",
                image_filename="scene_03_mariana_life.jpg"
            ),
            Scene(
                index=4,
                title="The Final Frontier",
                narration="We know more about the surface of Mars than the bottom of our own oceans. The deep remains our planet's greatest secret.",
                visual_prompt="Breathtaking underwater panoramic vista of the Challenger Deep seafloor trench stretching into infinity, solitary submersible illumination beacon, majestic geological chasm, 35mm cinematic film.",
                motion_type="zoom_out",
                style="deep_abyss",
                sfx_cue="cinematic_hit",
                image_filename="scene_04_mariana_chasm.jpg"
            )
        ]
    },
    "pyramids": {
        "title": "The Great Pyramids: Architects of Eternity",
        "style": "epic_history",
        "scenes": [
            Scene(
                index=1,
                title="The Giza Plateau",
                narration="Rising from the golden sands of Giza, the Great Pyramid has defied the relentless erosion of four thousand five hundred years.",
                visual_prompt="Breathtaking cinematic wide shot of the Great Pyramids of Giza at golden sunset, dust haze catching warm amber sunbeams, camels walking along sand dunes in foreground, IMAX 70mm documentary film still, photorealistic.",
                motion_type="zoom_in",
                style="epic_history",
                sfx_cue="cinematic_hit",
                image_filename="scene_01_pyramids_plateau.jpg"
            ),
            Scene(
                index=2,
                title="The Impossible Masonry",
                narration="Two point three million stone blocks, each weighing up to eighty tons, aligned with astronomical precision to the true cardinal points.",
                visual_prompt="Dramatic low-angle shot of limestone pyramid mega-blocks towering into deep azure desert sky, perfect geometric angles, microscopic stone grain and desert patina, Ridley Scott cinematic framing, hyper-detailed.",
                motion_type="pan_right",
                style="epic_history",
                sfx_cue="drone",
                image_filename="scene_02_pyramids_masonry.jpg"
            ),
            Scene(
                index=3,
                title="Stargates of the Pharaohs",
                narration="Ancient texts reveal shafts pointed directly toward the belt of Orion—a cosmic stairway designed to propel a king into immortality.",
                visual_prompt="Nighttime time-lapse view of the Great Pyramid with the Milky Way galaxy and Orion constellation gleaming directly above its apex, ancient starlight reflecting on desert sands, National Geographic astronomical photography.",
                motion_type="crane_down",
                style="epic_history",
                sfx_cue="riser",
                image_filename="scene_03_pyramids_stars.jpg"
            ),
            Scene(
                index=4,
                title="The Unbroken Riddle",
                narration="No toolmarks explain their speed. No blueprints survived. And eternity has guarded their architect's name in silence.",
                visual_prompt="The Great Sphinx of Giza framed with the Pyramids in dawn mist, dramatic shadows cutting across weathered limestone face, cinematic historical epic, evocative lighting, photorealistic 8k.",
                motion_type="zoom_out",
                style="epic_history",
                sfx_cue="cinematic_hit",
                image_filename="scene_04_pyramids_sphinx.jpg"
            )
        ]
    },
    "space": {
        "title": "Cosmic Genesis: Beyond the Edge of Time",
        "style": "dark_mystery",
        "scenes": [
            Scene(
                index=1,
                title="The First Light",
                narration="Thirteen point eight billion years ago, the universe ignited from an infinitesimal singularity into infinite expanding space.",
                visual_prompt="Photorealistic cosmic birth, vibrant celestial nebula in deep space glowing with radiant magenta and cyan interstellar dust, newborn stars igniting, James Webb Space Telescope deep field photography, 8k resolution.",
                motion_type="zoom_in",
                style="dark_mystery",
                sfx_cue="cinematic_hit",
                image_filename="scene_01_space_singularity.jpg"
            ),
            Scene(
                index=2,
                title="Stellar Forges",
                narration="Inside titanic cosmic crucibles, dying stars fused the very atoms of iron, calcium, and carbon that now flow within our veins.",
                visual_prompt="Supernova explosion shockwave rippling through colorful interstellar gas clouds, molten stellar core, hyper-detailed cosmic physics visualization, Interstellar movie cinematography.",
                motion_type="pan_left",
                style="dark_mystery",
                sfx_cue="drone",
                image_filename="scene_02_space_supernova.jpg"
            ),
            Scene(
                index=3,
                title="The Event Horizon",
                narration="At the center of every galaxy lurks a supermassive black hole—a tear in spacetime where light, time, and gravity cease to exist.",
                visual_prompt="Cinematic view of a gargantuan spinning supermassive black hole with glowing relativistic accretion disk, gravitational lensing bending starfield behind it, ultra-high fidelity scientific visualization.",
                motion_type="crane_down",
                style="dark_mystery",
                sfx_cue="riser",
                image_filename="scene_03_space_blackhole.jpg"
            ),
            Scene(
                index=4,
                title="The Pale Blue Dot",
                narration="Across trillions of lightyears of silence, we stand as the universe looking back upon itself—conscious, curious, and alive.",
                visual_prompt="Planet Earth viewed from lunar orbit, crescent sunlight illuminating the Pacific ocean, thin delicate blue atmospheric ribbon, vast cold black star-studded cosmos, Apollo photography aesthetics, 70mm IMAX.",
                motion_type="zoom_out",
                style="dark_mystery",
                sfx_cue="cinematic_hit",
                image_filename="scene_04_space_earth.jpg"
            )
        ]
    }
}

class CinematicStoryboard:
    """
    Generates Hollywood-grade documentary scripts, visual shot lists,
    and camera choreography for any topic.
    """
    def __init__(self, topic: str, style: str = "auto", custom_scenes: List[Scene] = None):
        self.topic = topic
        self.style = style
        self.custom_scenes = custom_scenes or []
        
    def generate(self) -> dict:
        # Check presets first
        topic_lower = self.topic.lower()
        matched_key = None
        for key in PRESET_DOCUMENTARIES:
            if key in topic_lower:
                matched_key = key
                break
                
        if matched_key and not self.custom_scenes:
            preset = PRESET_DOCUMENTARIES[matched_key]
            chosen_style = self.style if self.style != "auto" else preset["style"]
            scenes = preset["scenes"]
            # Apply style override if specified
            for sc in scenes:
                if self.style != "auto":
                    sc.style = chosen_style
            return {
                "topic": self.topic,
                "title": preset["title"],
                "style": chosen_style,
                "scenes": [asdict(s) for s in scenes]
            }
            
        if self.custom_scenes:
            chosen_style = self.style if self.style != "auto" else "clean_cinema"
            return {
                "topic": self.topic,
                "title": self.topic.title(),
                "style": chosen_style,
                "scenes": [asdict(s) for s in self.custom_scenes]
            }
            
        # Dynamic storyboard generation for arbitrary topics
        return self._generate_dynamic_storyboard()
        
    def _generate_dynamic_storyboard(self) -> dict:
        clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', self.topic).title()
        style = self.style if self.style != "auto" else "dark_mystery"
        
        scenes = [
            Scene(
                index=1,
                title="The Genesis",
                narration=f"In the beginning, the story of {clean_topic} was etched into the shadows of human curiosity.",
                visual_prompt=f"Cinematic documentary establishing wide shot of {clean_topic}, dramatic atmospheric volumetric fog, high-contrast chiaroscuro lighting, Panavision 35mm anamorphic film still, National Geographic photography, 8k resolution.",
                motion_type="zoom_in",
                style=style,
                sfx_cue="cinematic_hit",
                image_filename="scene_01_genesis.jpg"
            ),
            Scene(
                index=2,
                title="The Monumental Secret",
                narration=f"Every detail, every fragment uncovered by explorers revealed an intricate design far beyond its era.",
                visual_prompt=f"Intricate detailed close-up shot of {clean_topic}, hyper-realistic textures, dramatic lighting raking across surface, golden ratio composition, BBC documentary style cinematography.",
                motion_type="pan_right",
                style=style,
                sfx_cue="drone",
                image_filename="scene_02_secret.jpg"
            ),
            Scene(
                index=3,
                title="The Turning Point",
                narration=f"Then came the turning point—where myth collided with undeniable reality, shattering centuries of certainty.",
                visual_prompt=f"Dramatic low-angle cinematic shot of {clean_topic}, epic scale, storm clouds gathering, divine sunbeams breaking through darkness, masterclass film cinematography.",
                motion_type="crane_down",
                style=style,
                sfx_cue="riser",
                image_filename="scene_03_turning_point.jpg"
            ),
            Scene(
                index=4,
                title="The Legacy",
                narration=f"Today, the legacy of {clean_topic} endures as a testament to the unquenchable human spirit.",
                visual_prompt=f"Breathtaking sweeping panoramic vista of {clean_topic} at sunset, warm cinematic glow, tranquil atmospheric majesty, IMAX 70mm aesthetic, photorealistic.",
                motion_type="zoom_out",
                style=style,
                sfx_cue="cinematic_hit",
                image_filename="scene_04_legacy.jpg"
            )
        ]
        
        return {
            "topic": self.topic,
            "title": f"{clean_topic}: A Cinematic Journey",
            "style": style,
            "scenes": [asdict(s) for s in scenes]
        }
