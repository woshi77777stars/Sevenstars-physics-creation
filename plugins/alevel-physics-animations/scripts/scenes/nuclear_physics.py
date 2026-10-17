SCENE_META = {
    "topic": "nuclear-physics",
    "title": "E = mc² and radioactive half-life",
    "red_lines": ["nuclear-physics-mass-energy", "nuclear-physics-half-life"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes
from redlines import mass_energy, radioactive_decay


class NuclearDecay(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("E = mc² and decay is exponential", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 4, 1], [0, 6, 1], x_length=5.8, y_length=4.2, x_label="t / t½", y_label="N")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        n0, half_life = 5.0, 1.0
        curve = axes.plot(lambda t: radioactive_decay(n0, t, half_life), x_range=[0, 4], color=BLUE_LINE)
        self.play(Create(curve))

        marks = VGroup()
        for i in range(1, 4):
            n = radioactive_decay(n0, i * half_life, half_life)
            marks.add(Dot(point=axes.c2p(i, n), radius=0.08, color=RED_LINE))
            marks.add(DashedLine(axes.c2p(i, 0), axes.c2p(i, n), color=RED_LINE))
        self.play(FadeIn(marks))
        energy = mass_energy(1.0e-3)
        note = Text(f"N₀→N₀/2→N₀/4 in equal times · E = mc² ({energy:.2e} J/g)", font_size=24).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
