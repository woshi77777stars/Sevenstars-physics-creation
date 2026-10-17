SCENE_META = {
    "topic": "deformation",
    "title": "Hooke's law and stored energy",
    "red_lines": ["deformation-hooke-limit", "deformation-area-energy"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class HookeAndEnergy(Scene):
    def construct(self):
        title = Text("F ∝ x below the elastic limit", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 8, 2], [0, 6, 2], x_length=5.4, y_length=4.2, x_label="extension x", y_label="force F")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        k = 1.0
        line = axes.plot(lambda x: k * x, x_range=[0, 4], color=BLUE_LINE)
        dashed = axes.plot(lambda x: 4.0, x_range=[4, 7], color=RED_LINE).set_style(stroke_width=2)
        limit = vertical_tick(axes, 4, y0=0, y1=4, color=RED_LINE, dashed=True)
        triangle = Polygon(
            axes.c2p(0, 0), axes.c2p(4, 4), axes.c2p(4, 0),
            color="#EAB308", fill_opacity=0.35, stroke_width=0,
        )
        self.play(Create(line))
        self.play(FadeIn(triangle))
        self.play(Create(limit), Create(dashed))
        energy = Text("energy stored = area under F–x = ½kx²", font_size=27).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(energy))
        self.wait(1.0)
