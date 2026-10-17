SCENE_META = {
    "topic": "kinematics",
    "title": "Free fall: distance grows as t²",
    "red_lines": ["kinematics-parabola", "kinematics-vertical-1-3-5"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from redlines import free_fall_distance


class FreeFall(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Free fall from rest", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([-1.5, 1.5, 1], [0, 12, 2], x_length=3.0, y_length=5.2, y_label="s = ½gt² / m")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        dt = 0.3
        n = 7
        distances = [free_fall_distance(i * dt) for i in range(n)]
        dots = VGroup()
        ticks = VGroup()
        for i, d in enumerate(distances):
            dots.add(Dot(point=axes.c2p(0, -d), radius=0.1, color=YELLOW))
            ticks.add(Line(axes.c2p(-0.3, -d), axes.c2p(0.3, -d), color=GREY))
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.25))
        self.play(Create(ticks))

        gaps = [round(distances[i] - distances[i - 1], 2) for i in range(1, n)]
        text = Text("gaps in equal times: 1 : 3 : 5 : …", font_size=28, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(text))
        self.wait(1.0)
