SCENE_META = {
    "topic": "magnetic-fields",
    "title": "Magnetic force is perpendicular to B and v",
    "red_lines": ["magnetic-fields-perpendicular", "magnetic-fields-right-hand-rule"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class MagneticFields(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("F = Bqv sinθ, perpendicular to both B and v", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        wire = Line(2.6 * UP, 2.6 * DOWN, color=YELLOW, stroke_width=5)
        current = Arrow(wire.get_bottom(), wire.get_top(), buff=0, color=YELLOW).next_to(wire, LEFT, buff=0.15)
        self.play(Create(wire), Create(current))

        circles = VGroup(*[Circle(radius=r, color=BLUE_LINE, stroke_width=1.5) for r in (0.8, 1.4, 2.0)])
        self.play(LaggedStart(*[Create(c) for c in circles], lag_ratio=0.15))
        b_label = Text("B circles the current (right-hand rule)", font_size=25, color=BLUE_LINE).to_corner(DR, buff=0.6).shift(UP * 0.2)
        self.play(FadeIn(b_label))
        self.wait(0.6)

        self.play(FadeOut(VGroup(wire, current, circles, b_label)))
        b_field = VGroup(*[Arrow(3.4 * LEFT + y * UP, 5.2 * RIGHT + y * UP, buff=0, color=BLUE_LINE) for y in (-0.7, 0, 0.7)])
        charge = Dot(point=ORIGIN, radius=0.14, color=YELLOW)
        v_vec = Arrow(ORIGIN, RIGHT * 1.8, buff=0.3, color=YELLOW)
        f_vec = Arrow(ORIGIN, UP * 1.8, buff=0.3, color=RED_LINE)
        self.play(FadeIn(b_field), FadeIn(charge), Create(v_vec), Create(f_vec))
        note = Text("F is ⊥ to both B and v: circular motion results", font_size=26, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
