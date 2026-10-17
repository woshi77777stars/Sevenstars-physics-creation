SCENE_META = {
    "topic": "particle-physics",
    "title": "Conservation in particle interactions",
    "red_lines": ["particle-physics-conservation"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class ParticleConservation(Scene):
    def construct(self):
        title = Text("β⁻ decay: charge, baryon and lepton numbers are conserved", font_size=32).to_edge(UP)
        self.play(FadeIn(title))

        neutron = VGroup(Circle(radius=0.45, color=WHITE), Text("n", font_size=28)).move_to(3.4 * LEFT)
        proton = VGroup(Circle(radius=0.45, color=BLUE_LINE), Text("p", font_size=28)).move_to(0.8 * LEFT + 1.2 * UP)
        electron = VGroup(Circle(radius=0.3, color=YELLOW), Text("e⁻", font_size=24)).move_to(0.8 * LEFT + 0.2 * DOWN)
        antineutrino = VGroup(Circle(radius=0.3, color=GREY), Text("ν̄", font_size=24)).move_to(2.2 * RIGHT + 0.6 * DOWN)
        arrow_a = Arrow(neutron.get_right(), proton.get_left(), buff=0.15, color=GREY)
        arrow_b = Arrow(neutron.get_right(), electron.get_left(), buff=0.15, color=GREY)
        arrow_c = Arrow(neutron.get_right(), antineutrino.get_left(), buff=0.15, color=GREY)
        self.play(FadeIn(neutron))
        self.play(Create(arrow_a), Create(arrow_b), Create(arrow_c))
        self.play(FadeIn(proton), FadeIn(electron), FadeIn(antineutrino))

        charge = Text("charge: 0 = +1 − 1 + 0", font_size=26).to_edge(DOWN, buff=1.25)
        baryon = Text("baryon: 1 = 1 + 0 + 0", font_size=26).to_edge(DOWN, buff=0.8)
        lepton = Text("lepton: 0 = 0 + 1 − 1", font_size=26).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(charge), FadeIn(baryon), FadeIn(lepton))
        self.wait(1.2)
