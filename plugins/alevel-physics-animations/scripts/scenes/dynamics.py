SCENE_META = {
    "topic": "dynamics",
    "title": "Newton's second law and momentum",
    "red_lines": ["dynamics-fma", "dynamics-momentum-conserved"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE


class NewtonAndMomentum(Scene):
    def construct(self):
        title = Text("F = ma, and momentum is conserved", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        box = Square(side_length=1.0, color=BLUE_LINE).move_to(3.5 * LEFT)
        force = Arrow(box.get_left(), box.get_left() + 1.8 * RIGHT, buff=0, color=RED_LINE)
        label = Text("F", font_size=28, color=RED_LINE).next_to(force, UP, buff=0.08)
        eq = Text("a = F / m", font_size=30).next_to(box, DOWN, buff=0.6)
        self.play(Create(box), Create(force), FadeIn(label), FadeIn(eq))

        tracker = ValueTracker(0)
        moving = always_redraw(lambda: box.copy().move_to(box.get_center() + RIGHT * 0.6 * tracker.get_value() ** 2))
        self.add(moving)
        self.play(tracker.animate.set_value(2.0), run_time=1.6)
        self.wait(0.4)

        self.play(FadeOut(VGroup(box, moving, force, label, eq)))
        title2 = Text("Collision: total p before = total p after", font_size=34).to_edge(UP)
        self.play(Transform(title, title2))

        m1 = Circle(radius=0.35, color=BLUE_LINE).move_to(3.2 * LEFT)
        m2 = Circle(radius=0.35, color=RED_LINE).move_to(0.6 * LEFT)
        before = Text("p = m₁v₁ + m₂v₂", font_size=30).to_edge(DOWN, buff=0.8)
        after = Text("= m₁v₁′ + m₂v₂′", font_size=30).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(m1), FadeIn(m2))
        self.play(m1.animate.shift(RIGHT * 2.4), m2.animate.shift(RIGHT * 0.6), run_time=1.2)
        self.play(Write(before))
        self.play(Write(after))
        self.wait(1.0)
