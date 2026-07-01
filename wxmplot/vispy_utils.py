#!/usr/bin/python
"""
wxmplot ImageCanvas: shared VisPy utilities used by all wxmplot VisPy widgets
"""

import sys

import vispy
from wxutils.colors import get_color
from wxutils.themes import get_theme

__all__ = ["vispy_init", "vispy_colour", "vsync_for_platform"]

_VISPY_INITIALISED = False


def vispy_init() -> None:
    """Initialise VisPy with the wx backend and the appropriate GL backend for the platform."""
    global _VISPY_INITIALISED
    if _VISPY_INITIALISED:
        return
    vispy.use(app="wx", gl="glplus" if sys.platform == "win32" else "gl2")
    _VISPY_INITIALISED = True


def vsync_for_platform() -> bool:
    """Return True on platforms where vsync is safe with the wx GL backend."""
    return sys.platform != "linux"


def vispy_colour(name: str) -> tuple:
    """Return a theme colour as a normalised (r, g, b, a) float tuple for VisPy.

    Plot-specific names (plot_curve, plot_fill, plot_selection) are resolved
    from the active ColorTheme. All other names fall back to get_color().
    """
    if name == "plot_curve":
        c = get_theme().blue
        return (c.Red() / 255, c.Green() / 255, c.Blue() / 255, 1.0)
    if name == "plot_fill":
        c = get_theme().blue
        return (c.Red() / 255, c.Green() / 255, c.Blue() / 255, 30 / 255)
    if name == "plot_selection":
        c = get_theme().selection_bg
        return (c.Red() / 255, c.Green() / 255, c.Blue() / 255, 178 / 255)
    rgba = get_color(name)
    return tuple(c / 255 for c in rgba)

