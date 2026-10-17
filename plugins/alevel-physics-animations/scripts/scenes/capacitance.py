SCENE_META = {
    "topic": "capacitance",
    "title": "Capacitor discharge: τ = RC",
    "red_lines": ["capacitance-q-cv", "capacitance-tau-rc"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes
from redlines import rc_discharge


class CapacitorDischarge(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Q = CV, then V decays exponentially with τ = RC", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 5, 1], [0, 6, 1], x_length=5.8, y_length=4.2, x_label="t / τ", y_label="V / V")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        v0, tau = 5.0, 1.0
        curve = axes.plot(lambda t: rc_discharge(v0, t, tau), x_range=[0, 5], color=BLUE_LINE)
        self.play(Create(curve))

        markers = VGroup()
        for i in range(1, 5):
            v = rc_discharge(v0, i * tau, tau)
            markers.add(Dot(point=axes.c2p(i, v), radius=0.08, color=RED_LINE))
            markers.add(DashedLine(axes.c2p(i, 0), axes.c2p(i, v), color=RED_LINE))
        self.play(FadeIn(markers))
        note = Text("every τ, the voltage falls by a factor of e", font_size=27, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
