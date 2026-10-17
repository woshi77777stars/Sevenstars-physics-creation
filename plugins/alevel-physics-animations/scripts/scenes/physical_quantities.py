SCENE_META = {
    "topic": "physical-quantities",
    "title": "Physical quantities and units",
    "red_lines": ["physical-quantities-units-homogeneous", "physical-quantities-vector-addition"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class UnitsAndVectors(Scene):
    def construct(self):
        title = Text("Units are homogeneous", font_size=34).to_edge(UP)
        equation = Text("s = ut + ½at²", font_size=30)
        check = Text("m = (m/s)·s + (m/s²)·s² = m  ✓", font_size=30, color=BLUE).next_to(equation, DOWN, buff=0.5)
        self.play(Write(title))
        self.play(FadeIn(equation, shift=UP * 0.3))
        self.play(FadeIn(check, shift=UP * 0.3))
        self.wait(0.6)

        self.play(FadeOut(VGroup(equation, check)))
        title2 = Text("Vectors add tip-to-tail", font_size=34).to_edge(UP)
        self.play(Transform(title, title2))

        origin = 3 * LEFT + 0.8 * DOWN
        a = Arrow(origin, origin + 3 * RIGHT, buff=0, color=BLUE_LINE)
        b = Arrow(origin + 3 * RIGHT, origin + 3 * RIGHT + 2.2 * UP, buff=0, color=RED_LINE)
        r = Arrow(origin, origin + 3 * RIGHT + 2.2 * UP, buff=0, color=YELLOW)
        self.play(Create(a), Create(b))
        self.play(Create(r))
        self.play(Indicate(r, color=YELLOW))
        result = Text("resultant = vector sum", font_size=28).next_to(r, RIGHT, buff=0.3)
        self.play(FadeIn(result, shift=RIGHT * 0.2))
        self.wait(1.0)
