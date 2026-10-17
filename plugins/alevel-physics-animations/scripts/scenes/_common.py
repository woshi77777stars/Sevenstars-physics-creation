"""Shared visual helpers for the Manim scenes."""

from __future__ import annotations

from manim import *


AXIS_GREY = GREY_B
RED_LINE = "#E4572E"
BLUE_LINE = "#1F6FEB"


def standard_axes(x_range, y_range, x_length=7.0, y_length=4.0, x_label=None, y_label=None):
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config={"color": AXIS_GREY},
        tips=False,
    )
    labels = VGroup()
    if x_label:
        labels.add(axes.get_x_axis_label(Text(x_label, font_size=26)))
    if y_label:
        labels.add(axes.get_y_axis_label(Text(y_label, font_size=26).rotate(PI / 2)))
    return axes, labels


def scene_title(text: str) -> Text:
    return Text(text, font_size=34).to_edge(UP)


def time_dot(axes, tracker, fn, color=YELLOW, radius=0.09):
    return always_redraw(
        lambda: Dot(point=axes.c2p(*fn(tracker.get_value())), radius=radius, color=color)
    )


def vertical_tick(axes, x, y0=0.0, y1=1.0, color=GREY, dashed=True):
    line_class = DashedLine if dashed else Line
    return line_class(axes.c2p(x, y0), axes.c2p(x, y1), color=color, stroke_width=2)


def vector(start, end, color, buff=0.0):
    return Arrow(
        start=start,
        end=end,
        buff=buff,
        color=color,
        max_tip_length_to_length_ratio=0.15,
    )


def point_and_label(axes, xy, text, direction=DOWN, color=WHITE):
    dot = Dot(point=axes.c2p(*xy), radius=0.08, color=color)
    label = Text(text, font_size=22).next_to(dot, direction, buff=0.08)
    return VGroup(dot, label)


def note(text: str, position=DOWN, color=WHITE, font_size=26):
    return Text(text, font_size=font_size, color=color).to_edge(position, buff=0.35)


def zigzag_spring(start, end, coils=9, width=0.28, color=WHITE):
    """A coil spring as a jagged polyline between two points."""

    def build(s, e):
        s = np.array(s)
        e = np.array(e)
        direction = e - s
        length = np.linalg.norm(direction)
        unit = direction / length
        normal = np.array([-unit[1], unit[0], 0.0])
        points = [s]
        segments = 2 * coils + 1
        for i in range(1, segments):
            frac = i / segments
            if i % 2 == 1:
                offset = width / 2
            else:
                offset = -width / 2
            points.append(s + direction * frac + normal * offset)
        points.append(e)
        return VMobject().set_points_as_corners(points).set_color(color)

    return always_redraw(lambda: build(start.get_center(), end.get_center()))
