SCENE_META = {
    "topic": "temperature",
    "title": "Temperature and thermal equilibrium",
    "red_lines": ["temperature-zeroth-law"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class ThermalEquilibrium(Scene):
    def construct(self):
        title = Text("Heat flows from hot to cold until equilibrium", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        hot = VGroup(Rectangle(width=1.6, height=2.2, color=RED_LINE, fill_opacity=0.8), Text("hot", font_size=28)).move_to(2.6 * LEFT)
        cold = VGroup(Rectangle(width=1.6, height=2.2, color=BLUE_LINE, fill_opacity=0.8), Text("cold", font_size=28)).move_to(2.6 * RIGHT)
        self.play(FadeIn(hot), FadeIn(cold))

        heat = Arrow(hot.get_right(), cold.get_left(), buff=0.12, color=YELLOW)
        self.play(Create(heat))
        self.play(Indicate(heat, color=YELLOW))
        zero = Text("zeroth law: temperature is defined by thermal equilibrium", font_size=26).to_edge(DOWN, buff=0.75)
        never = Text("heat never flows cold → hot spontaneously", font_size=26, color=RED_LINE).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(zero), FadeIn(never))
        self.wait(1.2)
