SCENE_META = {
    "topic": "circular-motion",
    "title": "Uniform circular motion: a = v²/r inward",
    "red_lines": ["circular-motion-accel-inward", "circular-motion-v-omega-r"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes
from redlines import circular_state


class CircularMotion(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("v = ωr, and a = v²/r points to the centre", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([-3, 3, 1], [-3, 3, 1], x_length=5.4, y_length=5.4)
        axes.shift(DOWN * 0.25)
        self.play(Create(axes), FadeIn(labels))

        r, omega = 2.0, 0.9
        circle = Circle(radius=r, color=GREY).move_to(axes.c2p(0, 0))
        self.play(Create(circle))

        tracker = ValueTracker(0)
        dot = always_redraw(
            lambda: Dot(point=axes.c2p(*circular_state(r, omega, tracker.get_value())[0]), radius=0.11, color=YELLOW)
        )
        velocity = always_redraw(
            lambda: Arrow(
                axes.c2p(*circular_state(r, omega, tracker.get_value())[0]),
                axes.c2p(*(circular_state(r, omega, tracker.get_value())[0][i] + 0.9 * circular_state(r, omega, tracker.get_value())[1][i] for i in range(2))),
                buff=0, color=BLUE_LINE,
            )
        )
        accel = always_redraw(
            lambda: Arrow(
                axes.c2p(*circular_state(r, omega, tracker.get_value())[0]),
                axes.c2p(*(circular_state(r, omega, tracker.get_value())[0][i] + 0.7 * circular_state(r, omega, tracker.get_value())[2][i] for i in range(2))),
                buff=0, color=RED_LINE,
            )
        )
        self.add(dot, velocity, accel)
        self.play(tracker.animate.set_value(2 * PI / omega), run_time=5.0, rate_func=linear)

        note = Text("a ⊥ v, always toward the centre", font_size=27, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
