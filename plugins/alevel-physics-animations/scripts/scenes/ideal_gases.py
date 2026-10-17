SCENE_META = {
    "topic": "ideal-gases",
    "title": "Ideal gas: pV/T is constant",
    "red_lines": ["ideal-gases-pv-t"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE


class IdealGasLaw(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Gas pressure comes from molecular collisions", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        box = Rectangle(width=5.0, height=3.4, color=BLUE_LINE)
        self.play(Create(box))
        tracker = ValueTracker(0)
        particles = VGroup()
        specs = [(1.5, 0.8, 0.7, 1.1), (-1.0, 0.3, 0.9, -0.6), (0.4, -1.1, -0.6, 0.9), (-1.6, -0.8, 0.5, -0.8)]
        for x0, y0, vx, vy in specs:
            dot = always_redraw(
                lambda x0=x0, y0=y0, vx=vx, vy=vy: Dot(
                    point=np.array([
                        ((x0 + vx * tracker.get_value() + 2.5) % 5.0) - 2.5,
                        ((y0 + vy * tracker.get_value() + 1.7) % 3.4) - 1.7,
                        0,
                    ]),
                    radius=0.08,
                    color=YELLOW,
                )
            )
            particles.add(dot)
        self.add(particles)
        self.play(tracker.animate.set_value(6.0), run_time=6.0, rate_func=linear)

        law = Text("pV/T = constant (fixed amount)", font_size=30).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(law))
        self.wait(1.0)
