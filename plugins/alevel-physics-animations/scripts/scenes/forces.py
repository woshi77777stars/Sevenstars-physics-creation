SCENE_META = {
    "topic": "forces-density-pressure",
    "title": "Moments and upthrust",
    "red_lines": ["forces-density-pressure-moments-balance", "forces-density-pressure-upthrust-displaced"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class MomentsAndUpthrust(Scene):
    def construct(self):
        title = Text("Moments balance; upthrust = ρgV", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        pivot = Triangle(color=GREY).scale(0.5).move_to(0.2 * DOWN)
        bar = Line(4 * LEFT, 4 * RIGHT, color=WHITE).move_to(0.2 * UP)
        f_left = Arrow(3.2 * LEFT + 0.4 * UP, 3.2 * LEFT - 0.9 * UP, buff=0, color=RED_LINE)
        f_right = Arrow(2.0 * RIGHT + 0.4 * UP, 2.0 * RIGHT - 1.4 * UP, buff=0, color=BLUE_LINE)
        moment = Text("F₁d₁ = F₂d₂  ⇒  no rotation", font_size=28).to_edge(DOWN, buff=1.1)
        self.play(Create(pivot), Create(bar))
        self.play(Create(f_left), Create(f_right), FadeIn(moment))
        self.wait(0.7)

        self.play(FadeOut(VGroup(pivot, bar, f_left, f_right, moment)))
        water = Rectangle(width=4.4, height=2.4, color="#3AA6DD", fill_opacity=0.45).shift(DOWN * 1.1)
        block = Square(side_length=1.1, color=YELLOW).shift(UP * 0.35)
        weight = Arrow(block.get_center(), block.get_center() + DOWN * 1.2, buff=0, color=RED_LINE)
        buoy = Arrow(block.get_bottom(), block.get_bottom() + UP * 1.2, buff=0, color=BLUE_LINE)
        self.play(Create(water), FadeIn(block))
        self.play(Create(weight), Create(buoy))
        note = Text("upthrust = weight of displaced fluid = ρgV", font_size=28).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
