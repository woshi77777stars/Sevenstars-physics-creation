SCENE_META = {
    "topic": "dc-circuits",
    "title": "Kirchhoff's laws and the potential divider",
    "red_lines": ["dc-circuits-kirchhoff", "dc-circuits-terminal-pd", "dc-circuits-divider"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class KirchhoffAndDivider(Scene):
    def construct(self):
        title = Text("Junctions and loops: current and p.d. balance", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        battery = Rectangle(width=0.7, height=1.4, color=WHITE).move_to(3.6 * LEFT)
        r1 = Rectangle(width=1.6, height=0.5, color=BLUE_LINE).move_to(1.2 * RIGHT + 0.9 * UP)
        r2 = Rectangle(width=1.6, height=0.5, color=RED_LINE).move_to(1.2 * RIGHT + 0.9 * DOWN)
        wire = VGroup(
            Line(battery.get_top(), r1.get_left(), color=GREY),
            Line(battery.get_bottom(), r2.get_left(), color=GREY),
            Line(r1.get_right(), 3.2 * RIGHT, color=GREY),
            Line(r2.get_right(), 3.2 * RIGHT, color=GREY),
        )
        junction = Text("I₁ + I₂ = I₃", font_size=28, color=YELLOW).move_to(3.4 * RIGHT)
        self.play(Create(battery), Create(r1), Create(r2), Create(wire))
        self.play(Write(junction))
        self.wait(0.6)

        self.play(FadeOut(VGroup(battery, r1, r2, wire, junction)))
        vin = Arrow(4.2 * LEFT, 2.2 * LEFT, buff=0, color=YELLOW)
        res_a = Rectangle(width=0.5, height=1.6, color=BLUE_LINE).move_to(0.8 * LEFT)
        res_b = Rectangle(width=0.5, height=1.6, color=RED_LINE).move_to(1.4 * RIGHT)
        vout = Arrow(res_b.get_bottom(), res_b.get_bottom() + DOWN * 1.2, buff=0, color=RED_LINE)
        divider = Text("V_out = V_in · R₂/(R₁+R₂)", font_size=30).to_edge(DOWN, buff=0.35)
        self.play(Create(vin), Create(res_a), Create(res_b), Create(vout))
        self.play(FadeIn(divider))
        self.wait(1.0)
