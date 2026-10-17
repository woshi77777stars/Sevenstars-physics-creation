SCENE_META = {
    "topic": "superposition",
    "title": "Interference and stationary waves",
    "red_lines": ["superposition-constructive-n-lambda", "superposition-node-lambda-2", "superposition-double-slit-equal"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import RED_LINE, standard_axes


class InterferenceAndStationaryWaves(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("In phase: amplitude doubles; nodes every λ/2", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 12, 2], [-2.4, 2.4, 1], x_length=7.4, y_length=3.4, x_label="x", y_label="y")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        wavelength = 3.0
        k = 2 * PI / wavelength
        wave_a = axes.plot(lambda x: np.sin(k * x), x_range=[0, 12], color="#3AA6DD")
        wave_b = axes.plot(lambda x: np.sin(k * x), x_range=[0, 12], color=RED_LINE)
        total = axes.plot(lambda x: 2 * np.sin(k * x), x_range=[0, 12], color=YELLOW, stroke_width=4)
        self.play(Create(wave_a), Create(wave_b))
        self.play(Create(total))
        construct = Text("path difference = nλ  ⇒  constructive", font_size=26).to_edge(DOWN, buff=1.0)
        self.play(FadeIn(construct))
        self.wait(0.6)

        self.play(FadeOut(VGroup(wave_a, wave_b, total, construct)))
        tracker = ValueTracker(0)
        stationary = always_redraw(
            lambda: axes.plot(
                lambda x: 2 * np.cos(k * x) * np.sin(2 * PI * tracker.get_value()),
                x_range=[0, 12],
                color="#3AA6DD",
                stroke_width=3,
            )
        )
        self.add(stationary)
        self.play(tracker.animate.set_value(1.5), run_time=3.0, rate_func=linear)

        nodes = VGroup()
        for i in range(0, 48):
            x = i * 0.25
            if abs(np.cos(k * x)) < 1e-6:
                nodes.add(Dot(point=axes.c2p(x, 0), radius=0.09, color=RED_LINE))
        self.play(FadeIn(nodes))
        note = Text("nodes are λ/2 apart", font_size=27, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)
