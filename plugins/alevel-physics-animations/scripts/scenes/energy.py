SCENE_META = {
    "topic": "work-energy-power",
    "title": "Work, kinetic energy and conservation",
    "red_lines": ["work-energy-power-kinetic-energy", "work-energy-power-conservation"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class WorkEnergy(Scene):
    def construct(self):
        title = Text("KE = ½mv²; energy is conserved", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        hill = Line(4.5 * LEFT + 2.4 * DOWN, 4.5 * RIGHT + 2.4 * DOWN, color=GREY)
        top = Dot(point=4.5 * LEFT + 2.4 * DOWN, radius=0.16, color=YELLOW)
        bottom = Dot(point=4.5 * RIGHT + 2.4 * DOWN, radius=0.16, color=YELLOW)
        self.play(Create(hill), FadeIn(top), FadeIn(bottom))

        gpe = Text("GPE = mgh", font_size=28, color=RED_LINE).next_to(top, UP, buff=0.25)
        ke = Text("KE = ½mv²", font_size=28, color=BLUE_LINE).next_to(bottom, UP, buff=0.25)
        self.play(FadeIn(gpe))
        self.play(top.animate.move_to(bottom.get_center()), run_time=1.2)
        self.play(FadeIn(ke))

        conserve = Text("mgh = ½mv²  (no energy lost)", font_size=28).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(conserve))
        self.wait(1.0)
