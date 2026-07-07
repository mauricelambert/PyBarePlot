#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    SVG chart generator CLI and Python module for creating visual charts
#    with support for styling, legends, gradients, and layout
#    customization.
#    Copyright (C) 2026  PyBarePlot

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
SVG chart generator CLI and Python module for creating visual charts
with support for styling, legends, gradients, and layout
customization.
"""

__version__ = "0.0.4"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
SVG chart generator CLI and Python module for creating visual charts
with support for styling, legends, gradients, and layout
customization.
"""
__url__ = "https://github.com/mauricelambert/PyBarePlot"

__all__ = [
    "load_graphs",
    "StackedBar",
    "GroupedBar",
    "escape_svg",
    "DataPoint",
    "BarLayout",
    "get_color",
    "SVGChart",
    "DataBox",
    "THEMES",
    "Graph",
    "Point",
    "Tick",
    "Zone",
    "Bar",
]

__license__ = "GPL-3.0 License"
__copyright__ = """
PyBarePlot  Copyright (C) 2026  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from typing import (
    Tuple,
    List,
    Dict,
    Union,
    Optional,
    NamedTuple,
    Callable,
    Any,
)
from math import pi, cos, sin, floor, log10, radians
from datetime import datetime, date

# from collections import namedtuple
from collections import defaultdict
from statistics import median
from random import randrange
from sys import exit, stderr
from json import load, loads
from pathlib import Path
from csv import reader
from enum import Enum

try:
    from webbrowser import open as svgopen
except ImportError:
    OPEN = False
else:
    OPEN = True

Number = Union[int, float]
# Point = namedtuple('Point', ['position_x', 'position_y', 'data'])
# Tick = namedtuple("Tick", ["position", "label"])
# Bar = namedtuple(
#     "Bar", ["position_x", "position_y", "width", "height", "data"]
# )
# GroupedBar = namedtuple(
#     "GroupedBar",
#     ["position_x", "position_y", "width", "height", "data", "group_index"],
# )
# StackedBar = namedtuple(
#     "StackedBar",
#     ["position_x", "position_y", "width", "height", "data", "graph"],
# )
# BarLayout = namedtuple("BarLayout", ["group_width", "bar_width", "offset"])


class AxisMode(Enum):
    LINEAR = "linear"
    CATEGORY = "category"


class DataPoint:
    """
    Single data point representation.
    """

    points: List["DataPoint"] = []

    def __init__(
        self,
        value: Number,
        name: Optional[Union[str, int, datetime, date]] = None,
        color: Optional[str] = None,
    ):
        """
        Initialize a data point.

        Parameters
        ----------
        value : int or float
            Numeric value.
        name : str, int or datetime, date, optional
            Data label.
        color : str, optional
            Color value.
        """

        self.value = value
        self.name = name
        self.color = color or get_color(len(DataPoint.points))
        DataPoint.points.append(self)

    def __repr__(self) -> str:
        """
        Return a string representation.
        """

        return (
            f"{self.__class__.__name__}("
            + ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
            + ")"
        )


class DataBox(DataPoint):
    """
    Boxplot statistical data container.
    """

    def __init__(
        self,
        median_value: Number,
        first_quartile: Number,
        third_quartile: Number,
        minimum: Number,
        maximum: Number,
        name: Optional[Union[str, int, datetime, date]] = None,
        color: Optional[str] = None,
    ):
        """
        Initialize boxplot statistics.
        """

        super().__init__(median_value, name, color)
        self.median = median_value
        self.first_quartile = first_quartile
        self.third_quartile = third_quartile
        self.minimum = minimum
        self.maximum = maximum


class Graph:
    """
    Graph data container.
    """

    graphs: List["Graph"] = []

    def __init__(
        self,
        data: Optional[List[Union[DataPoint, Number]]] = None,
        default_color: Optional[str] = "#3498db",
        show_points: Optional[bool] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize graph data.
        """

        self.default_color = default_color or get_color(len(Graph.graphs))
        self.data: List[DataPoint] = []
        self.show_points = show_points
        self.name = name

        Graph.graphs.append(self)
        if data:
            self.build_data(data)

    def build_data(
        self,
        data: List[Union[DataPoint, Number]],
    ) -> None:
        """
        Normalize raw values into DataPoint instances.
        """

        self.data = []
        for d in data:
            if isinstance(d, DataPoint):
                self.data.append(d)
            else:
                self.data.append(
                    DataPoint(
                        value=d,
                        color=self.default_color,
                    )
                )

    def apply_color_gradient(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        start_color: str = "#00ff00",
        end_color: str = "#ff0000",
    ) -> None:
        """
        Apply a linear color gradient to data points.
        """

        values = [d.value for d in self.data]
        if min_value is None:
            min_value = min(values)
        if max_value is None:
            max_value = max(values)

        def hex_to_rgb(hex_color: str):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return "#{:02x}{:02x}{:02x}".format(*rgb)

        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)

        for d in self.data:
            ratio = (
                (d.value - min_value) / (max_value - min_value)
                if max_value != min_value
                else 0
            )
            new_rgb = tuple(
                int(s + (e - s) * ratio) for s, e in zip(start_rgb, end_rgb)
            )
            d.color = rgb_to_hex(new_rgb)

    def apply_color_steps(
        self,
        steps: List[tuple],
    ) -> None:
        """
        Apply stepped color ranges.
        """

        for d in self.data:
            applied = False
            for min_val, max_val, color in steps:
                if min_val <= d.value <= max_val:
                    d.color = color
                    applied = True
                    break
            if not applied:
                d.color = self.default_color

    def __repr__(self) -> str:
        """
        Return a string representation.
        """

        return f"Graph({self.data})"


class Point(NamedTuple):
    """
    SVG coordinates of a graph point.
    """

    position_x: float
    position_y: float
    data: DataPoint


class Tick(NamedTuple):
    """
    Position and label of an axis tick.
    """

    position: int
    label: Union[str, Number]


class Bar(NamedTuple):
    """
    SVG rectangle representing a bar.
    """

    position_x: float
    position_y: float
    width: int
    height: int
    data: DataPoint


class GroupedBar(NamedTuple):
    """
    SVG rectangle for a grouped bar.
    """

    position_x: Number
    position_y: Number
    width: Number
    height: Number
    data: DataPoint
    group_index: int


class StackedBar(NamedTuple):
    """
    SVG rectangle for a stacked bar.
    """

    position_x: Number
    position_y: Number
    width: Number
    height: Number
    data: DataPoint
    graph: Graph


class BarLayout(NamedTuple):
    """
    Common layout information for bar charts.
    """

    group_width: Number
    bar_width: Number
    offset: int


class Zone(NamedTuple):
    """
    SVG zone in charts.
    """

    position_low: Number
    position_hight: Number
    color: str
    opacity: float


LIGHT_THEME = {
    "background": "white",
    "axis": "black",
    "text": "black",
    "grid": "lightgray",
    "box": "black",
}

DARK_THEME = {
    "background": "#121212",
    "axis": "#e0e0e0",
    "text": "#e0e0e0",
    "grid": "#444444",
    "box": "#e0e0e0",
}

TRANSPARENT_THEME = {
    "background": None,
    "axis": "black",
    "text": "black",
    "grid": "lightgray",
    "box": "black",
}

THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "transparent": TRANSPARENT_THEME,
}


