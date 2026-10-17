SCENE_META = {
    "topic": "kinematics",
    "title": "Projectile: launch at an angle",
    "red_lines": ["kinematics-parabola", "kinematics-horizontal-constant", "kinematics-vertical-1-3-5"],
}

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import standard_axes
from redlines import G, projectile_positions


class ProjectileOblique(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Oblique launch: the path is a parabola", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 45, 9], [-6, 14, 4], x_length=7.4, y_length=5.0, x_label="x / m", y_label="y / m")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        u, angle = 20.0, 45.0
        theta = math.radians(angle)
        dt = 0.35
        n = 10
        points = projectile_positions(u, angle, dt, n)
        range_m = u * u * math.sin(2 * theta) / G
        trajectory = axes.plot(
            lambda x: x * math.tan(theta) - G * x * x / (2 * u * u * math.cos(theta) ** 2),
            x_range=[0, range_m],
            color=BLUE_LINE,
        )
        self.play(Create(trajectory), run_time=1.2)

        dots = VGroup()
        for i, (x, y) in enumerate(points):
            dots.add(Dot(point=axes.c2p(x, y), radius=0.09, color=YELLOW))
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.18))

        line = Text("equal-time dots: equal horizontal spacing, symmetric height", font_size=26).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(line))
        self.wait(1.0)
