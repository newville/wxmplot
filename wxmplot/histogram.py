"""
wxmplot Histogram: histogram data computation and a generic histogram widget with 
draggable range handles and an optional colorbar strip.
"""

import math
from typing import Callable

import numpy as np
import wx
from wxutils.colors import get_color, register_darkdetect
from wxutils.themes import get_theme

from wxmplot.colors import lookup_colormap

__all__ = ["compute_histogram_data", "Histogram"]

_DEFAULT_MAX_PIXELS = 500_000


def compute_histogram_data(
    image: np.ndarray,
    max_pixels: int = _DEFAULT_MAX_PIXELS,
    log_scale: bool = True,
) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
    """Returns (bin_centers, log_counts) for a log-log histogram. Samples up to max_pixels pixels from the image before computing the histogram."""
    flat = image.ravel()
    if flat.size > max_pixels:
        flat = flat[:: flat.size // max_pixels]
    flat = flat.astype(np.float64)

    if log_scale:
        positive = flat[flat > 0]
        if positive.size == 0:
            return None, None
        data = np.log1p(positive)
        data = data[np.isfinite(data)]
        if data.size == 0:
            return None, None
        hist, bin_edges = np.histogram(data, bins=1500)
        mask = hist > 0
        if not mask.any():
            return None, None
        return bin_edges[:-1][mask], np.log(hist[mask].astype(np.float64))
    else:
        finite = flat[np.isfinite(flat)]
        if finite.size == 0:
            return None, None
        hist, bin_edges = np.histogram(finite, bins=256)
        mask = hist > 0
        if not mask.any():
            return None, None
        centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        return centers[mask], hist[mask].astype(np.float64)


class Histogram(wx.Panel):
    """Horizontal histogram with draggable range handles and an optional colorbar strip."""

    def __init__(
        self,
        parent: wx.Window,
        colormap: str = "gray",
        log_scale: bool = False,
        show_colorbar: bool = False,
        on_levels_changed: Callable | None = None,
        margin_left: int = 30,
        margin_right: int = 10,
        margin_top: int = 6,
        margin_bottom: int = 20,
        gradient_height: int = 12,
        gradient_gap: int = 4,
        handle_radius: int = 6,
        hit_radius: int = 10,
    ) -> None:
        """Initialise the Histogram widget.

        parent:            Parent wx.Window
        colormap:          Colormap name for the gradient strip (only used when show_colorbar=True)
        log_scale:         If True, use log-scale axis mapping for intensity images
        show_colorbar:     If True, draw a colormap gradient strip below the histogram
        on_levels_changed: Optional callback fired with (min, max) when handles move
        margin_left:       Left margin in pixels (default 30)
        margin_right:      Right margin in pixels (default 10)
        margin_top:        Top margin in pixels (default 6)
        margin_bottom:     Bottom margin in pixels (default 20)
        gradient_height:   Height of the colorbar strip in pixels (default 12)
        gradient_gap:      Gap between histogram and colorbar in pixels (default 4)
        handle_radius:     Radius of the handle circles in pixels (default 6)
        hit_radius:        Hit-test radius for handle dragging in pixels (default 10)
        """
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, 80))

        self._colormap = colormap
        self._log_scale = log_scale
        self._show_colorbar = show_colorbar
        self._margin_left = margin_left
        self._margin_right = margin_right
        self._margin_top = margin_top
        self._margin_bottom = margin_bottom
        self._gradient_height = gradient_height
        self._gradient_gap = gradient_gap
        self._handle_radius = handle_radius
        self._hit_radius = hit_radius
        self._min_val = 1.0
        self._max_val = 255.0
        self._level_min = 1.0
        self._level_max = 255.0
        self._bin_centers: np.ndarray | None = None
        self._counts: np.ndarray | None = None
        self._gradient_bitmap: wx.Bitmap | None = None
        self._gradient_bitmap_width: int = 0
        self._dragging: str | None = None
        self._drag_start_x: float = 0.0
        self._drag_start_min: float = 0.0
        self._drag_start_max: float = 0.0
        self._last_callback_levels: tuple[float, float] | None = None
        self._on_levels_changed = on_levels_changed

        register_darkdetect(self._on_theme_change)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)

    def set_colormap(self, colormap: str) -> None:
        """Set the colormap by name and redraw."""
        self._colormap = colormap
        self._gradient_bitmap = None
        self.Refresh()

    def set_data(self, data: np.ndarray, auto_scale: bool = False, data_range: tuple[float, float] | None = None) -> None:
        """Update histogram from a data array"""
        if data is None or data.size == 0:
            return

        # Use provided data_range for axis, or fall back to actual data range
        flat = data.ravel().astype(np.float64)

        if data_range is not None:
            new_min, new_max = data_range
            use_log = self._log_scale and new_min >= 0
        elif self._log_scale:
            # Always use positive pixels for log-scale detector images.
            # Negative pixels (gap/masked pixels) are excluded from the axis and histogram.
            positive = flat[flat > 0]
            if positive.size == 0:
                return
            raw_min = float(positive.min())
            raw_max = float(positive.max())
            new_min = raw_min
            new_max = raw_max if raw_max > raw_min else raw_min + 1.0
            use_log = True
        else:
            actual_min = float(flat.min())
            actual_max = float(flat.max())
            new_min = actual_min
            new_max = actual_max if actual_max > actual_min else actual_min + 1.0
            use_log = False

        self._bin_centers, self._counts = compute_histogram_data(flat, log_scale=use_log)
        self._min_val = new_min
        self._max_val = new_max
        if auto_scale or self._level_min >= self._level_max:
            self._level_min = new_min
            self._level_max = new_max
        self.Refresh()

    def set_levels(self, min_val: float, max_val: float) -> None:
        """Set the range handles directly."""
        # Ensure handles don't overlap
        if max_val <= min_val:
            max_val = min_val + 1.0
        self._level_min = min_val
        self._level_max = max_val
        self.Refresh()

    def get_levels(self) -> tuple[float, float]:
        """Return the current min, max handle values."""
        return self._level_min, self._level_max

    def set_range(self, min_val: float, max_val: float) -> None:
        """Set the data range shown by the histogram axis."""
        self._min_val = min_val
        self._max_val = max_val if max_val > self._min_val else self._min_val + 1.0
        self.Refresh()

    def _on_theme_change(self, is_dark: bool = False) -> None:
        """Repaint when the system theme changes."""
        self._gradient_bitmap = None
        self.Refresh()

    def _colorbar_height(self) -> int:
        """Return the total vertical space reserved for the colorbar strip."""
        return (self._gradient_height + self._gradient_gap) if self._show_colorbar else 0

    def _plot_rect(self) -> tuple[int, int, int, int]:
        """Return x, y, w, h of the histogram plot area."""
        w, h = self.GetSize()
        pb = h - self._margin_bottom - self._colorbar_height()
        return self._margin_left, self._margin_top, max(1, w - self._margin_left - self._margin_right), max(1, pb - self._margin_top)

    def _gradient_rect(self) -> tuple[int, int, int, int]:
        """Return x, y, w, h of the colorbar gradient strip."""
        w, h = self.GetSize()
        y = h - self._margin_bottom - self._gradient_height
        return self._margin_left, y, max(1, w - self._margin_left - self._margin_right), self._gradient_height

    def _val_to_x(self, value: float) -> float:
        """Map a data value to canvas x coordinate."""
        pl, _, pw, _ = self._plot_rect()
        if self._log_scale:
            # Use log scale for positive values, linear for negative
            if self._min_val >= 0.0:
                v_min = np.log1p(self._min_val)
                v_max = np.log1p(self._max_val)
                v = np.log1p(max(value, 0.0))
            else:
                # Mixed range: map linearly when min is negative
                v_min = self._min_val
                v_max = self._max_val
                v = value
        else:
            v_min = self._min_val
            v_max = self._max_val
            v = value
        if v_max == v_min:
            return pl + pw / 2.0
        t = max(0.0, min(1.0, (v - v_min) / (v_max - v_min)))
        return pl + t * pw

    def _x_to_val(self, x: float) -> float:
        """Map a canvas x coordinate to a data value."""
        pl, _, pw, _ = self._plot_rect()
        if self._log_scale:
            # Use log scale for positive values, linear for negative
            if self._min_val >= 0.0:
                v_min = np.log1p(self._min_val)
                v_max = np.log1p(self._max_val)
                t = max(0.0, min(1.0, (x - pl) / pw))
                v = v_min + t * (v_max - v_min)
                return np.expm1(v)
            else:
                # Mixed range: map linearly when min is negative
                v_min = self._min_val
                v_max = self._max_val
                t = max(0.0, min(1.0, (x - pl) / pw))
                return v_min + t * (v_max - v_min)
        else:
            v_min = self._min_val
            v_max = self._max_val
            t = max(0.0, min(1.0, (x - pl) / pw))
            return v_min + t * (v_max - v_min)

    def _build_gradient_bitmap(self, w: int, h: int) -> wx.Bitmap:
        """Build a wx.Bitmap of the current colormap gradient."""
        cmap = lookup_colormap(self._colormap)
        ts = np.linspace(0.0, 1.0, max(w, 1))
        rgba = cmap[ts].rgba
        rgb = (np.clip(rgba[:, :3], 0.0, 1.0) * 255).astype(np.uint8)
        data = np.ascontiguousarray(np.repeat(rgb[:, np.newaxis, :], h, axis=1).transpose(1, 0, 2))
        return wx.Bitmap.FromBuffer(w, h, data.tobytes())

    def _fmt_value(self, v: float) -> str:
        """Format a data value for display as a handle label."""
        if not math.isfinite(v):
            return ""
        if v == 0:
            return "0"
        av = abs(v)
        if v == int(v) and av < 1e15:
            n = int(v)
            return f"{n:,}" if av >= 1_000_000 else str(n)
        return f"{v:.4g}"

    def _on_paint(self, _: wx.PaintEvent) -> None:
        """Paint the histogram, optional colorbar, handles, and labels."""
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        bg = get_color("bg")
        border = get_color("graytext")
        theme = get_theme()
        hist_line = wx.Colour(theme.blue.Red(), theme.blue.Green(), theme.blue.Blue())
        hist_fill = wx.Colour(theme.blue.Red(), theme.blue.Green(), theme.blue.Blue(), 35)
        region_fill = wx.Colour(theme.blue.Red(), theme.blue.Green(), theme.blue.Blue(), 45)
        region_hover = wx.Colour(theme.blue.Red(), theme.blue.Green(), theme.blue.Blue(), 70)
        handle_min = wx.Colour(theme.red.Red(), theme.red.Green(), theme.red.Blue())
        handle_max = wx.Colour(theme.green.Red(), theme.green.Green(), theme.green.Blue())

        w, h = self.GetSize()
        pl, pt, pw, ph = self._plot_rect()

        gc.SetBrush(wx.Brush(bg))
        gc.DrawRectangle(0, 0, w, h)

        if self._show_colorbar:
            gx, gy, gw, gh = self._gradient_rect()
            bmp_w, bmp_h = int(gw), int(gh)
            if bmp_w > 0 and bmp_h > 0:
                if self._gradient_bitmap is None or self._gradient_bitmap_width != bmp_w:
                    self._gradient_bitmap = self._build_gradient_bitmap(bmp_w, bmp_h)
                    self._gradient_bitmap_width = bmp_w
                gc.DrawBitmap(self._gradient_bitmap, gx, gy, bmp_w, bmp_h)
            gc.SetPen(wx.Pen(border, 1))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(gx, gy, gw, gh)
            handle_bottom = gy + gh
        else:
            handle_bottom = pt + ph

        if self._bin_centers is not None and self._counts is not None and len(self._bin_centers) > 1:
            if self._log_scale and self._min_val >= 0:
                v_min = np.log1p(self._min_val)
                v_max = np.log1p(self._max_val)
            else:
                v_min = self._min_val
                v_max = self._max_val
            v_range = v_max - v_min or 1.0
            count_range = (self._counts.max() - self._counts.min()) or 1.0
            count_min = self._counts.min()

            pts = [
                (pl + max(0.0, min(1.0, (bc - v_min) / v_range)) * pw, pt + ph - (c - count_min) / count_range * ph)
                for bc, c in zip(self._bin_centers, self._counts)
            ]

            fill_path = gc.CreatePath()
            fill_path.MoveToPoint(pts[0][0], pt + ph)
            for px, py in pts:
                fill_path.AddLineToPoint(px, py)
            fill_path.AddLineToPoint(pts[-1][0], pt + ph)
            fill_path.CloseSubpath()
            gc.SetBrush(wx.Brush(hist_fill))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.FillPath(fill_path)

            line_path = gc.CreatePath()
            line_path.MoveToPoint(pts[0][0], pts[0][1])
            for px, py in pts[1:]:
                line_path.AddLineToPoint(px, py)
            gc.SetPen(wx.Pen(hist_line, 1))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.StrokePath(line_path)

        min_x = self._val_to_x(self._level_min)
        max_x = self._val_to_x(self._level_max)
        rw = max(min_x, max_x) - min(min_x, max_x)
        if rw > 0:
            fill_colour = region_hover if self._dragging == "region" else region_fill
            gc.SetBrush(wx.Brush(fill_colour))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(min(min_x, max_x), pt, rw, ph + self._colorbar_height())

        handle_bg = get_color("bg")
        for x, col in ((min_x, handle_min), (max_x, handle_max)):
            gc.SetPen(wx.Pen(col, 1))
            gc.StrokeLine(x, pt, x, handle_bottom)
            r = self._handle_radius
            gc.SetBrush(wx.Brush(col))
            gc.SetPen(wx.Pen(handle_bg, 1))
            gc.DrawEllipse(x - r, handle_bottom - r, r * 2, r * 2)

        font = wx.Font(wx.Size(0, 11), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        for x, col, val in ((min_x, handle_min, self._level_min), (max_x, handle_max, self._level_max)):
            gc.SetFont(font, col)
            lbl = self._fmt_value(val)
            tw, _ = gc.GetTextExtent(lbl)
            gc.DrawText(lbl, x - tw / 2, handle_bottom + 2 + self._handle_radius)

    def _on_mouse_down(self, event: wx.MouseEvent) -> None:
        """Begin dragging a handle or the selection region."""
        x = event.GetX()
        min_x = self._val_to_x(self._level_min)
        max_x = self._val_to_x(self._level_max)
        if abs(x - min_x) < self._hit_radius:
            self._dragging = "min"
            self.CaptureMouse()
        elif abs(x - max_x) < self._hit_radius:
            self._dragging = "max"
            self.CaptureMouse()
        elif min(min_x, max_x) <= x <= max(min_x, max_x):
            self._dragging = "region"
            self._drag_start_x = x
            self._drag_start_min = self._level_min
            self._drag_start_max = self._level_max
            self.CaptureMouse()

    def _on_mouse_up(self, event: wx.MouseEvent) -> None:
        """Release mouse capture and end drag."""
        if self._dragging and self.HasCapture():
            self.ReleaseMouse()
        self._dragging = None
        self.Refresh()

    def _on_mouse_move(self, event: wx.MouseEvent) -> None:
        """Update range handles while dragging."""
        if not self._dragging:
            return
        x = event.GetX()
        if self._dragging == "region":
            delta = x - self._drag_start_x
            if self._log_scale and self._min_val >= 0.0:
                # Use log scale only for fully positive range
                log_span = np.log1p(self._drag_start_max) - np.log1p(self._drag_start_min)
                log_dmin = np.log1p(self._min_val)
                log_dmax = np.log1p(self._max_val)
                new_min = self._x_to_val(self._val_to_x(self._drag_start_min) + delta)
                lmin = np.log1p(new_min)
                lmax = lmin + log_span
                if lmin < log_dmin:
                    lmin, lmax = log_dmin, log_dmin + log_span
                if lmax > log_dmax:
                    lmax, lmin = log_dmax, log_dmax - log_span
                self._level_min = np.expm1(lmin)
                self._level_max = np.expm1(lmax)
            else:
                # Use linear scale for negative or mixed ranges
                span = self._drag_start_max - self._drag_start_min
                new_min = self._x_to_val(self._val_to_x(self._drag_start_min) + delta)
                new_min = max(self._min_val, min(self._max_val - span, new_min))
                self._level_min = new_min
                self._level_max = new_min + span
        else:
            value = max(self._min_val, min(self._max_val, self._x_to_val(x)))
            if self._dragging == "min" and value < self._level_max:
                self._level_min = value
            elif self._dragging == "max" and value > self._level_min:
                self._level_max = value
        self.Refresh()
        # Only fire callback if the value actually changed
        current_levels = (self._level_min, self._level_max)
        if self._on_levels_changed and current_levels != self._last_callback_levels:
            self._last_callback_levels = current_levels
            self._on_levels_changed(self._level_min, self._level_max)

    def _on_size(self, event: wx.SizeEvent) -> None:
        """Unset gradient cache on resize."""
        self._gradient_bitmap = None
        self.Refresh()
        event.Skip()
