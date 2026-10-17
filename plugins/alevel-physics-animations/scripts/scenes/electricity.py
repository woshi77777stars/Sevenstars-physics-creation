SCENE_META = {
    "topic": "electricity",
    "title": "Ohm's law, power and I–V shapes",
    "red_lines": ["electricity-ohms-law", "electricity-power", "electricity-iv-shapes"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes


class OhmAndPower(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("V = IR · P = VI = I²R", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([-3, 3, 1], [-3, 3, 1], x_length=5.6, y_length=4.4, x_label="V", y_label="I")
        axes.shift(DOWN * 0.35 + LEFT * 0.4)
        self.play(Create(axes), FadeIn(labels))

        ohmic = axes.plot(lambda v: v / 2.0, x_range=[-3, 3], color=BLUE_LINE)
        diode = axes.plot(lambda v: np.clip(np.exp(v) - 1, 0, 5), x_range=[-3, 2.5], color=RED_LINE)
        self.play(Create(ohmic))
        self.play(Create(diode))

        ohm_note = Text("ohmic: straight line through origin", font_size=24, color=BLUE_LINE).to_edge(DOWN, buff=1.0).shift(RIGHT * 0.2)
        diode_note = Text("diode: conducts one way only", font_size=24, color=RED_LINE).to_edge(DOWN, buff=0.55).shift(RIGHT * 0.2)
        self.play(FadeIn(ohm_note), FadeIn(diode_note))
        self.wait(1.0)
