SCENE_META = {
    "topic": "alternating-currents",
    "title": "RMS values and the ideal transformer",
    "red_lines": ["alternating-currents-rms", "alternating-currents-transformer"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes
from redlines import ideal_transformer, rms


class AlternatingCurrent(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("V_rms = V₀/√2", font_size=34).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 2 * PI, PI / 2], [-6, 6, 2], x_length=6.2, y_length=4.0, x_label="t", y_label="V")
        axes.shift(DOWN * 0.35)
        self.play(Create(axes), FadeIn(labels))
        v0 = 5.0
        wave = axes.plot(lambda t: v0 * np.sin(t), x_range=[0, 2 * PI], color=BLUE_LINE)
        rms_line = DashedLine(axes.c2p(0, rms(v0)), axes.c2p(2 * PI, rms(v0)), color=RED_LINE)
        self.play(Create(wave))
        self.play(Create(rms_line))
        label = Text("V_rms = V₀/√2", font_size=26, color=RED_LINE).next_to(rms_line, UP, buff=0.08)
        self.play(FadeIn(label))
        self.wait(0.6)

        self.play(FadeOut(VGroup(axes, labels, wave, rms_line, label)))
        vs = ideal_transformer(240.0, 1000.0, 100.0)
        primary = VGroup(Rectangle(width=1.0, height=1.8, color=BLUE_LINE), Text("N_p = 1000", font_size=22)).move_to(3.0 * LEFT)
        secondary = VGroup(Rectangle(width=1.0, height=1.8, color=RED_LINE), Text("N_s = 100", font_size=22)).move_to(3.0 * RIGHT)
        core = Line(primary.get_top(), secondary.get_top(), color=GREY)
        self.play(FadeIn(primary), FadeIn(secondary), Create(core))
        ratio = Text(f"V_s = V_p·(N_s/N_p) = {vs:.0f} V", font_size=28).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(ratio))
        self.wait(1.0)
