SCENE_META = {
    "topic": "oscillations",
    "title": "Simple pendulum: T = 2π√(L/g)",
    "red_lines": ["oscillations-shm-accel", "oscillations-pendulum-period"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import RED_LINE
from redlines import pendulum_period


class SimplePendulum(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Small angles: SHM, period set by L only", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        pivot = Dot(point=UP * 2.2, radius=0.09, color=WHITE)
        length, theta0, omega = 3.0, 0.28, 1.8
        tracker = ValueTracker(0)

        def bob_pos():
            theta = theta0 * np.cos(omega * tracker.get_value())
            return np.array([
                pivot.get_center()[0] + length * np.sin(theta),
                pivot.get_center()[1] - length * np.cos(theta),
                0,
            ])

        rod = always_redraw(lambda: Line(pivot.get_center(), bob_pos(), color=WHITE))
        bob = always_redraw(lambda: Dot(point=bob_pos(), radius=0.18, color=YELLOW))
        self.play(FadeIn(pivot), FadeIn(rod), FadeIn(bob))
        self.play(tracker.animate.set_value(2 * PI / omega), run_time=5.0, rate_func=linear)

        period = pendulum_period(length)
        label = Text(f"T = 2π√(L/g) = {period:.2f} s  (mass and small amplitude do not matter)", font_size=26).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(label))
        self.wait(1.0)
