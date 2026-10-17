SCENE_META = {
    "topic": "kinematics",
    "title": "Projectile: horizontal launch",
    "red_lines": [
        "kinematics-horizontal-constant",
        "kinematics-vertical-1-3-5",
        "kinematics-fall-time-independent",
    ],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import standard_axes, vertical_tick
from redlines import G, projectile_positions


class ProjectileHorizontal(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Horizontal launch: x is steady, y accelerates", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 38, 6], [-50, 5, 10], x_length=7.4, y_length=5.4, x_label="x / m", y_label="y / m")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))

        u = 12.0
        dt = 0.5
        n = 7
        points = projectile_positions(u, 0.0, dt, n)
        trajectory = axes.plot(lambda x: -G * x * x / (2 * u * u), x_range=[0, u * (n - 1) * dt], color=BLUE_LINE)
        self.play(Create(trajectory), run_time=1.2)

        dots = VGroup()
        ticks = VGroup()
        for i, (x, y) in enumerate(points):
            dots.add(Dot(point=axes.c2p(x, y), radius=0.09, color=YELLOW))
            ticks.add(vertical_tick(axes, x, y0=y, y1=0))
        self.play(Create(ticks), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.15))

        equal = Text("equal Δx every 0.5 s", font_size=26, color=BLUE_LINE).next_to(trajectory.get_end(), UP, buff=0.1).shift(DOWN * 0.3)
        gaps = Text("vertical gaps grow 1 : 3 : 5 : …", font_size=26, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(equal), FadeIn(gaps))
        self.wait(1.2)