class SVGChart:
    """
    SVG chart renderer.
    """

    colors = [
        "red",
        "blue",
        "green",
        "orange",
        "purple",
        "yellow",
        "magenta",
        "cyan",
        "pink",
        "lime",
        "brown",
        "black",
        "lavenderblush",
        "dimgrey",
        "lightpink",
        "dimgray",
        "hotpink",
        "white",
        "darkmagenta",
        "whitesmoke",
        "indigo",
        "gainsboro",
        "deeppink",
        "lightgray",
        "fuchsia",
        "lightgrey",
        "darkviolet",
        "silver",
        "crimson",
        "darkgray",
        "navy",
        "darkgrey",
        "darkblue",
        "gray",
        "ghostwhite",
        "grey",
        "aliceblue",
        "darkslategray",
        "snow",
        "darkslategrey",
        "mistyrose",
        "slategrey",
        "seashell",
        "slategray",
        "floralwhite",
        "lightslategray",
        "maroon",
        "thistle",
        "darkred",
        "plum",
        "olive",
        "lightslategrey",
        "papayawhip",
        "darkslateblue",
        "ivory",
        "cadetblue",
        "blanchedalmond",
        "palevioletred",
        "rosybrown",
        "mediumvioletred",
        "linen",
        "midnightblue",
        "cornsilk",
        "darkolivegreen",
        "azure",
        "sienna",
        "violet",
        "firebrick",
        "orchid",
        "tomato",
        "mediumorchid",
        "peachpuff",
        "darkorchid",
        "bisque",
        "steelblue",
        "lightyellow",
        "darkseagreen",
        "darkgreen",
        "lavender",
        "saddlebrown",
        "lightcyan",
        "darkkhaki",
        "mediumblue",
        "tan",
        "teal",
        "beige",
        "darkcyan",
        "oldlace",
        "blueviolet",
        "indianred",
        "dodgerblue",
        "burlywood",
        "darkturquoise",
        "lightsteelblue",
        "orangered",
        "mediumpurple",
        "lightsalmon",
        "slateblue",
        "coral",
        "lightblue",
        "darkorange",
        "powderblue",
        "darkgoldenrod",
        "mintcream",
        "seagreen",
        "honeydew",
        "olivedrab",
        "lemonchiffon",
        "mediumseagreen",
        "moccasin",
        "forestgreen",
        "navajowhite",
        "lightseagreen",
        "antiquewhite",
        "deepskyblue",
        "lightcoral",
        "mediumslateblue",
        "salmon",
        "royalblue",
        "darksalmon",
        "aqua",
        "peru",
        "lightskyblue",
        "chocolate",
        "cornflowerblue",
        "sandybrown",
        "mediumaquamarine",
        "gold",
        "paleturquoise",
        "lawngreen",
        "mediumturquoise",
        "lightgoldenrodyellow",
        "mediumspringgreen",
        "palegoldenrod",
        "springgreen",
        "wheat",
        "turquoise",
        "khaki",
        "skyblue",
        "goldenrod",
        "aquamarine",
        "yellowgreen",
        "palegreen",
        "limegreen",
        "greenyellow",
        "lightgreen",
        "chartreuse",
    ]

    def __init__(
        self,
        width: int = 600,
        height: int = 400,
        margin: int = 40,
        margin_left: Optional[int] = None,
        margin_right: Optional[int] = None,
        margin_top: Optional[int] = None,
        margin_bottom: Optional[int] = None,
        theme: str = "light",
    ):
        """
        Initialize SVG chart canvas.
        """

        self.is_bar = False
        self.width = width
        self.height = height
        self.margin = margin
        self.margin_left = margin_left if margin_left is not None else margin
        self.margin_right = (
            margin_right if margin_right is not None else margin
        )
        self.margin_top = margin_top if margin_top is not None else margin
        self.margin_bottom = (
            margin_bottom if margin_bottom is not None else margin
        )
        self.defs: List[str] = []
        self.elements: List[str] = []

        try:
            self.theme = THEMES[theme]
        except KeyError:
            raise ValueError(f"Unknown theme: {theme!r} ({', '.join(THEMES)})")

        self.x_zones: List[Zone] = []
        self.y_zones: List[Zone] = []

    def _scale_x(self, i: int, n: int) -> float:
        """
        Scale x coordinate for line plots.
        """

        return self.margin_left + i * (
            self.width - self.margin_left - self.margin_right
        ) / max(1, n - 1)

    def _scale_x_value(self, value: float, xmin: float, xmax: float) -> float:
        """
        Scale x coordinate for horizontal plots.
        """

        plot_width = self.width - self.margin_left - self.margin_right
        return self.margin_left + (value - xmin) * plot_width / max(1e-9, (xmax - xmin))

    def _scale_y(
        self,
        v: Number,
        vmin: Number,
        vmax: Number,
    ) -> float:
        """
        Scale y coordinate.
        """

        return (
            self.height
            - self.margin_bottom
            - (v - vmin)
            / (vmax - vmin)
            * (self.height - self.margin_top - self.margin_bottom)
        )

    def _scale_x_bar(self, i: int, n: int) -> float:
        """
        Scale x coordinate for vertical bars.
        """

        return (
            self.margin_left
            + (i + 0.5)
            * (self.width - self.margin_left - self.margin_right)
            / n
        )

    def _scale_y_bar(self, i: int, n: int) -> float:
        """
        Scale y coordinate for horizontal bars.
        """

        return (
            self.margin_top
            + (i + 0.5)
            * (self.height - self.margin_top - self.margin_bottom)
            / n
        )

    def _nice_ticks(
        self,
        vmin: Number,
        vmax: Number,
        n: int = 5,
    ) -> List[Number]:
        """
        Generate rounded tick values.
        """

        span = vmax - vmin
        step = span / n
        mag = 10 ** floor(log10(step))
        step = round(step / mag) * mag
        return [vmin + i * step for i in range(n + 1)]

    def _count_categories(self, graphs: List[Graph]) -> int:
        """
        Return the number of x categories safely.
        Always based on actual data length.
        """

        return max((len(g.data) for g in graphs), default=0)

    def _compute_stacked_xmax(self, graphs: List[Graph]) -> Number:
        """
        Compute xmax for stacked charts (sum per index).
        """

        return max(
            sum(graph.data[i].value for graph in graphs)
            for i in range(len(graphs[0].data))
        )

    def _compute_legend_position(
        self,
        x: Optional[Number] = None,
        y: Optional[Number] = None,
    ) -> Tuple[Number, Number]:
        """
        Compute legend position.
        """

        x = x or (self.width - self.margin_right - 90)
        y = y or self.margin_top
        return x, y

    def format_tick_value(
        self, value: Union[Number, date, datetime], is_timestamp: bool = False
    ) -> str:
        """
        Format a tick value for display.
        """

        if is_timestamp:
            value = date.fromtimestamp(value)

        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, str):
            return value
        return str(round(value, 1))

    def compute_limits(
        self,
        graphs: List[Graph],
        ymin: Optional[Number] = None,
        ymax: Optional[Number] = None,
        xmax: Optional[Union[int, date, datetime]] = None,
    ) -> Tuple[Number, Number, int]:
        """
        Compute graph boundaries.
        """

        if ymin is None:
            ymin = min(
                min(g.data, key=lambda d: d.value).value for g in graphs
            )

        if ymax is None:
            ymax = max(
                max(g.data, key=lambda d: d.value).value for g in graphs
            )

        if xmax is None:
            xmax = max(len(g.data) for g in graphs)

        return ymin, ymax, xmax

    def compute_x_ticks(
        self,
        xmin: Union[Number, date, datetime],
        xmax: Union[Number, date, datetime],
        xticks: Union[int, List[Union[Number, date, datetime]]],
        bar: bool = False,
    ) -> List[Tuple[float, str]]:
        """
        Compute X tick positions and labels.
        """

        ml = self.margin_left
        mr = self.margin_right
        width = self.width - ml - mr
        is_datetime = isinstance(xticks, list) and all(
            isinstance(x, (datetime, date)) for x in xticks
        )

        ticks = []

        def num_value(value: Union[Number, date, datetime]) -> Number:
            if isinstance(value, (datetime, date)):
                nonlocal is_datetime
                is_datetime = True
                return value.timestamp()
            return value

        if isinstance(xticks, int):
            xmin_num = num_value(xmin)
            xmax_num = num_value(xmax)

            for i in range(xticks + 1):
                x = ml + i * width / xticks
                value = xmin_num + (i * (xmax_num - xmin_num) / xticks)
                ticks.append(
                    Tick(x, self.format_tick_value(value, is_datetime))
                )

        else:
            n = len(xticks)
            for i, value in enumerate(xticks):
                if bar:
                    x = ml + (i + 0.5) * width / n
                else:
                    x = ml + i * width / max(1, n - 1)
                ticks.append(Tick(x, self.format_tick_value(value)))

        return ticks

    def compute_y_ticks(
        self,
        ymin: Number,
        ymax: Number,
        yticks: Union[int, List],
        hbar: bool = False,
    ) -> List[Tuple[float, str]]:
        """
        Compute Y tick positions and labels.
        """

        mt = self.margin_top
        mb = self.margin_bottom
        height = self.height - mt - mb

        ticks = []

        if isinstance(yticks, int):
            for i in range(yticks + 1):
                y = self.height - mb - i * height / yticks
                value = ymin + i * (ymax - ymin) / yticks
                ticks.append(Tick(y, f"{value:.1f}"))

        else:
            n = len(yticks)
            cell_height = height / n
            for i, value in enumerate(yticks):
                if hbar:
                    y = mt + i * cell_height + cell_height / 2
                else:
                    y = self.height - mb - i * height / max(1, n - 1)
                ticks.append(Tick(y, str(value)))

        return ticks

    def compute_svg_points(
        self, graph: Graph, ymin: Number, ymax: Number, xmax: int
    ) -> List[Point]:
        """
        Compute SVG coordinates for a graph.
        """

        points: List[Point] = []

        for i, d in enumerate(graph.data):
            x = self._scale_x(i, xmax)
            y = self._scale_y(d.value, ymin, ymax)
            points.append(Point(x, y, d))

        return points

    def compute_segments(
        self, graph: Graph, ymin: Number, ymax: Number, xmax: int
    ) -> List[Tuple[Point, Point]]:
        """
        Compute graph line segments.
        """

        points = self.compute_svg_points(graph, ymin, ymax, xmax)
        return list(zip(points[:-1], points[1:]))

    def compute_bar_layout(
        self,
        xmax: int,
        bars_per_group: int = 1,
        bar_width_ratio: float = 0.8,
    ) -> BarLayout:
        """
        Compute common bar layout information.
        """

        plot_width = self.width - self.margin_left - self.margin_right
        group_width = plot_width / max(
            1, xmax if isinstance(xmax, int) else xmax
        )
        bar_width = group_width * bar_width_ratio / max(1, bars_per_group)
        offset = (group_width - bar_width * bars_per_group) / 2
        return BarLayout(group_width, bar_width, offset)

    def compute_horizontal_bar_layout(
        self,
        graph_count: int,
        category_count: int,
        plot_size: Number,
    ) -> BarLayout:
        """
        Compute common bar layout.
        """

        group_width = plot_size / category_count
        bar_width = group_width / graph_count
        offset = (group_width - graph_count * bar_width) / 2
        return BarLayout(group_width, bar_width, offset)

    def compute_bars(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        bar_width_ratio: float = 0.8,
    ) -> List[Bar]:
        """
        Compute SVG rectangles for a bar chart.
        """

        layout = self.compute_bar_layout(xmax, bar_width_ratio=bar_width_ratio)
        baseline = self._scale_y(0, ymin, ymax)
        bars: List[Bar] = []

        for i, data in enumerate(graph.data):
            x = self._scale_x(i, xmax) - layout.bar_width / 2
            y = self._scale_y(data.value, ymin, ymax)

            bars.append(
                Bar(
                    x,
                    min(y, baseline),
                    layout.bar_width,
                    abs(baseline - y),
                    data,
                )
            )

        return bars

    def compute_horizontal_bars(
        self,
        graph: Graph,
        xmin: Number,
        xmax: Number,
        ymax: int,
        height: Number,
    ) -> List[Bar]:
        """
        Compute horizontal bars.
        """

        bars = []
        plot_height = self.height - self.margin_top - self.margin_bottom

        for i, d in enumerate(graph.data):
            y = (
                self.margin_top
                + i * plot_height / ymax
                + (plot_height / ymax - height) / 2
            )

            x0 = self._scale_x_value(xmin, xmin, xmax)
            x1 = self._scale_x_value(d.value, xmin, xmax)
            width = x1 - x0
            bars.append(Bar(x0, y, width, height, d))

        return bars



    def compute_grouped_bars(
        self,
        graphs: List[Graph],
        ymin: Number,
        ymax: Number,
        xmax: int,
        bar_width_ratio: float = 0.8,
    ) -> List[GroupedBar]:
        """
        Compute grouped bar layout for multiple graphs.
        """

        layout = self.compute_bar_layout(
            xmax, bars_per_group=len(graphs), bar_width_ratio=bar_width_ratio
        )
        baseline = self._scale_y(0, ymin, ymax)

        bars: List[GroupedBar] = []

        for gi, graph in enumerate(graphs):
            for i, d in enumerate(graph.data):
                x_center = self.margin_left + (i + 0.5) * layout.group_width
                x = (
                    x_center
                    - layout.group_width / 2
                    + layout.offset
                    + gi * layout.bar_width
                )

                y = self._scale_y(d.value, ymin, ymax)

                bars.append(
                    GroupedBar(
                        x,
                        min(y, baseline),
                        layout.bar_width,
                        abs(baseline - y),
                        d,
                        gi,
                    )
                )

        return bars

    def compute_stacked_bars(
        self,
        graphs: List[Graph],
        ymin: Number,
        ymax: Number,
        xmax: int,
        bar_width_ratio: float = 0.8,
    ) -> List[StackedBar]:
        """
        Compute stacked bar layout.
        """

        layout = self.compute_bar_layout(xmax, bar_width_ratio=bar_width_ratio)
        bars: List[StackedBar] = []

        for i in range(xmax):
            positive = 0
            negative = 0

            for graph in graphs:
                if i >= len(graph.data):
                    continue

                d = graph.data[i]

                if d.value >= 0:
                    bottom = positive
                    top = positive + d.value
                    positive = top
                else:
                    top = negative
                    bottom = negative + d.value
                    negative = bottom

                y1 = self._scale_y(top, ymin, ymax)
                y2 = self._scale_y(bottom, ymin, ymax)

                bars.append(
                    StackedBar(
                        self.margin_left + (i + 0.5) * layout.group_width,
                        min(y1, y2),
                        layout.bar_width,
                        abs(y2 - y1),
                        d,
                        graph,
                    )
                )

        return bars

    def compute_horizontal_grouped_bars(
        self,
        graphs: List[Graph],
        xmin: Number,
        xmax: Number,
        ymax: int,
    ) -> List[GroupedBar]:
        """
        Compute grouped horizontal bars.
        """

        bars = []

        plot_height = self.height - self.margin_top - self.margin_bottom
        layout = self.compute_horizontal_bar_layout(
            len(graphs), ymax, plot_height
        )

        for group_index, graph in enumerate(graphs):
            for index, data in enumerate(graph.data):
                y = (
                    self.margin_top
                    + index * layout.group_width
                    + group_index * layout.bar_width
                )

                width = (
                    self._scale_x_value(data.value, xmin, xmax)
                    - self.margin_left
                )

                bars.append(
                    GroupedBar(
                        self.margin_left,
                        y,
                        width,
                        layout.bar_width,
                        data,
                        group_index,
                    )
                )

        return bars

    def compute_horizontal_stacked_bars(
        self,
        graphs: List[Graph],
        xmin: Number,
        xmax: Number,
        ymax: int,
    ) -> List[StackedBar]:
        """
        Compute stacked horizontal bars.
        """

        bars = []

        plot_height = self.height - self.margin_top - self.margin_bottom
        bar_height = plot_height / ymax

        offsets = [xmin] * ymax

        for graph in graphs:
            for index, data in enumerate(graph.data):
                x1 = self._scale_x_value(offsets[index], xmin, xmax)
                x2 = self._scale_x_value(offsets[index] + data.value, xmin, xmax)

                y = self.margin_top + index * bar_height

                bars.append(
                    StackedBar(x1, y, x2 - x1, bar_height, data, graph)
                )

                offsets[index] += data.value

        return bars

    def compute_polyline(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
    ) -> str:
        """
        Compute SVG polyline points.
        """

        return " ".join(
            f"{p.position_x},{p.position_y}"
            for p in self.compute_svg_points(graph, ymin, ymax, xmax)
        )

    def compute_step_paths(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
    ) -> List[Tuple[str, str]]:
        """
        Compute SVG paths grouped by contiguous colors.
        Returns: [(path_d, color)]
        """

        paths: List[Tuple[str, str]] = []

        current_color = None
        commands: List[str] = []

        for start, end in self.compute_segments(graph, ymin, ymax, xmax):
            color = start.data.color or graph.default_color

            if color != current_color:
                if commands:
                    paths.append((" ".join(commands), current_color))

                commands = [f"M {start.position_x} {start.position_y}"]
                current_color = color

            commands.append(f"L {end.position_x} {end.position_y}")

        if commands:
            paths.append((" ".join(commands), current_color))

        return paths

    def compute_grouped_step_paths(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
    ) -> Dict[str, str]:
        """
        Compute SVG paths grouped by color.
        """

        paths: Dict[str, List[str]] = defaultdict(list)

        for start, end in self.compute_segments(graph, ymin, ymax, xmax):
            color = start.data.color or graph.default_color
            paths[color].append(self.segment_to_path(start, end))

        return {color: " ".join(commands) for color, commands in paths.items()}

    def compute_boxplot(self, graphs: List[Graph]) -> List[DataBox]:
        """
        Compute boxplot statistics from graphs.
        """

        boxes: List[DataBox] = []

        for g in graphs:
            if not g.data:
                continue

            values = sorted(d.value for d in g.data)

            mn = values[0]
            mx = values[-1]
            med = median(values)
            mid = len(values) // 2
            q1 = median(values[:mid])
            q3 = median(values[mid + (len(values) % 2) :])

            boxes.append(DataBox(med, q1, q3, mn, mx, color=g.default_color))

        return boxes

    def _compute_pie_geometry(
        self,
        radius: Optional[Number],
        center: Optional[tuple],
    ) -> tuple:
        """
        Compute pie chart geometry.
        """

        radius = (
            radius
            or min(
                self.width - self.margin_left - self.margin_right,
                self.height - self.margin_top - self.margin_bottom,
            )
            / 2
        )

        cx, cy = center or (
            self.margin_left
            + (self.width - self.margin_left - self.margin_right) / 2,
            self.margin_top
            + (self.height - self.margin_top - self.margin_bottom) / 2,
        )

        return radius, cx, cy

    def compute_pie_slices(
        self, graph: Graph
    ) -> List[Tuple[DataPoint, float, float]]:
        """
        Compute pie slices (start_angle, end_angle).
        """

        total = sum(d.value for d in graph.data)

        angle = 0
        slices = []

        for data in graph.data:
            start = angle
            angle += 360 * data.value / total
            slices.append((data, start, angle))

        return slices

    def compute_radar(self, graphs: List[Graph]) -> tuple:
        """
        Compute radar chart geometry.
        """

        n = max(len(g.data) for g in graphs)
        rmax = max(max(d.value for d in g.data) for g in graphs)
        cx = (
            self.margin_left
            + (self.width - self.margin_left - self.margin_right) / 2
        )
        cy = (
            self.margin_top
            + (self.height - self.margin_top - self.margin_bottom) / 2
        )
        radius = (
            min(
                self.width - self.margin_left - self.margin_right,
                self.height - self.margin_top - self.margin_bottom,
            )
            / 2
        )
        angles = [2 * pi * i / n for i in range(n)]
        return rmax, cx, cy, radius, angles

    def compute_radar_points(
        self,
        graph: Graph,
        radius: Number,
        rmax: Number,
        cx: Number,
        cy: Number,
        angles: List[float],
    ) -> str:
        """
        Compute radar polygon points.
        """

        points = []
        for angle, data in zip(angles, graph.data):
            r = radius * data.value / rmax
            x = cx + r * sin(angle)
            y = cy - r * cos(angle)
            points.append(f"{x},{y}")
        return " ".join(points)

    def compute_radar_ring(
        self, cx: Number, cy: Number, radius: Number, angles: List[float]
    ) -> str:
        """
        Compute radar ring polygon.
        """

        points = []
        for angle in angles:
            x = cx + radius * sin(angle)
            y = cy - radius * cos(angle)
            points.append(f"{x},{y}")
        return " ".join(points)

    def compute_radar_labels(
        self,
        graph: Graph,
        cx: Number,
        cy: Number,
        radius: Number,
        angles: List[float],
        offset: Number = 15,
    ) -> List[Tuple[Number, Number, str]]:
        """
        Compute radar labels.
        """

        labels = []
        for angle, data in zip(angles, graph.data):
            x = cx + (radius + offset) * sin(angle)
            y = cy - (radius + offset) * cos(angle)
            labels.append((x, y, str(data.name or "")))
        return labels

    def prepare_plot(
        self,
        graphs: List[Graph],
        ymin: Optional[Number] = None,
        ymax: Optional[Number] = None,
        xmin: Union[int, date, datetime] = 0,
        xmax: Optional[Union[int, date, datetime]] = None,
        draw_axes: bool = True,
        bar: bool = False,
    ) -> Tuple[Number, Number, int]:
        """
        Prepare a line chart before drawing.
        """

        ymin, ymax, xmax = self.compute_limits(graphs, ymin, ymax, xmax)

        if bar:
            ymin = min(0, ymin)

        if draw_axes:
            xticks = 5
            if self.verify_graphs_names(graphs):
                xticks = [x.name for x in graphs[0].data]
            self.axes(xmin, xmax - 1, ymin, ymax, xticks, bar=bar)

        return ymin, ymax, xmax

    def prepare_horizontal_plot(
        self,
        graphs: List[Graph],
        xmin: Optional[Number] = None,
        xmax: Optional[Number] = None,
        ymin: Number = 0,
        ymax: Optional[int] = None,
    ) -> Tuple[Number, Number, int]:
        """
        Prepare axes and bounds for horizontal bar charts.
        """

        if xmin is None:
            xmin = min(min(
                min(graph.data, key=lambda d: d.value).value
                for graph in graphs
            ), 0)

        if xmax is None:
            xmax = max(
                max(graph.data, key=lambda d: d.value).value
                for graph in graphs
            )

        if ymax is None:
            ymax = max(len(graph.data) for graph in graphs)

        yticks = ymax
        if self.verify_graphs_names(graphs):
            yticks = [x.name for x in graphs[0].data]
        self.axes(xmin, xmax, ymin, ymax, yticks=yticks, bar=False, hbar=True)

        return xmin, xmax, ymax

    def segment_to_path(self, start: Point, end: Point) -> str:
        """
        Convert a segment to an SVG path command.
        """

        return (
            f"M {start.position_x} {start.position_y} "
            f"L {end.position_x} {end.position_y}"
        )

    @staticmethod
    def verify_graphs_names(graphs: List[Graph]) -> Union[bool, List[str]]:
        """
        Checks that all graphs have the same names.

        Returns:
            False: If the graphs do not contain the same names.
            False: If any name is not defined (None).
            List[str]: The list of names if all graphs match.
        """

        if not graphs:
            return False

        base = [x.name for x in graphs[0].data]
        if any(x is None for x in base):
            return False

        return (
            base
            if all(base == [x.name for x in y.data] for y in graphs[1:])
            else False
        )

    def draw_line(
        self,
        x1: Number,
        y1: Number,
        x2: Number,
        y2: Number,
        stroke: str,
        width: int = 2,
        dasharray: Optional[Tuple[int, int]] = None,
        opacity: float = 1,
        stroke_opacity: Optional[Number] = None,
    ) -> None:
        """
        Draw a SVG line.
        """

        attributes = [
            f'x1="{x1}"',
            f'y1="{y1}"',
            f'x2="{x2}"',
            f'y2="{y2}"',
            f'stroke="{stroke}"',
            f'stroke-width="{width}"',
            f'opacity="{opacity}"',
        ]

        if dasharray is not None:
            dash = ",".join(str(v) for v in dasharray)
            attributes.append(f'stroke-dasharray="{dash}"')

        if stroke_opacity:
            attributes.append(f'stroke-opacity="{stroke_opacity}"')

        self.elements.append(f"<line {' '.join(attributes)}/>")

    def draw_path(
        self,
        path: str,
        stroke: str,
        width: int = 2,
        fill: Optional[str] = None,
        opacity: float = 1,
        fill_opacity: Optional[Number] = None,
        stroke_opacity: Optional[Number] = None,
    ) -> None:
        """
        Draw a SVG path.
        """

        if stroke == "none" and stroke_opacity and fill:
            stroke = fill

        self.elements.append(
            (
                f'<path d="{path}" '
                f'fill="{fill or (stroke if fill_opacity else "none")}" '
                f'stroke="{stroke}" '
                f'stroke-width="{width}" '
                + (f'fill-opacity="{fill_opacity}" ' if fill_opacity else "")
                + (
                    f'stroke-opacity="{stroke_opacity}" '
                    if stroke_opacity
                    else ""
                )
                + f'opacity="{opacity}"/>'
            )
        )

    def draw_circle(
        self,
        x: Number,
        y: Number,
        radius: Number,
        color: str,
        stroke: Optional[str] = None,
        stroke_width: int = 1,
        opacity: int = 1,
        fill_opacity: Optional[Number] = None,
        stroke_opacity: Optional[Number] = None,
    ) -> None:
        """
        Draw a SVG circle.
        """

        if stroke_opacity:
            stroke = stroke or color

        if color == "none" and fill_opacity and stroke:
            color = stroke

        self.elements.append(
            (
                f'<circle cx="{x}" '
                f'cy="{y}" '
                f'r="{radius}" '
                + (
                    f'stroke="{stroke}" stroke-width="{stroke_width}" '
                    if stroke
                    else ""
                )
                + (f'fill-opacity="{fill_opacity}" ' if fill_opacity else "")
                + (
                    f'stroke-opacity="{stroke_opacity}" '
                    if stroke_opacity
                    else ""
                )
                + f'fill="{color}" opacity="{opacity}"/>'
            )
        )

    def draw_rect(
        self,
        x: Number,
        y: Number,
        width: Number,
        height: Number,
        fill: str,
        stroke: Optional[str] = None,
        stroke_width: int = 1,
        opacity: float = 1,
        fill_opacity: Optional[Number] = None,
        stroke_opacity: Optional[Number] = None,
    ) -> None:
        """
        Draw a SVG rectangle.
        """

        if fill == "none" and fill_opacity and stroke:
            fill = stroke

        attributes = [
            f'x="{x}"',
            f'y="{y}"',
            f'width="{width}"',
            f'height="{height}"',
            f'fill="{fill}"',
            f'opacity="{opacity}"',
        ]

        if fill_opacity:
            attributes.append(f'fill-opacity="{fill_opacity}"')

        if stroke_opacity:
            stroke = stroke or fill
            attributes.append(f'stroke-opacity="{stroke_opacity}"')

        if stroke is not None:
            attributes.append(f'stroke="{stroke}"')
            attributes.append(f'stroke-width="{stroke_width}"')

        self.elements.append(f"<rect {' '.join(attributes)}/>")

    def draw_text(
        self,
        x: Number,
        y: Number,
        text: str,
        color: str,
        font_size: int = 12,
        anchor: str = "middle",
        opacity: float = 1,
    ) -> None:
        """
        Draw a SVG text.
        """

        self.elements.append(
            (
                f'<text fill="{color}" '
                f'x="{x}" '
                f'y="{y}" '
                f'text-anchor="{anchor}" '
                f'font-size="{font_size}" opacity="{opacity}">'
                f"{escape_svg(text)}</text>"
            )
        )

    def draw_polyline(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        fill: str = "none",
        width: int = 2,
        opacity: float = 1,
        stroke_opacity: Optional[Number] = None,
    ) -> None:
        """
        Draw a polyline for a graph.
        """

        points = [
            f"{x},{y}"
            for x, y, _ in self.compute_svg_points(graph, ymin, ymax, xmax)
        ]

        self.elements.append(
            (
                f'<polyline fill="{fill}" '
                f'stroke="{graph.default_color}" '
                f'stroke-width="{width}" opacity="{opacity}" '
                + (
                    f'stroke-opacity="{stroke_opacity}" '
                    if stroke_opacity
                    else ""
                )
                + f'points="{" ".join(points)}"/>'
            )
        )

    def draw_polygon(
        self,
        points: str,
        stroke: str,
        fill: Optional[str] = None,
        stroke_width: int = 1,
        opacity: float = 1,
        dasharray: Optional[Tuple[Number, Number]] = None,
        fill_opacity: Optional[Number] = None,
        stroke_opacity: Optional[Number] = None,
    ) -> None:
        """
        Draw a SVG polygon.
        """

        if fill_opacity:
            fill = fill or stroke

        if stroke == "none" and stroke_opacity and fill:
            stroke = fill

        self.elements.append(
            (
                f'<polygon points="{points}" '
                f'fill="{fill}" '
                f'stroke="{stroke}" '
                f'stroke-width="{stroke_width}" '
                + (
                    f'stroke-dasharray="{",".join(str(v) for v in dasharray)}" '
                    if dasharray
                    else ""
                )
                + (f'fill-opacity="{fill_opacity}" ' if fill_opacity else "")
                + (
                    f'stroke-opacity="{stroke_opacity}" '
                    if stroke_opacity
                    else ""
                )
                + f' opacity="{opacity}"/>'
            )
        )

    def draw_points(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        *args,
        radius: int = 3,
        **kwargs,
    ) -> None:
        """
        Draw graph points.
        """

        for x, y, d in self.compute_svg_points(graph, ymin, ymax, xmax):
            self.draw_circle(
                x, y, radius, d.color or graph.default_color, *args, **kwargs
            )

    def draw_bar(self, bar: Bar, color: str, *args, **kwargs) -> None:
        """
        Draw a single bar.
        """

        self.draw_rect(
            bar.position_x,
            bar.position_y,
            bar.width,
            bar.height,
            color,
            *args,
            **kwargs,
        )

    def draw_bars(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        width: Number,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw graph bars.
        """

        for bar in self.compute_bars(graph, ymin, ymax, xmax, width):
            self.draw_bar(
                bar, bar.data.color or graph.default_color, *args, **kwargs
            )

    def draw_horizontal_bars(
        self,
        graph: Graph,
        xmin: Number,
        xmax: Number,
        ymax: int,
        height: Number,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw horizontal graph bars.
        """

        for bar in self.compute_horizontal_bars(
            graph, xmin, xmax, ymax, height
        ):
            self.draw_bar(
                bar, bar.data.color or graph.default_color, *args, **kwargs
            )

    def draw_segment(
        self,
        start: Point,
        end: Point,
        stroke: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a line segment.
        """

        self.draw_line(
            start.position_x,
            start.position_y,
            end.position_x,
            end.position_y,
            stroke,
            *args,
            **kwargs,
        )

    def draw_gradient_segment(
        self,
        start: Point,
        end: Point,
        start_color: str,
        end_color: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a gradient line segment.
        """

        gid = f"seg_grad_{len(self.defs)}"

        self.defs.append(
            (
                f'<linearGradient id="{gid}" '
                f'gradientUnits="userSpaceOnUse" '
                f'x1="{start.position_x}" '
                f'y1="{start.position_y}" '
                f'x2="{end.position_x}" '
                f'y2="{end.position_y}">'
                f'<stop offset="0%" stop-color="{start_color}"/>'
                f'<stop offset="100%" stop-color="{end_color}"/>'
                f"</linearGradient>"
            )
        )

        self.draw_segment(
            start,
            end,
            f"url(#{gid})",
            *args,
            **kwargs,
        )

    def draw_graph(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        line_renderer: Optional[Callable] = None,
        point_renderer: Optional[Callable] = None,
        args_line: List[Any] = [],
        kwargs_line: Dict[str, Any] = {},
        args_point: List[Any] = [],
        kwargs_point: Dict[str, Any] = {},
    ) -> None:
        """
        Draw a graph with its line and optional points.
        """

        if line_renderer is None:
            line_renderer = self.draw_polyline

        if point_renderer is None:
            point_renderer = self.draw_points

        line_renderer(graph, ymin, ymax, xmax, *args_line, **kwargs_line)

        if graph.show_points:
            point_renderer(
                graph,
                ymin,
                ymax,
                xmax,
                *args_point,
                **kwargs_point,
            )

    def draw_x_axis(self) -> None:
        """
        Draw the horizontal axis.
        """

        self.draw_line(
            self.margin_left,
            self.height - self.margin_bottom,
            self.width - self.margin_right,
            self.height - self.margin_bottom,
            self.theme["axis"],
            width=1,
        )

    def draw_y_axis(self) -> None:
        """
        Draw the vertical axis.
        """

        self.draw_line(
            self.margin_left,
            self.margin_top,
            self.margin_left,
            self.height - self.margin_bottom,
            self.theme["axis"],
            width=1,
        )

    def draw_x_zones(self, xmin: Number, xmax: Number) -> None:
        """
        Draw vertical background bands.
        """

        plot_width = self.width - self.margin_left - self.margin_right

        for x_min, x_max, color, opacity in self.x_zones:
            x1 = self.margin_left + (x_min - xmin) * plot_width / (xmax - xmin)
            x2 = self.margin_left + (x_max - xmin) * plot_width / (xmax - xmin)
            self.draw_rect(
                x1,
                self.margin_top,
                x2 - x1,
                self.height - self.margin_top - self.margin_bottom,
                color,
                opacity=opacity,
            )

    def draw_y_zones(self, ymin: Number, ymax: Number) -> None:
        """
        Draw horizontal background zones.
        """

        plot_height = self.height - self.margin_top - self.margin_bottom

        for y_min, y_max, color, opacity in self.y_zones:
            top = self.margin_top + (
                (ymax - y_max) * plot_height / (ymax - ymin)
            )
            bottom = self.margin_top + (
                (ymax - y_min) * plot_height / (ymax - ymin)
            )

            self.draw_rect(
                self.margin_left,
                top,
                self.width - self.margin_left - self.margin_right,
                bottom - top,
                color,
                opacity=opacity,
            )

    def draw_x_tick(self, x: Number) -> None:
        """
        Draw a tick on the X axis.
        """

        self.draw_line(
            x,
            self.height - self.margin_bottom,
            x,
            self.height - self.margin_bottom + 5,
            self.theme["axis"],
            width=1,
        )

    def draw_x_label(self, x: Number, label: str, *args, **kwargs) -> None:
        """
        Draw X axis label.
        """

        self.draw_text(
            x,
            self.height - self.margin_bottom + 20,
            label,
            self.theme["text"],
            *args,
            **kwargs,
        )

    def draw_x_grid_line(
        self,
        x: Number,
        dasharray: Tuple[int, int] = (4, 4),
    ) -> None:
        """
        Draw a vertical grid line.
        """

        self.draw_line(
            x,
            self.margin_top,
            x,
            self.height - self.margin_bottom,
            self.theme["grid"],
            width=1,
            dasharray=dasharray,
        )

    def draw_y_tick(self, y: Number) -> None:
        """
        Draw a tick on the Y axis.
        """

        self.draw_line(
            self.margin_left - 5,
            y,
            self.margin_left,
            y,
            self.theme["axis"],
            width=1,
        )

    def draw_y_label(self, y: Number, label: str, *args, **kwargs) -> None:
        """
        Draw Y axis label.
        """

        self.draw_text(
            self.margin_left - 10,
            y + 4,
            label,
            self.theme["text"],
            *args,
            **kwargs,
        )

    def draw_y_grid_line(
        self,
        y: Number,
        dasharray: Tuple[int, int] = (4, 4),
    ) -> None:
        """
        Draw a horizontal grid line.
        """

        self.draw_line(
            self.margin_left,
            y,
            self.width - self.margin_right,
            y,
            self.theme["grid"],
            width=1,
            dasharray=dasharray,
        )

    def draw_gradient_line(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a gradient line.
        """

        for start, end in self.compute_segments(graph, ymin, ymax, xmax):
            self.draw_gradient_segment(
                start,
                end,
                start.data.color or graph.default_color,
                end.data.color or graph.default_color,
                *args,
                **kwargs,
            )

    def draw_step_line(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a line split whenever the point color changes.
        """

        for path, color in self.compute_step_paths(graph, ymin, ymax, xmax):
            self.draw_path(path, color, *args, **kwargs)

    def draw_step_line_grouped(
        self,
        graph: Graph,
        ymin: Number,
        ymax: Number,
        xmax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw grouped line segments sharing the same color.
        """

        for color, path in self.compute_grouped_step_paths(
            graph, ymin, ymax, xmax
        ).items():
            self.draw_path(path, color, *args, **kwargs)

    def draw_grouped_bars(
        self,
        graphs: List[Graph],
        ymin: Number,
        ymax: Number,
        xmax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw grouped bar charts.
        """

        for bar in self.compute_grouped_bars(graphs, ymin, ymax, xmax):
            self.draw_rect(
                bar.position_x,
                bar.position_y,
                bar.width,
                bar.height,
                bar.data.color or graphs[bar.group_index].default_color,
                *args,
                **kwargs,
            )

    def draw_stacked_bars(
        self,
        graphs: List[Graph],
        ymin: Number,
        ymax: Number,
        xmax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw stacked bars.
        """

        for bar in self.compute_stacked_bars(graphs, ymin, ymax, xmax):
            self.draw_rect(
                bar.position_x,
                bar.position_y,
                bar.width,
                bar.height,
                bar.data.color or bar.graph.default_color,
                *args,
                **kwargs,
            )

    def draw_horizontal_grouped_bars(
        self,
        graphs: List[Graph],
        xmin: Number,
        xmax: Number,
        ymax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw grouped horizontal bars.
        """

        for bar in self.compute_horizontal_grouped_bars(
            graphs,
            xmin,
            xmax,
            ymax,
        ):
            self.draw_bar(
                bar,
                bar.data.color or graphs[bar.group_index].default_color,
                *args,
                **kwargs,
            )

    def draw_horizontal_stacked_bars(
        self,
        graphs: List[Graph],
        xmin: Number,
        xmax: Number,
        ymax: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw stacked horizontal bars.
        """

        for bar in self.compute_horizontal_stacked_bars(
            graphs,
            xmin,
            xmax,
            ymax,
        ):
            self.draw_bar(
                bar,
                bar.data.color or bar.graph.default_color,
                *args,
                **kwargs,
            )

    def _draw_single_box(
        self,
        box: DataBox,
        i: int,
        n: int,
        box_width: float,
        ymin: Number,
        ymax: Number,
        fill: str = "none",
        **kwargs,
    ) -> None:
        """
        Draw a single boxplot element.
        """

        plot_width = self.width - self.margin_left - self.margin_right
        x = self.margin_left + (i + 0.5) * plot_width / n

        y_q1 = self._scale_y(box.first_quartile, ymin, ymax)
        y_q3 = self._scale_y(box.third_quartile, ymin, ymax)
        y_med = self._scale_y(box.median, ymin, ymax)
        y_min = self._scale_y(box.minimum, ymin, ymax)
        y_max = self._scale_y(box.maximum, ymin, ymax)
        middle_x = x - box_width / 2

        color = box.color

        self.draw_rect(
            middle_x, y_q3, box_width, y_q1 - y_q3, fill, color, 1, **kwargs
        )
        self.draw_line(middle_x, y_med, x + box_width / 2, y_med, color, 1)
        self.draw_line(x, y_q3, x, y_max, color, 1)
        self.draw_line(x, y_q1, x, y_min, color, 1)

    def draw_boxplot(self, boxes: List[DataBox], *args, **kwargs) -> None:
        """
        Draw boxplot from precomputed statistics.
        """

        if not boxes:
            return

        ymin = min(b.minimum for b in boxes)
        ymax = max(b.maximum for b in boxes)
        n = len(boxes)
        self.axes(xmin=0, xmax=n, ymin=ymin, ymax=ymax, bar=True)

        plot_width = self.width - self.margin_left - self.margin_right
        box_width = (plot_width / n) * 0.6

        for i, b in enumerate(boxes):
            self._draw_single_box(
                b, i, n, box_width, ymin, ymax, *args, **kwargs
            )

    def _draw_pie_slice(
        self,
        data: DataPoint,
        start_angle: float,
        end_angle: float,
        cx: float,
        cy: float,
        radius: float,
        fill: str,
        stroke: str = "none",
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a single pie slice.
        """

        self.draw_path(
            (
                f"M {cx} {cy} "
                f"L {cx + radius * cos(radians(start_angle))} "
                f"{cy + radius * sin(radians(start_angle))} "
                f"A {radius} {radius} 0 "
                f'{"1" if end_angle - start_angle > 180 else "0"} 1 '
                f"{cx + radius * cos(radians(end_angle))} "
                f"{cy + radius * sin(radians(end_angle))} "
                "Z"
            ),
            stroke,
            *args,
            fill=fill,
            **kwargs,
        )

    def draw_pie(
        self,
        graph: Graph,
        radius: Optional[Number] = None,
        center: Optional[tuple] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw pie chart.
        """

        radius, cx, cy = self._compute_pie_geometry(radius, center)
        for data, start, end in self.compute_pie_slices(graph):
            self._draw_pie_slice(
                data, start, end, cx, cy, radius, data.color, *args, **kwargs
            )

    def _draw_radar_graph(
        self,
        graph: Graph,
        rmax: Number,
        cx: float,
        cy: float,
        radius: float,
        angles: List[float],
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a single radar graph.
        """

        points = self.compute_radar_points(graph, radius, rmax, cx, cy, angles)
        self.draw_polygon(points, graph.default_color, *args, **kwargs)

    def draw_radar(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Draw radar chart.
        """

        rmax, cx, cy, radius, angles = self.compute_radar(graphs)
        self.draw_radar_grid(cx, cy, radius, angles)

        if self.verify_graphs_names(graphs):
            self.draw_radar_labels(graphs[0], cx, cy, radius, angles)

        for g in graphs:
            self._draw_radar_graph(
                g, rmax, cx, cy, radius, angles, *args, **kwargs
            )

    def draw_radar_grid(
        self,
        cx: Number,
        cy: Number,
        radius: Number,
        angles: List[float],
        rings: int = 5,
    ) -> None:
        """
        Draw radar grid.
        """

        for angle in angles:
            self.draw_line(
                cx,
                cy,
                cx + radius * sin(angle),
                cy - radius * cos(angle),
                self.theme["grid"],
                width=1,
                dasharray=(4, 4),
            )

        for i in range(1, rings + 1):
            points = self.compute_radar_ring(
                cx, cy, radius * i / rings, angles
            )
            self.draw_polygon(points, self.theme["grid"], dasharray=(4, 4))

    def _draw_legend_item(
        self,
        data: Union[DataPoint, Graph],
        index: int,
        x: Number,
        y: Number,
        box_size: int = 15,
        spacing: int = 5,
        font_size: int = 12,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw a single legend item.
        """

        if not data.name:
            return None

        y_pos = y + index * (box_size + spacing)

        color = (
            getattr(data, "color", None)
            or getattr(data, "default_color", None)
            or "grey"
        )
        text_color = self.theme["text"]

        self.draw_rect(
            x, y_pos, box_size, box_size, *args, fill=color, **kwargs
        )

        self.draw_text(
            x + box_size + 5,
            y_pos + box_size - 3,
            str(data.name),
            text_color,
            font_size,
            "start",
        )

    def draw_legend(
        self,
        graphs: List[Graph],
        x: Optional[Number] = None,
        y: Optional[Number] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw graph legend.
        """

        x, y = self._compute_legend_position(x, y)
        for i, d in enumerate(graphs):
            self._draw_legend_item(d, i, x, y, *args, **kwargs)

    def draw_pie_legend(
        self,
        graph: Graph,
        x: Optional[Number] = None,
        y: Optional[Number] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Draw legend for pie chart.
        """

        x, y = self._compute_legend_position(x, y)
        for i, d in enumerate(graph.data):
            self._draw_legend_item(d, i, x, y, *args, **kwargs)

    def draw_radar_labels(
        self,
        graph: Graph,
        cx: Number,
        cy: Number,
        radius: Number,
        angles: List[float],
        offset: Number = 15,
        **kwargs,
    ) -> None:
        """
        Draw radar labels.
        """

        for x, y, label in self.compute_radar_labels(
            graph,
            cx,
            cy,
            radius,
            angles,
            offset,
        ):
            self.draw_text(x, y, label, self.theme["text"], **kwargs)

    def add_x_zone(
        self, xmin: Number, xmax: Number, color: str, opacity: float = 0.2
    ) -> None:
        """
        Add a vertical background zone.
        """

        self.x_zones.append(Zone(xmin, xmax, color, opacity))

    def add_y_zone(
        self, ymin: Number, ymax: Number, color: str, opacity: float = 0.2
    ) -> None:
        """
        Add an horizontal background zone.
        """

        self.y_zones.append(Zone(ymin, ymax, color, opacity))

    def axes(
        self,
        xmin: Union[Number, date, datetime],
        xmax: Union[Number, date, datetime],
        ymin: Number,
        ymax: Number,
        xticks: Union[int, List[Union[int, date, datetime]]] = 5,
        yticks: int = 5,
        bar: bool = False,
        hbar: bool = False,
    ) -> None:
        """
        Draw chart axes and grid.
        """

        self.draw_y_zones(ymin, ymax)
        self.draw_x_zones(xmin, xmax)
        self.draw_x_axis()
        self.draw_y_axis()

        for x, label in self.compute_x_ticks(xmin, xmax, xticks, bar=bar):
            self.draw_x_tick(x)
            self.draw_x_label(x, label)

            if hbar:
                self.draw_x_grid_line(x)

        for y, label in self.compute_y_ticks(ymin, ymax, yticks, hbar=hbar):
            self.draw_y_tick(y)
            self.draw_y_label(y, label)

            if not hbar:
                self.draw_y_grid_line(y)

    def _plot_graphs(
        self,
        graphs: List[Graph],
        ymin: Optional[Number] = None,
        ymax: Optional[Number] = None,
        xmin: Number = 0,
        xmax: Optional[int] = None,
        line_renderer: Optional[Callable] = None,
        point_renderer: Optional[Callable] = None,
        kwargs_line: Dict[str, Any] = {},
        kwargs_point: Dict[str, Any] = {},
    ) -> None:
        """
        Prepare axes and draw graphs.
        """

        ymin, ymax, xmax = self.prepare_plot(graphs, ymin, ymax, xmin, xmax)

        for graph in graphs:
            self.draw_graph(
                graph,
                ymin,
                ymax,
                xmax,
                line_renderer=line_renderer,
                point_renderer=point_renderer,
                kwargs_line=kwargs_line,
                kwargs_point=kwargs_point,
            )

    def plot_line(self, graph: Graph, *args, **kwargs) -> None:
        """
        Plot line chart.
        """

        self.plot_lines([graph], *args, **kwargs)

    def plot_lines(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Plot line charts.
        """

        self._plot_graphs(graphs, *args, **kwargs)

    def plot_gradient_lines(
        self, graphs: List[Graph], *args, **kwargs
    ) -> None:
        """
        Plot lines with color gradients.
        """

        self._plot_graphs(
            graphs, *args, line_renderer=self.draw_gradient_line, **kwargs
        )

    def plot_step_lines(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Plot step lines with color changes.
        """

        self._plot_graphs(
            graphs, *args, line_renderer=self.draw_step_line, **kwargs
        )

    def plot_step_lines_optimized(self, graphs, *args, **kwargs) -> None:
        """
        Plot optimized step lines grouped by color.
        """

        self._plot_graphs(
            graphs, *args, line_renderer=self.draw_step_line_grouped, **kwargs
        )

    def plot_grouped_bars(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Plot grouped bar charts.
        """

        self._plot_bars_common(graphs, 0.8, "grouped", *args, **kwargs)

    def plot_stacked_bars(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Plot stacked bar charts.
        """

        self._plot_bars_common(graphs, 0.8, "stacked", *args, **kwargs)

    def _plot_bars_common(
        self,
        graphs: List[Graph],
        bar_width_ratio: float,
        mode: str,
        ymin: Optional[Number] = None,
        ymax: Optional[Number] = None,
        xmin: Number = 0,
        xmax: Optional[int] = None,
        **kwargs,
    ) -> None:
        """
        Common bar plotting logic for all bar modes.
        """

        if mode == "stacked" and ymax is None:
            ymax = self._compute_stacked_xmax(graphs)

        ymin, ymax, _ = self.prepare_plot(
            graphs, ymin, ymax, xmin, xmax, bar=True
        )
        n = self._count_categories(graphs)
        if n == 0:
            return

        if mode == "simple":
            plot_width = self.width - self.margin_left - self.margin_right
            bar_width = (plot_width / n) * bar_width_ratio

            for graph in graphs:
                for i, d in enumerate(graph.data):
                    x = self.margin_left + i * (plot_width / n)
                    y = self._scale_y(d.value, ymin, ymax)
                    h = self.height - self.margin_bottom - y
                    self.draw_bar(
                        Bar(x, y, bar_width, h, d),
                        d.color or graph.default_color,
                        **kwargs,
                    )
            return

        if mode == "grouped":
            self.draw_grouped_bars(graphs, ymin, ymax, n, **kwargs)
            return

        if mode == "stacked":
            if xmax is None:
                xmax = self._compute_stacked_xmax(graphs)
            self.draw_stacked_bars(graphs, ymin, ymax, n, **kwargs)
            return

    def plot_bars(
        self, graphs: List[Graph], bar_width_ratio: float = 0.6, **kwargs
    ) -> None:
        """
        Plot bar charts.
        """

        self._plot_bars_common(graphs, bar_width_ratio, "simple", **kwargs)

    def _plot_horizontal_bars_common(
        self,
        graphs: List[Graph],
        bar_height_ratio: float,
        mode: str,
        xmin: Optional[Number] = None,
        xmax: Optional[Number] = None,
        ymin: Number = 0,
        ymax: Optional[int] = None,
    ) -> None:
        """
        Common horizontal bar plotting logic.

        mode:
            - "simple"
            - "grouped"
            - "stacked"
        """

        if mode == "stacked" and xmax is None:
            xmax = self._compute_stacked_xmax(graphs)

        xmin, xmax, ymax = self.prepare_horizontal_plot(
            graphs, xmin, xmax, ymin, ymax
        )

        if mode == "simple":
            plot_height = self.height - self.margin_top - self.margin_bottom
            bar_height = plot_height / ymax * bar_height_ratio
            for graph in graphs:
                self.draw_horizontal_bars(graph, xmin, xmax, ymax, bar_height)
            return

        if mode == "grouped":
            self.draw_horizontal_grouped_bars(graphs, xmin, xmax, ymax)
            return

        if mode == "stacked":
            self.draw_horizontal_stacked_bars(graphs, xmin, xmax, ymax)
            return

    def plot_horizontal_bars(
        self, graphs: List[Graph], bar_height_ratio: float = 0.6, **kwargs
    ) -> None:
        """
        Plot horizontal bar charts.
        """

        self._plot_horizontal_bars_common(
            graphs, bar_height_ratio, "simple", **kwargs
        )

    def plot_horizontal_grouped_bars(
        self, graphs: List[Graph], *args, **kwargs
    ) -> None:
        """
        Plot grouped horizontal bar charts.
        """

        self._plot_horizontal_bars_common(
            graphs, 0.8, "grouped", *args, **kwargs
        )

    def plot_horizontal_stacked_bars(
        self,
        graphs: List[Graph],
        *args,
        **kwargs,
    ) -> None:
        """
        Plot stacked horizontal bar charts.
        """

        self._plot_horizontal_bars_common(
            graphs, 0.8, "stacked", *args, **kwargs
        )

    def plot_boxplots(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Plot boxplots.
        """

        boxes = self.compute_boxplot(graphs)
        self.draw_boxplot(boxes, *args, **kwargs)

    def plot_pie(self, graph: Graph, *args, **kwargs) -> None:
        """
        Plot pie chart.
        """

        self.draw_pie(graph, *args, **kwargs)

    def plot_radar(self, graphs: List[Graph], *args, **kwargs) -> None:
        """
        Plot radar chart.
        """

        self.draw_radar(graphs, *args, **kwargs)

    def render(self) -> str:
        """
        Return the full SVG string.
        """

        defs = ""
        if self.defs:
            defs = "<defs>\n" + "\n".join(self.defs) + "\n</defs>\n"

        background = ""
        if self.theme["background"] is not None:
            background = (
                f'<rect width="{self.width}" '
                f'height="{self.height}" '
                f'fill="{self.theme["background"]}"/>\n'
            )

        content = "\n".join(self.elements)

        return (
            f'<svg width="{self.width}" '
            f'height="{self.height}" '
            f'xmlns="http://www.w3.org/2000/svg">\n'
            f"{defs}{background}{content}\n"
            f"</svg>"
        )

    def save(self, filename: str) -> None:
        """
        Save the rendered SVG to a file.
        """

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.render())


_PLOTTERS = {
    "lines": SVGChart.plot_lines,
    "bars": SVGChart.plot_bars,
    "grouped-bars": SVGChart.plot_grouped_bars,
    "stacked-bars": SVGChart.plot_stacked_bars,
    "horizontal-bars": SVGChart.plot_horizontal_bars,
    "horizontal-grouped-bars": SVGChart.plot_horizontal_grouped_bars,
    "horizontal-stacked-bars": SVGChart.plot_horizontal_stacked_bars,
    "pie": SVGChart.plot_pie,
    "boxplot": SVGChart.plot_boxplots,
    "radar": SVGChart.plot_radar,
    "gradient-line": SVGChart.plot_gradient_lines,
    "step-line": SVGChart.plot_step_lines,
    "step-line-optimized": SVGChart.plot_step_lines_optimized,
}

_PLOT_ALIASES = {
    "bar": "bars",
    "line": "lines",
    "hbar": "horizontal-bars",
    "horizontal": "horizontal-bars",
    "stack": "stacked-bars",
    "group": "grouped-bars",
    "box": "boxplot",
    "gradient": "gradient-line",
    "step": "step-line",
}

_PLOT_SINGLE_GRAPH = frozenset({"pie"})
_DECORATORS = []


def escape_svg(text: str) -> str:
    """
    Escape a string for safe use in SVG (XML) content.

    Replaces the five XML special characters with their corresponding
    entity references:
      - &  -> &amp;
      - <  -> &lt;
      - >  -> &gt;
      - "  -> &quot;
      - '  -> &apos;

    Args:
        text (str): The input string to escape.

    Returns:
        str: The escaped string, safe for use in SVG/XML text or attribute
        values.
    """

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _load_csv(
    path: str,
    graph_name: Optional[str] = None,
    graph_color: Optional[str] = None,
) -> Graph:
    """
    Load a Graph from a CSV file.

    Expected format:
        value,color,name
        10,red,A
        20,blue,B

    Returns:
        Graph
    """

    points = []
    with open(path, newline="", encoding="utf-8") as f:
        csvreader = reader(f)

        for row in csvreader:
            if not row:
                continue

            value = float(row[0])
            color = row[1] if len(row) > 1 and row[1] else None
            name = row[2] if len(row) > 2 and row[2] else None

            points.append(DataPoint(value, color=color, name=name))

    return Graph(points, name=graph_name, default_color=graph_color)


def _load_json_object(
    data: Dict[str, Any],
    graph_name: Optional[str] = None,
    graph_color: Optional[str] = None,
) -> Graph:
    """
    Internal helper for JSON/MJSON parsing.
    """

    points = [
        DataPoint(
            p["value"],
            color=p.get("color"),
            name=p.get("name"),
        )
        for p in data.get("points", [])
    ]

    return Graph(
        points,
        default_color=graph_color or data.get("default_color"),
        name=graph_name or data.get("name"),
    )


def _load_json(
    path: str,
    graph_name: Optional[str] = None,
    graph_color: Optional[str] = None,
) -> "Graph":
    """
    Load a Graph from a JSON file.

    Format:
    {
        "name": "graph",
        "default_color": "red",
        "points": [
            {"value": 10, "color": "red", "name": "A"}
        ]
    }
    """

    with open(path, encoding="utf-8") as f:
        data = load(f)

    return _load_json_object(data, graph_name, graph_color)


def _load_mjson(
    path: str,
    graph_name: Optional[str] = None,
    graph_color: Optional[str] = None,
) -> Graph:
    """
    Load raw points from a MJSON file.

    Format (stream of objects, NOT graph):
        {"value": 10, "color": "red", "name": "A"}
        {"value": 20, "color": "blue", "name": "B"}
    """

    with open(path, encoding="utf-8") as file:
        return _load_json_object(
            {"points": [loads(obj) for obj in file]}, graph_name, graph_color
        )


def load_graphs(args: Namespace) -> Graph:
    """
    Merge all input sources into a single list of Graphs.

    Order priority:
        1. CSV
        2. JSON
        3. MJSON
        4. CLI values
    """

    graphs: list[Graph] = []

    for source in args.csv:
        path, name, color = _parse_graph_source(source)
        graphs.append(_load_csv(path, name, color))

    for source in args.json:
        path, name, color = _parse_graph_source(source)
        graphs.append(_load_json(path, name, color))

    for source in args.mjson:
        path, name, color = _parse_graph_source(source)
        graphs.append(_load_mjson(path, name, color))

    for i, values in enumerate(args.values):
        colors = args.colors[i] if i < len(args.colors) else None
        names = args.labels[i] if i < len(args.labels) else (args.point_labels or None)
        graph_name = args.graph_name[i] if i < len(args.graph_name) else None
        graph_color = (
            args.graph_color[i] if i < len(args.graph_color) else None
        )

        points = []
        for j, v in enumerate(values):
            points.append(
                DataPoint(
                    v,
                    color=colors[j] if colors and j < len(colors) else None,
                    name=names[j] if names and j < len(names) else None,
                )
            )
        graphs.append(
            Graph(points, name=graph_name, default_color=graph_color)
        )

    return graphs


def _parse_graph_source(
    source: str,
) -> tuple[str, str | None, str | None]:
    r"""
    Parse a graph source specification.

    The expected format is::

        PATH
        PATH:GRAPH_NAME
        PATH:GRAPH_NAME:GRAPH_COLOR

    The separator is parsed from the right so that ':' characters may safely
    appear in the path (for example on Windows).

    Args:
        source:
            Graph source specification.

    Returns:
        tuple[str, str | None, str | None]:
            A tuple containing:

            - file path
            - graph name
            - graph default color

    Examples:
        >>> _parse_graph_source("graph.csv")
        ('graph.csv', None, None)

        >>> _parse_graph_source("graph.csv;Sales")
        ('graph.csv', 'Sales', None)

        >>> _parse_graph_source("graph.csv;Sales;red")
        ('graph.csv', 'Sales', 'red')

        >>> _parse_graph_source("C:\\tmp\\graph.csv")
        ('C:\\tmp\\graph.csv', None, None)

        >>> _parse_graph_source("C:\\tmp\\graph.csv;Sales")
        ('C:\\tmp\\graph.csv', 'Sales', None)

        >>> _parse_graph_source("C:\\tmp\\graph.csv;Sales;red")
        ('C:\\tmp\\graph.csv', 'Sales', 'red')
    """

    path_spec, separator, color = source.rpartition(";")
    if not separator:
        return source, None, None

    path, separator, name = path_spec.rpartition(";")
    if not separator:
        return path_spec, color, None

    return path, name or None, color or None


def _plot_chart(chart: SVGChart, plot_type: str, graphs: list[Graph]) -> None:
    """
    Plot graphs using the requested chart type.

    Args:
        chart:
            Destination SVG chart.
        plot_type:
            Chart type or alias.
        graphs:
            Graphs to plot.
    """

    plot_type = _PLOT_ALIASES.get(plot_type, plot_type)
    plotter = _PLOTTERS[plot_type]

    if plot_type in _PLOT_SINGLE_GRAPH:
        if len(graphs) != 1:
            raise ValueError("pie charts require exactly one graph")
        plotter(chart, graphs[0])
    else:
        plotter(chart, graphs)


def _apply_background_decorations(
    chart: SVGChart, args: Namespace, graphs: List[Graph]
) -> None:
    """
    Apply all visual background decorations to the chart.
    """

    for start, end, color in args.x_zone:
        chart.add_x_zone(float(start), float(end), color)

    for start, end, color in args.y_zone:
        chart.add_y_zone(float(start), float(end), color)

    if args.gradient:
        values = args.gradient
        if len(values) not in (2, 4):
            raise ValueError("Invalid gradient format")

        start_color, end_color = values[0], values[1]
        min_v = float(values[2]) if len(values) == 4 else None
        max_v = float(values[3]) if len(values) == 4 else None

        for g in graphs:
            g.apply_color_gradient(
                min_value=min_v,
                max_value=max_v,
                start_color=start_color,
                end_color=end_color,
            )

    for step in args.color_step:
        min_v, max_v, color = step
        for g in graphs:
            g.apply_color_steps([(float(min_v), float(max_v), color)])

    if args.show_points:
        for graph in graphs:
            graph.show_points = True


def _apply_legend(
    chart: SVGChart, args: Namespace, graphs: List[Graph]
) -> None:
    """
    Apply legend to the chart.
    """

    if args.legend:
        plot_type = _PLOT_ALIASES.get(args.type.lower(), args.type.lower())
        default_colors = {x.default_color for x in graphs}
        colors = {x.color for x in graphs[0].data}
        if plot_type in _PLOT_SINGLE_GRAPH or (len(default_colors) == 1 and len(colors) > 1):
            chart.draw_pie_legend(graphs[0])
        else:
            chart.draw_legend(graphs)


def _validate_args(args: Namespace, graphs: List[Graph]) -> None:
    """
    Validate command-line arguments.

    Args:
        args:
            Parsed command-line arguments.
        graphs:
            Loaded graphs.

    Raises:
        ValueError:
            If the command-line arguments are inconsistent.
    """

    plot_type = _PLOT_ALIASES.get(args.type.lower(), args.type.lower())

    if not graphs:
        raise ValueError("at least one graph is required")

    if plot_type in _PLOT_SINGLE_GRAPH and len(graphs) != 1:
        raise ValueError(f"{plot_type!r} requires exactly one graph")

    if args.graph_name and len(args.graph_name) > len(graphs):
        raise ValueError("too many graph names")

    if args.graph_color and len(args.graph_color) > len(graphs):
        raise ValueError("too many graph colors")

    if len(args.colors) > len(args.values):
        raise ValueError("too many point color groups")

    if len(args.labels) > len(args.values):
        raise ValueError("too many point label groups")

    _validate_values(args)


def _validate_values(args: Namespace) -> None:
    """
    Validate numeric command-line values.

    Args:
        args:
            Parsed command-line arguments.

    Raises:
        ValueError:
            If a numeric value is invalid.
    """

    def check_float(value: str, argument: str) -> None:
        try:
            float(value)
        except ValueError as exc:
            raise ValueError(
                f"{argument}: {value!r} is not a valid floating-point value."
            ) from exc

    for start, end, _ in args.x_zone:
        check_float(start, "--x-zone")
        check_float(end, "--x-zone")

    for start, end, _ in args.y_zone:
        check_float(start, "--y-zone")
        check_float(end, "--y-zone")

    for minimum, maximum, _ in args.color_step:
        check_float(minimum, "--color-step")
        check_float(maximum, "--color-step")

    if args.gradient:
        if len(args.gradient) not in (2, 4):
            raise ValueError(
                "--gradient expects either 2 values "
                "(START END) or 4 values (START END MIN MAX)."
            )

        if len(args.gradient) == 4:
            check_float(args.gradient[2], "--gradient")
            check_float(args.gradient[3], "--gradient")


def get_color(index: int) -> str:
    """
    Return a strategic different color for each call.
    """

    return SVGChart.colors[index % len(SVGChart.colors)]


def parse_args() -> Namespace:
    """
    Parse command-line arguments.

    Returns:
        Namespace:
            Parsed command-line arguments.

    Notes:
        Graph data may come from one or more sources:

        - ``--values`` for direct command-line values.
        - ``--csv`` for CSV files.
        - ``--json`` for JSON graph files.
        - ``--mjson`` for multi-graph JSON files.

        All graph sources are merged together preserving their order.
    """

    parser = ArgumentParser(
        description="Generate SVG charts from the command line.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    input_group = parser.add_argument_group("Input")
    input_group.add_argument(
        "-v",
        "--values",
        action="append",
        nargs="+",
        type=float,
        metavar="VALUE",
        default=[],
        help=(
            "Graph values. Repeat the option to create multiple graphs.\n"
            "Example: --values 1 2 3 --values 4 5 6"
        ),
    )
    input_group.add_argument(
        "--csv",
        action="append",
        metavar="FILE",
        default=[],
        help=(
            "Load one graph from a CSV file. "
            "Repeat the option to load multiple CSV files."
            "Format: FILE[;GRAPH_NAME[;GRAPH_COLOR]]"
        ),
    )
    input_group.add_argument(
        "--json",
        action="append",
        metavar="FILE",
        default=[],
        help=(
            "Load one graph from a JSON file. "
            "Repeat the option to load multiple JSON files."
            "Format: FILE[;GRAPH_NAME[;GRAPH_COLOR]]"
        ),
    )
    input_group.add_argument(
        "--mjson",
        action="append",
        metavar="FILE",
        default=[],
        help=(
            "Load one or more graphs from a Multi-JSON file. "
            "Repeat the option to load multiple files."
            "Format: FILE[;GRAPH_NAME[;GRAPH_COLOR]]"
        ),
    )

    chart_group = parser.add_argument_group("Chart")
    chart_group.add_argument(
        "-t",
        "--type",
        default="line",
        choices=tuple(_PLOTTERS) + tuple(_PLOT_ALIASES),
        help="Chart type.",
    )
    # chart_group.add_argument(
    #     "--title",
    #     metavar="TEXT",
    #     help="Chart title.",
    # )
    chart_group.add_argument(
        "--theme",
        choices=tuple(THEMES),
        default="light",
        help="Chart theme.",
    )
    chart_group.add_argument(
        "-W",
        "--width",
        type=int,
        default=800,
        help="SVG width.",
    )
    chart_group.add_argument(
        "-H",
        "--height",
        type=int,
        default=400,
        help="SVG height.",
    )
    chart_group.add_argument(
        "--margin-top",
        type=int,
        default=20,
        help="Top margin.",
    )
    chart_group.add_argument(
        "--margin-bottom",
        type=int,
        default=30,
        help="Bottom margin.",
    )
    chart_group.add_argument(
        "--margin-left",
        type=int,
        default=40,
        help="Left margin.",
    )
    chart_group.add_argument(
        "--margin-right",
        type=int,
        default=20,
        help="Right margin.",
    )

    label_group = parser.add_argument_group("Labels")
    label_group.add_argument(
        "--graph-name",
        nargs="+",
        action="extend",
        default=[],
        metavar="NAME",
        help="Graph name. Repeat once for each graph.",
    )
    label_group.add_argument(
        "--labels",
        nargs="+",
        action="append",
        default=[],
        metavar="LABEL",
        help="Point labels.",
    )
    label_group.add_argument(
        "--point-labels",
        nargs="+",
        action="extend",
        default=[],
        metavar="LABEL",
        help=(
            "Default labels applied to all graphs "
            "(used when per-graph labels are not provided)."
        ),
    )
    # label_group.add_argument(
    #     "--x-label",
    #     metavar="TEXT",
    #     help="X axis label.",
    # )
    # label_group.add_argument(
    #     "--y-label",
    #     metavar="TEXT",
    #     help="Y axis label.",
    # )

    color_group = parser.add_argument_group("Colors")
    color_group.add_argument(
        "--graph-color",
        action="append",
        default=[],
        metavar="NAME",
        help="Graph color. Repeat once for each graph.",
    )
    color_group.add_argument(
        "-c",
        "--colors",
        action="append",
        nargs="+",
        default=[],
        metavar="COLOR",
        help="Point colors.",
    )
    color_group.add_argument(
        "--gradient",
        nargs="+",
        metavar="VALUE",  # ("START", "END", "MIN", "MAX"),
        help=(
            "Gradient colors.\n"
            "Examples:\n"
            "  --gradient green red\n"
            "  --gradient green red 0 100"
        ),
    )
    color_group.add_argument(
        "--color-step",
        action="append",
        nargs=3,
        metavar=("MIN", "MAX", "COLOR"),
        default=[],
        help="Color step definition.",
    )

    deco_group = parser.add_argument_group("Decorations")
    deco_group.add_argument(
        "--legend",
        action="store_true",
        help="Draw graph legend.",
    )
    deco_group.add_argument(
        "--show-points",
        action="store_true",
        help="Display graph points.",
    )
    deco_group.add_argument(
        "--x-zone",
        action="append",
        nargs=3,
        metavar=("START", "END", "COLOR"),
        default=[],
        help="Highlight an X zone.",
    )
    deco_group.add_argument(
        "--y-zone",
        action="append",
        nargs=3,
        metavar=("START", "END", "COLOR"),
        default=[],
        help="Highlight a Y zone.",
    )

    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "-o",
        "--output",
        required=True,
        metavar="FILE",
        help="Destination SVG file.",
    )
    output_group.add_argument(
        "--open",
        action="store_true",
        dest="open_svg",
        help="Open the generated SVG after saving.",
    )

    return parser.parse_args()


def main() -> int:
    """
    Main function for command-line SVG plotting.
    Builds the plot from CLI arguments and saves it to the output file.

    Example usage:
        python PyBarePlot.py --type bar --output chart.svg --values 10 20 15 --colors red green blue
        python PyBarePlot.py --type pie --output chart.svg --values 30 70 --labels A B
    """

    args = parse_args()
    graphs = load_graphs(args)

    try:
        _validate_args(args, graphs)
    except ValueError as e:
        print("CLI value error:", e, file=stderr)
        return 127

    chart = SVGChart(
        width=args.width,
        height=args.height,
        margin_top=args.margin_top,
        margin_bottom=args.margin_bottom,
        margin_left=args.margin_left,
        margin_right=args.margin_right,
        theme=args.theme,
    )

    _apply_background_decorations(chart, args, graphs)
    _plot_chart(chart, args.type.lower(), graphs)
    _apply_legend(chart, args, graphs)

    output_path = Path(args.output)
    chart.save(output_path)
    print(f"SVG plot saved to {output_path}")

    if OPEN and args.open_svg:
        svgopen(output_path)
    return 0


def test() -> None:
    from datetime import timedelta

    data = [randrange(51) for x in range(0x51)]
    graph1 = Graph(default_color="blue")
    graph1.build_data(data)

    data = [randrange(51) + 50 for x in range(0x51)]
    graph2 = Graph(data, default_color="orange")

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_lines((graph1, graph2))
    chart.save("graph0.svg")

    graph3 = Graph(default_color="blue")
    graph3.build_data(
        [
            DataPoint(randrange(51), date.today() + timedelta(days=i))
            for i in range(10)
        ]
    )
    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="light")
    chart.add_x_zone(0, 2, "orange")
    chart.add_x_zone(5, 8, "cyan")
    chart.add_y_zone(3, 4, "green")
    chart.plot_line(graph3)
    chart.save("graph0.1.svg")

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_bars((graph2, graph1))
    chart.save("graph1.svg")

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_grouped_bars((graph2, graph1))
    chart.save("graph1.1.svg")

    chart = SVGChart(
        1200, 440, margin_top=20, margin_bottom=30, theme="transparent"
    )
    chart.plot_stacked_bars((graph2, graph1))
    chart.save("graph1.2.svg")

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_horizontal_bars((graph2, graph1))
    chart.save("graph2.svg")

    chart = SVGChart(880, 880, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_horizontal_stacked_bars((graph2, graph1))
    chart.save("graph2.1.svg")

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_horizontal_grouped_bars((graph2, graph1))
    chart.save("graph2.2.svg")

    graph = Graph(
        [
            DataPoint(0, "test", "blue"),
            DataPoint(8, "toto", "red"),
            DataPoint(6, "titi", "orange"),
            DataPoint(7, "tata", "purple"),
            DataPoint(3, "tutu", "cyan"),
            DataPoint(5, "tout", "green"),
            DataPoint(7, "ottu", "magenta"),
            DataPoint(1, "uttu", "gray"),
        ]
    )

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_pie(graph, fill_opacity=0.2, stroke_opacity=1)
    chart.draw_pie_legend(graph, fill_opacity=0.2, stroke_opacity=1)
    chart.save("graph4.svg")

    chart = SVGChart(880, 440, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_boxplots((graph, graph1, graph2), fill_opacity=0.2)
    chart.save("graph.svg")

    graph = Graph(
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 6, 4, 2, 6, 0, 8), show_points=True
    )
    steps = [
        (7.2, 8.0, "#ff0000"),
        (5.6, 7.2, "#ff9900"),
        (4.4, 5.6, "#ffff00"),
        (0.0, 4.4, "#00ff00"),
    ]
    graph.apply_color_steps(steps)
    chart = SVGChart(800, 400, margin_top=20, margin_bottom=30, theme="dark")
    graph.apply_color_gradient(
        min_value=0, max_value=8, start_color="#00ff00", end_color="#ff0000"
    )
    chart.plot_gradient_lines([graph])
    chart.save("graph8.svg")

    chart = SVGChart(800, 400, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_step_lines([graph])
    chart.save("graph7.svg")

    chart = SVGChart(800, 400, margin_top=20, margin_bottom=30, theme="dark")
    chart.plot_step_lines_optimized([graph])
    chart.save("graph6.svg")

    g1 = Graph(
        [
            DataPoint(1, name="A"),
            DataPoint(3, name="B"),
            DataPoint(2, name="C"),
            DataPoint(5, name="D"),
            DataPoint(4, name="E"),
        ],
        default_color="red",
        name="Alice",
    )
    g2 = Graph(
        [
            DataPoint(2, name="A"),
            DataPoint(2, name="B"),
            DataPoint(4, name="C"),
            DataPoint(3, name="D"),
            DataPoint(5, name="E"),
        ],
        default_color="blue",
        name="Bob",
    )

    chart = SVGChart(width=400, height=400, theme="dark")
    chart.plot_radar([g1, g2], fill_opacity=0.2)
    chart.draw_legend([g1, g2])
    chart.save("graph5.svg")


if __name__ == "__main__":
    exit(main())
