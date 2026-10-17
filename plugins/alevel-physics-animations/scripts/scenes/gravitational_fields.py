SCENE_META = {
    "topic": "gravitational-fields",
    "title": "Gravitational field: inverse-square and orbits",
    "red_lines": ["gravitational-fields-inverse-square", "gravitational-fields-kepler"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes


class GravitationalFields(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("g = GM/r² and T² ∝ r³", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([1, 8, 1], [0, 10, 2], x_length=5.2, y_length=4.0, x_label="r", y_label="g")
        axes.shift(DOWN * 0.35 + LEFT * 0.5)
        self.play(Create(axes), FadeIn(labels))
        curve = axes.plot(lambda r: 9.0 / (r * r), x_range=[1, 8], color=RED_LINE)
        self.play(Create(curve))
        note = Text("double the distance → g falls to ¼", font_size=25, color=RED_LINE).to_edge(DOWN, buff=0.9).shift(LEFT * 0.4)
        self.play(FadeIn(note))
        self.wait(0.6)

        self.play(FadeOut(VGroup(axes, labels, curve, note)))
        planet = Dot(point=ORIGIN, radius=0.28, color=BLUE_LINE)
        orbit = Circle(radius=2.0, color=GREY)
        tracker = ValueTracker(0)
        satellite = always_redraw(
            lambda: Dot(point=orbit.get_center() + np.array([2.0 * np.cos(tracker.get_value()), 2.0 * np.sin(tracker.get_value()), 0]), radius=0.12, color=YELLOW)
        )
        self.play(FadeIn(planet), Create(orbit), FadeIn(satellite))
        self.play(tracker.animate.set_value(2 * PI), run_time=5.0, rate_func=linear)
        kepler = Text("T² ∝ r³  (Kepler's third law)", font_size=28).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(kepler))
        self.wait(1.0)
