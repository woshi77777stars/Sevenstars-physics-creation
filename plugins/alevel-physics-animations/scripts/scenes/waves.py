SCENE_META = {
    "topic": "waves",
    "title": "Progressive wave: v = fλ",
    "red_lines": ["waves-v-f-lambda", "waves-particle-vs-wave", "waves-phase-linear"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import standard_axes


class ProgressiveWave(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("The wave travels; particles only vibrate", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 12, 2], [-2, 2, 1], x_length=7.4, y_length=3.2, x_label="x", y_label="y")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        wavelength, frequency, amplitude = 3.0, 1.0, 1.4
        k = 2 * PI / wavelength
        omega = 2 * PI * frequency
        tracker = ValueTracker(0)
        wave = always_redraw(
            lambda: axes.plot(
                lambda x: amplitude * np.sin(k * x - omega * tracker.get_value()),
                x_range=[0, 12],
                color="#3AA6DD",
                stroke_width=3,
            )
        )
        self.add(wave)
        self.play(tracker.animate.set_value(1.0), run_time=2.4, rate_func=linear)

        particle_x = 6.0
        particle = always_redraw(
            lambda: Dot(
                point=axes.c2p(particle_x, amplitude * np.sin(k * particle_x - omega * tracker.get_value())),
                radius=0.13,
                color=YELLOW,
            )
        )
        self.add(particle)
        self.play(tracker.animate.set_value(2.0), run_time=2.4, rate_func=linear)

        speed = Text("v = fλ", font_size=30, color=YELLOW).to_corner(UL, buff=0.7).shift(DOWN * 0.8)
        vibrate = Text("particle vibrates in place; only the wave moves", font_size=26).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(speed), FadeIn(vibrate))
        self.wait(1.0)
