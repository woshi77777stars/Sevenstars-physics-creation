SCENE_META = {
    "topic": "astronomy-cosmology",
    "title": "Hubble's law and apparent brightness",
    "red_lines": ["astronomy-cosmology-hubble", "astronomy-cosmology-brightness"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes
from redlines import apparent_brightness, hubble_velocity


class HubbleAndBrightness(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("v = H₀d; brightness ∝ 1/d²", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        h0 = 2.2e-18
        axes, labels = standard_axes([0, 8, 2], [0, 600, 100], x_length=5.2, y_length=3.8, x_label="d / Mpc", y_label="v / km s⁻¹")
        axes.shift(DOWN * 0.35 + LEFT * 0.5)
        self.play(Create(axes), FadeIn(labels))
        pc = 3.086e22
        slope = hubble_velocity(1e6 * pc, h0) / 1000.0  # km/s per Mpc
        hubble = axes.plot(lambda d: slope * d, x_range=[0, 8], color=BLUE_LINE)
        self.play(Create(hubble))
        law = Text("straight line through origin: v = H₀d", font_size=24, color=BLUE_LINE).to_edge(DOWN, buff=1.0).shift(LEFT * 0.4)
        self.play(FadeIn(law))
        self.wait(0.6)

        self.play(FadeOut(VGroup(axes, labels, hubble, law)))
        axes2, labels2 = standard_axes([1, 6, 1], [0, 8, 2], x_length=5.2, y_length=3.8, x_label="d", y_label="brightness")
        axes2.shift(DOWN * 0.35)
        self.play(Create(axes2), FadeIn(labels2))
        brightness = axes2.plot(lambda d: apparent_brightness(32 * PI, d), x_range=[1, 6], color=RED_LINE)
        self.play(Create(brightness))
        note = Text("double the distance → brightness falls to ¼", font_size=25, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
