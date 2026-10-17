SCENE_META = {
    "topic": "quantum-physics",
    "title": "Photoelectric effect: threshold frequency",
    "red_lines": ["quantum-physics-photon-energy", "quantum-physics-threshold"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class PhotoelectricEffect(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("E = hf, and no emission below the threshold", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        metal = Rectangle(width=3.4, height=1.6, color="#8B949E", fill_opacity=0.5).move_to(3.4 * RIGHT)
        metal_label = Text("metal", font_size=24).move_to(metal.get_center())
        self.play(Create(metal), FadeIn(metal_label))

        low_frequency_photons = VGroup(
            Arrow(3.4 * LEFT + 0.7 * UP, metal.get_left() + 0.7 * UP, buff=0.2, color=BLUE_LINE),
            Arrow(3.4 * LEFT + 0.0 * UP, metal.get_left() + 0.0 * UP, buff=0.2, color=BLUE_LINE),
            Arrow(3.4 * LEFT - 0.7 * UP, metal.get_left() - 0.7 * UP, buff=0.2, color=BLUE_LINE),
        )
        self.play(LaggedStart(*[Create(a) for a in low_frequency_photons], lag_ratio=0.2))
        no_emission = Text("f < f₀: no electrons, even at high intensity", font_size=26, color=RED_LINE).to_edge(DOWN, buff=0.8)
        self.play(FadeIn(no_emission))
        self.wait(0.8)

        self.play(FadeOut(low_frequency_photons), FadeOut(no_emission))
        high_photon = Arrow(3.4 * LEFT, metal.get_left(), buff=0.2, color=YELLOW)
        electron = Dot(point=metal.get_right() + RIGHT * 0.2, radius=0.12, color=YELLOW)
        self.play(Create(high_photon))
        self.play(electron.animate.shift(RIGHT * 2.2), run_time=0.8)
        emission = Text("f ≥ f₀: one photon → one electron (E = hf)", font_size=26).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(emission))
        self.wait(1.0)
