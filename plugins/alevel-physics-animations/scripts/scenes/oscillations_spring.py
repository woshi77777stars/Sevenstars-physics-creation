SCENE_META = {
    "topic": "oscillations",
    "title": "Mass on a spring: T = 2π√(m/k)",
    "red_lines": ["oscillations-shm-accel", "oscillations-spring-period"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import zigzag_spring
from redlines import spring_period


class MassSpring(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Spring oscillator: restoring force F = −kx", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        ceiling = Line(4.5 * LEFT + 2.4 * UP, 4.5 * RIGHT + 2.4 * UP, color=GREY)
        top = Dot(point=2.4 * UP, radius=0.05, color=WHITE)
        tracker = ValueTracker(0)
        mass_m, k, amplitude, omega = 1.0, 4.0, 0.55, 2.0
        rest = 2.4 * UP - 2.2 * np.array([0, 1, 0])

        def mass_center():
            return rest + np.array([0, amplitude * np.cos(omega * tracker.get_value()), 0])

        mass = always_redraw(lambda: Square(side_length=0.65, color=YELLOW).move_to(mass_center()))
        spring = zigzag_spring(top, mass, coils=8, width=0.3)
        self.play(Create(ceiling), FadeIn(top), FadeIn(spring), FadeIn(mass))
        self.play(tracker.animate.set_value(2 * PI / omega), run_time=5.0, rate_func=linear)

        period = spring_period(mass_m, k)
        label = Text(f"T = 2π√(m/k) = {period:.2f} s  (amplitude does not matter)", font_size=26).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(label))
        self.wait(1.0)
