SCENE_META = {
    "topic": "electric-fields",
    "title": "Electric field lines and Coulomb's law",
    "red_lines": ["electric-fields-field-f-q", "electric-fields-coulomb"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class ElectricFields(Scene):
    def construct(self):
        title = Text("Field lines run + → −, and F = qE", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        plus = VGroup(Circle(radius=0.3, color=RED_LINE), Text("+", font_size=32, color=RED_LINE)).move_to(3.4 * LEFT)
        minus = VGroup(Circle(radius=0.3, color=BLUE_LINE), Text("−", font_size=32, color=BLUE_LINE)).move_to(3.4 * RIGHT)
        self.play(FadeIn(plus), FadeIn(minus))

        lines = VGroup()
        for offset in (-0.9, -0.45, 0.0, 0.45, 0.9):
            start = plus.get_center() + offset * UP
            end = minus.get_center() + offset * UP
            arrow = Arrow(start, end, buff=0.3, color=GREY, max_tip_length_to_length_ratio=0.08)
            lines.add(arrow)
        self.play(LaggedStart(*[Create(a) for a in lines], lag_ratio=0.12))

        q = VGroup(Circle(radius=0.18, color=YELLOW), Text("q", font_size=24)).move_to(UP * 1.0)
        force = Arrow(q.get_center(), q.get_center() + RIGHT * 1.4, buff=0.25, color=YELLOW)
        self.play(FadeIn(q), Create(force))
        label = Text("F = qE; point charges: F = kq₁q₂/r²", font_size=27).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(label))
        self.wait(1.0)
