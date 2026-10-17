SCENE_META = {
    "topic": "medical-physics",
    "title": "Ultrasound echoes and X-ray attenuation",
    "red_lines": ["medical-physics-ultrasound", "medical-physics-xray-attenuation"],
}

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from _common import BLUE_LINE, RED_LINE, standard_axes, vertical_tick
from redlines import xray_attenuation


class MedicalPhysics(Scene):
    def construct(self):
        self.camera.background_color = "#0F172A"
        title = Text("Ultrasound reflects at interfaces; X-rays attenuate", font_size=32).to_edge(UP)
        self.play(FadeIn(title))

        axes, labels = standard_axes([0, 8, 1], [-1.5, 1.5, 0.5], x_length=5.4, y_length=2.6, x_label="x", y_label="p")
        axes.shift(DOWN * 0.35 + LEFT * 0.4)
        self.play(Create(axes), FadeIn(labels))
        boundary = vertical_tick(axes, 4.0, y0=-1.5, y1=1.5, color=RED_LINE, dashed=True)
        incident = axes.plot(lambda x: 1.0 * np.sin(6 * x), x_range=[0, 4], color=BLUE_LINE)
        reflected = axes.plot(lambda x: 0.8 * np.sin(-6 * x), x_range=[0, 4], color=YELLOW)
        self.play(Create(boundary), Create(incident), Create(reflected))
        ultra = Text("f = v/λ; strong echo at tissue boundary", font_size=23, color=BLUE_LINE).to_edge(DOWN, buff=1.15).shift(LEFT * 0.4)
        self.play(FadeIn(ultra))
        self.wait(0.6)

        self.play(FadeOut(VGroup(axes, labels, boundary, incident, reflected, ultra)))
        axes2, labels2 = standard_axes([0, 5, 1], [0, 6, 1], x_length=5.4, y_length=3.6, x_label="x / mm", y_label="I")
        axes2.shift(DOWN * 0.35)
        self.play(Create(axes2), FadeIn(labels2))
        mu = 1.0
        attenuation = axes2.plot(lambda x: xray_attenuation(5.0, mu, x), x_range=[0, 5], color=RED_LINE)
        self.play(Create(attenuation))
        xray = Text("X-rays: I = I₀ e^(−μx)", font_size=25, color=RED_LINE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(xray))
        self.wait(1.0)
