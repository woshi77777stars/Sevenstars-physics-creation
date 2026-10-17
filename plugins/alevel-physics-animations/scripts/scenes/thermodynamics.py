SCENE_META = {
    "topic": "thermodynamics",
    "title": "First law and p–V curves",
    "red_lines": ["thermodynamics-first-law", "thermodynamics-adiabatic-vs-isothermal"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes


class FirstLawPV(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("ΔU = q + W; adiabatic curves are steeper", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([1, 8, 1], [0, 10, 2], x_length=5.4, y_length=4.0, x_label="V", y_label="p")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        gamma = 5.0 / 3.0
        isothermal = axes.plot(lambda v: 9.0 / v, x_range=[1.4, 8], color=BLUE_LINE)
        adiabatic = axes.plot(lambda v: 12.0 / (v ** gamma), x_range=[1.4, 8], color=RED_LINE)
        self.play(Create(isothermal))
        self.play(Create(adiabatic))
        iso = Text("isothermal: pV = const", font_size=24, color=BLUE_LINE).to_edge(DOWN, buff=1.0)
        adi = Text("adiabatic: pV^γ = const (steeper)", font_size=24, color=RED_LINE).to_edge(DOWN, buff=0.55)
        law = Text("ΔU = q + W", font_size=28).to_corner(UR, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(iso), FadeIn(adi), FadeIn(law))
        self.wait(1.0)
