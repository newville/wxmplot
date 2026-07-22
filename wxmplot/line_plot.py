#!/usr/bin/python
"""
wxmplot LinePlot: a generic 1D line plot widget with pan/zoom, fill area, zoom, and
hover overlay.  Axes, tick labels, and overlays are painted with wx.GraphicsContext
on the outer wx.Panel and the curve and fill are rendered by a VisPy SceneCanvas
embedded inside the plot margins.
"""

import math
from typing import Callable

import numpy as np
import wx
from wxutils.colors import get_color, is_dark_theme, register_darkdetect
from wxutils.themes import get_theme

from wxmplot.vispy_utils import vispy_colour, vispy_init, vsync_for_platform

vispy_init()

from vispy import scene  # noqa: E402

__all__ = ["LinePlot"]


class LinePlot(wx.Panel):
    """Generic 1D line plot with VisPy curve rendering and wx.GC axes."""

    def __init__(
        self,
        parent: wx.Window,
        margin_left: int = 82,
        margin_right: int = 14,
        margin_top: int = 30,
        margin_bottom: int = 50,
    ) -> None:
        """Initialise the LinePlot panel."""
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetMinSize((-1, 160))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self._ml = margin_left
        self._mr = margin_right
        self._mt = margin_top
        self._mb = margin_bottom

        self._xs: np.ndarray | None = None
        self._ys: np.ndarray | None = None
        self._x_label: str = "x"
        self._y_label: str = "y"

        self._hover_data_x: float | None = None
        self._hover_data_y: float | None = None

        self._zoom_x_min: float | None = None
        self._zoom_x_max: float | None = None
        self._zoom_y_min: float | None = None
        self._zoom_y_max: float | None = None
        self._panning: bool = False
        self._pan_last_pt: wx.Point | None = None
        self._drag_start: wx.Point | None = None
        self._drag_end: wx.Point | None = None

        self._data_changed_cb: Callable[[np.ndarray, np.ndarray], None] | None = None

        self._canvas = scene.SceneCanvas(
            keys=None,
            parent=self,
            app="wx",
            vsync=vsync_for_platform(),
            size=(100, 100),
            bgcolor=vispy_colour("bg"),
            config={"double_buffer": True, "depth_size": 0, "stencil_size": 0},
        )
        self._view = self._canvas.central_widget.add_view()
        self._view.camera = scene.PanZoomCamera(aspect=None)
        self._view.camera.interactive = False

        self._curve_line = scene.visuals.Line(
            pos=np.array([[0, 0], [1, 1]], dtype=np.float32),
            color=vispy_colour("plot_curve"),
            width=1.5,
            method="agg",
            parent=self._view.scene,
        )
        self._curve_line.visible = False

        self._fill_mesh = scene.visuals.Mesh(
            vertices=np.zeros((4, 2), dtype=np.float32),
            faces=np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
            color=vispy_colour("plot_fill"),
            parent=self._view.scene,
        )
        self._fill_mesh.visible = False

        self._sel_line = scene.visuals.Line(
            pos=np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=np.float32),
            color=vispy_colour("plot_selection"),
            width=1,
            method="agg",
            connect="strip",
            parent=self._view.scene,
        )
        self._sel_line.visible = False

        self._canvas.native.Hide()

        register_darkdetect(self._on_theme_change)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self._on_right_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_RIGHT_DCLICK, self._on_right_dclick)

        self._canvas.native.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self._canvas.native.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
        self._canvas.native.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        self._canvas.native.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
        self._canvas.native.Bind(wx.EVT_RIGHT_UP, self._on_right_up)
        self._canvas.native.Bind(wx.EVT_MOTION, self._on_canvas_mouse_move)
        self._canvas.native.Bind(wx.EVT_LEAVE_WINDOW, self._on_canvas_leave)
        self._canvas.native.Bind(wx.EVT_RIGHT_DCLICK, self._on_right_dclick)

        wx.CallAfter(self._reposition_canvas)

    def set_data(self, xs: np.ndarray, ys: np.ndarray, x_label: str = "x", y_label: str = "y") -> None:
        """Set the curve data and reset zoom."""
        self._xs = xs
        self._ys = ys
        self._x_label = x_label
        self._y_label = y_label
        self._zoom_x_min = self._zoom_x_max = self._zoom_y_min = self._zoom_y_max = None
        self._rebuild_visuals()
        self.Refresh()
        if self._data_changed_cb is not None:
            self._data_changed_cb(xs, ys)

    def clear(self) -> None:
        """Clear all data and reset the plot."""
        self._xs = None
        self._ys = None
        self._x_label = "x"
        self._y_label = "y"
        self._zoom_x_min = self._zoom_x_max = self._zoom_y_min = self._zoom_y_max = None
        self._rebuild_visuals()
        self.Refresh()

    def reset_view(self) -> None:
        """Reset zoom to show the full data range."""
        self._zoom_x_min = self._zoom_x_max = self._zoom_y_min = self._zoom_y_max = None
        if self._xs is not None:
            self._sync_camera()
        self.Refresh()

    def set_data_changed_callback(self, callback: Callable[[np.ndarray, np.ndarray], None]) -> None:
        """Register a callback fired with (xs, ys) whenever new data is set."""
        self._data_changed_cb = callback

    def format_hover_info(self, x: float, y: float) -> str:
        """Return the hover overlay string. Override in a subclass to add domain fields."""
        return f"{self._x_label}: {x:.4g}   {self._y_label}: {y:.4g}"

    def draw_overlays(self, gc: wx.GraphicsContext, W: int, H: int) -> None:
        """Hook for subclasses to paint additional overlays after axes are drawn."""

    @property
    def xs(self) -> np.ndarray | None:
        """Current x data array."""
        return self._xs

    @property
    def ys(self) -> np.ndarray | None:
        """Current y data array."""
        return self._ys

    def _on_theme_change(self, is_dark: bool = False) -> None:
        """Update VisPy visual colours and background when the system theme changes."""
        self._canvas.bgcolor = vispy_colour("bg")
        self._curve_line.set_data(color=vispy_colour("plot_curve"))
        self._fill_mesh.color = vispy_colour("plot_fill")
        self._sel_line.set_data(color=vispy_colour("plot_selection"))
        self._canvas.update()
        self.Refresh()

    def _reposition_canvas(self) -> None:
        """Reposition the embedded VisPy canvas inside the plot margins."""
        W, H = self.GetSize()
        pw = W - self._ml - self._mr
        ph = H - self._mt - self._mb
        self._canvas.native.SetPosition((self._ml, self._mt))
        self._canvas.native.SetSize((max(1, pw), max(1, ph)))
        self._canvas.native.Lower()

    def _data_ranges(self) -> tuple[float, float, float, float] | None:
        """Return (x_min, x_max, y_min, y_max) from current zoom or full data."""
        if self._xs is None or self._ys is None or len(self._xs) < 2:
            return None
        x_min = self._zoom_x_min if self._zoom_x_min is not None else float(self._xs[0])
        x_max = self._zoom_x_max if self._zoom_x_max is not None else float(self._xs[-1])
        y_min = self._zoom_y_min if self._zoom_y_min is not None else float(self._ys.min())
        y_max = self._zoom_y_max if self._zoom_y_max is not None else float(self._ys.max())
        if x_max == x_min:
            x_max = x_min + 1
        if y_max == y_min:
            y_max = y_min + 1
        return x_min, x_max, y_min, y_max

    def _rebuild_visuals(self) -> None:
        """Rebuild the VisPy curve, fill mesh, and camera from current data."""
        ranges = self._data_ranges()
        has_data = ranges is not None and self._xs is not None and self._ys is not None

        self._curve_line.visible = has_data
        self._fill_mesh.visible = has_data
        self._canvas.native.Show(has_data)

        if not has_data:
            self._canvas.update()
            return

        xs, ys = self._xs, self._ys
        x_min, x_max, y_min, y_max = ranges

        pts = np.column_stack([xs, ys]).astype(np.float32)
        self._curve_line.set_data(pos=pts)

        n = len(xs)
        verts = np.empty((2 * n, 2), dtype=np.float32)
        verts[:n, 0] = xs
        verts[:n, 1] = ys
        verts[n:, 0] = xs
        verts[n:, 1] = y_min
        faces = np.empty((2 * (n - 1), 3), dtype=np.uint32)
        for i in range(n - 1):
            faces[2 * i] = [i, i + 1, n + i]
            faces[2 * i + 1] = [i + 1, n + i + 1, n + i]
        self._fill_mesh.set_data(vertices=verts, faces=faces, color=vispy_colour("plot_fill"))

        self._sync_camera()

    def _sync_camera(self) -> None:
        """Sync the VisPy camera to the current data ranges."""
        ranges = self._data_ranges()
        if ranges is None:
            return
        x_min, x_max, y_min, y_max = ranges
        self._view.camera.set_range(x=(x_min, x_max), y=(y_min, y_max), margin=0)
        self._canvas.update()

    def _canvas_pt_to_panel(self, cx: int, cy: int) -> wx.Point:
        """Translate a canvas-local coordinate to panel coordinates."""
        return wx.Point(cx + self._ml, cy + self._mt)

    def _panel_pt_in_plot(self, pt: wx.Point) -> bool:
        """Return True if pt falls within the plot area."""
        W, H = self.GetSize()
        return self._ml <= pt.x <= W - self._mr and self._mt <= pt.y <= H - self._mb

    def _panel_pt_to_data(self, pt: wx.Point) -> tuple[float, float] | None:
        """Map a panel coordinate to data coordinates."""
        ranges = self._data_ranges()
        if ranges is None:
            return None
        W, H = self.GetSize()
        pw = W - self._ml - self._mr
        ph = H - self._mt - self._mb
        if pw <= 0 or ph <= 0:
            return None
        x_min, x_max, y_min, y_max = ranges
        dx = x_min + (pt.x - self._ml) / pw * (x_max - x_min)
        dy = y_max - (pt.y - self._mt) / ph * (y_max - y_min)
        return dx, dy

    def _update_sel_box(self) -> None:
        """Update the rubber-band selection rectangle visual."""
        if self._drag_start is None or self._drag_end is None:
            self._sel_line.visible = False
            self._canvas.update()
            return
        ranges = self._data_ranges()
        if ranges is None:
            self._sel_line.visible = False
            self._canvas.update()
            return
        W, H = self.GetSize()
        pw = W - self._ml - self._mr
        ph = H - self._mt - self._mb
        x_min, x_max, y_min, y_max = ranges

        s, e = self._drag_start, self._drag_end
        cx0 = max(0, min(pw, s.x - self._ml))
        cx1 = max(0, min(pw, e.x - self._ml))
        cy0 = max(0, min(ph, s.y - self._mt))
        cy1 = max(0, min(ph, e.y - self._mt))
        sx = sorted([cx0, cx1])
        sy = sorted([cy0, cy1])
        if sx[1] - sx[0] <= 1 or sy[1] - sy[0] <= 1:
            self._sel_line.visible = False
            self._canvas.update()
            return
        dx0 = x_min + sx[0] / pw * (x_max - x_min)
        dx1 = x_min + sx[1] / pw * (x_max - x_min)
        dy0 = y_max - sy[1] / ph * (y_max - y_min)
        dy1 = y_max - sy[0] / ph * (y_max - y_min)
        pos = np.array([[dx0, dy0], [dx1, dy0], [dx1, dy1], [dx0, dy1], [dx0, dy0]], dtype=np.float32)
        self._sel_line.set_data(pos=pos)
        self._sel_line.visible = True
        self._canvas.update()

    def _clear_hover_state(self) -> None:
        """Clear all hover, pan, and drag state."""
        changed = self._hover_data_x is not None
        self._hover_data_x = None
        self._hover_data_y = None
        self._panning = False
        self._pan_last_pt = None
        self._drag_start = None
        self._drag_end = None
        self._sel_line.visible = False
        self._canvas.update()
        if changed:
            self.Refresh()

    def _handle_mouse_move(self, pt: wx.Point, event: wx.MouseEvent) -> None:
        """Handle shared mouse-move logic for both panel and canvas events."""
        W, H = self.GetSize()

        if self._drag_start is not None:
            self._drag_end = pt
            self._update_sel_box()
            self.Refresh()
            event.Skip()
            return

        if self._panning and self._pan_last_pt is not None:
            ranges = self._data_ranges()
            if ranges is not None:
                pw = W - self._ml - self._mr
                ph = H - self._mt - self._mb
                x_min, x_max, y_min, y_max = ranges
                dx = (pt.x - self._pan_last_pt.x) / pw * (x_max - x_min)
                dy = (pt.y - self._pan_last_pt.y) / ph * (y_max - y_min)
                self._zoom_x_min = x_min - dx
                self._zoom_x_max = x_max - dx
                self._zoom_y_min = y_min + dy
                self._zoom_y_max = y_max + dy
                self._pan_last_pt = pt
                self._sync_camera()
                self.Refresh()
            event.Skip()
            return

        ranges = self._data_ranges()
        pw = W - self._ml - self._mr
        ph = H - self._mt - self._mb
        if ranges is not None and self._ml <= pt.x <= self._ml + pw and self._mt <= pt.y <= self._mt + ph:
            x_min, x_max, y_min, y_max = ranges
            new_x = x_min + (pt.x - self._ml) / pw * (x_max - x_min)
            new_y = y_max - (pt.y - self._mt) / ph * (y_max - y_min)
        else:
            new_x, new_y = None, None

        if new_x != self._hover_data_x or new_y != self._hover_data_y:
            self._hover_data_x = new_x
            self._hover_data_y = new_y
            self.Refresh()
        event.Skip()

    def _on_mouse_wheel(self, event: wx.MouseEvent) -> None:
        """Zoom around the cursor position on mouse wheel."""
        if self._xs is None or len(self._xs) < 2:
            event.Skip()
            return
        W, H = self.GetSize()
        pw, ph = W - self._ml - self._mr, H - self._mt - self._mb
        raw_pt = event.GetPosition()
        obj = event.GetEventObject()
        pt = self._canvas_pt_to_panel(raw_pt.x, raw_pt.y) if obj is self._canvas.native else raw_pt
        if not (self._ml <= pt.x <= self._ml + pw and self._mt <= pt.y <= self._mt + ph):
            event.Skip()
            return
        ranges = self._data_ranges()
        if ranges is None:
            event.Skip()
            return
        x_min, x_max, y_min, y_max = ranges
        factor = 1.15 ** (-event.GetWheelRotation() / 120.0)
        mx = x_min + (pt.x - self._ml) / pw * (x_max - x_min)
        my = y_max - (pt.y - self._mt) / ph * (y_max - y_min)
        self._zoom_x_min = mx + (x_min - mx) * factor
        self._zoom_x_max = mx + (x_max - mx) * factor
        self._zoom_y_min = my + (y_min - my) * factor
        self._zoom_y_max = my + (y_max - my) * factor
        self._sync_camera()
        self.Refresh()
        event.Skip()

    def _on_right_dclick(self, event: wx.MouseEvent) -> None:
        """Reset zoom to full data range on right double-click."""
        self._zoom_x_min = self._zoom_x_max = self._zoom_y_min = self._zoom_y_max = None
        if self._xs is not None:
            self._sync_camera()
        self.Refresh()
        event.Skip()

    def _on_right_down(self, event: wx.MouseEvent) -> None:
        """Start pan on right down."""
        raw_pt = event.GetPosition()
        obj = event.GetEventObject()
        pt = self._canvas_pt_to_panel(raw_pt.x, raw_pt.y) if obj is self._canvas.native else raw_pt
        if self._xs is None:
            event.Skip()
            return
        self._panning = True
        self._pan_last_pt = pt
        event.Skip()

    def _on_right_up(self, event: wx.MouseEvent) -> None:
        """End pan on right up."""
        self._panning = False
        self._pan_last_pt = None
        event.Skip()

    def _on_mouse_move(self, event: wx.MouseEvent) -> None:
        """Forward panel mouse-move to the shared handler."""
        self._handle_mouse_move(event.GetPosition(), event)

    def _on_canvas_mouse_move(self, event: wx.MouseEvent) -> None:
        """Translate canvas mouse-move to panel coordinates and forward."""
        pt = self._canvas_pt_to_panel(event.GetPosition().x, event.GetPosition().y)
        self._handle_mouse_move(pt, event)

    def _on_leave(self, event: wx.MouseEvent) -> None:
        """Clear hover state when the mouse leaves the panel."""
        self._clear_hover_state()
        event.Skip()

    def _on_canvas_leave(self, event: wx.MouseEvent) -> None:
        """Clear hover state when the mouse leaves the canvas."""
        self._clear_hover_state()
        event.Skip()

    def _on_mouse_down(self, event: wx.MouseEvent) -> None:
        """Start rubber-band zoom on left down."""
        raw_pt = event.GetPosition()
        obj = event.GetEventObject()
        pt = self._canvas_pt_to_panel(raw_pt.x, raw_pt.y) if obj is self._canvas.native else raw_pt
        if self._xs is None:
            event.Skip()
            return
        if self._panel_pt_in_plot(pt):
            self._drag_start = self._drag_end = pt
        event.Skip()

    def _on_mouse_up(self, event: wx.MouseEvent) -> None:
        """Apply rubber-band zoom on left up."""
        if self._drag_start is not None:
            raw_pt = event.GetPosition()
            obj = event.GetEventObject()
            end = self._canvas_pt_to_panel(raw_pt.x, raw_pt.y) if obj is self._canvas.native else raw_pt
            start = self._drag_start
            self._drag_start = self._drag_end = None
            self._sel_line.visible = False
            self._canvas.update()
            ranges = self._data_ranges()
            if ranges is not None:
                W, H = self.GetSize()
                pw = W - self._ml - self._mr
                ph = H - self._mt - self._mb
                x_min, x_max, y_min, y_max = ranges
                sx = sorted([start.x, end.x])
                sy = sorted([start.y, end.y])
                if sx[1] - sx[0] > 4 and sy[1] - sy[0] > 4:
                    self._zoom_x_min = x_min + (sx[0] - self._ml) / pw * (x_max - x_min)
                    self._zoom_x_max = x_min + (sx[1] - self._ml) / pw * (x_max - x_min)
                    self._zoom_y_min = y_max - (sy[1] - self._mt) / ph * (y_max - y_min)
                    self._zoom_y_max = y_max - (sy[0] - self._mt) / ph * (y_max - y_min)
                    self._sync_camera()
            self.Refresh()
            event.Skip()
            return
        event.Skip()

    def _on_size(self, event: wx.SizeEvent) -> None:
        """Reposition the canvas and sync camera on resize."""
        self._reposition_canvas()
        if self._xs is not None:
            self._sync_camera()
        self.Refresh()
        event.Skip()

    def _on_paint(self, _: wx.PaintEvent) -> None:
        """Paint axes, tick labels, axis labels, and subclass overlays using theme colours."""
        dc = wx.AutoBufferedPaintDC(self)
        dc.DestroyClippingRegion()
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return
        self._draw_axes(gc, *self.GetSize())

    def _draw_axes(self, gc: wx.GraphicsContext, W: int, H: int) -> None:
        """Draw axes, labels, and overlays into gc at size (W, H)."""
        bg = get_color("bg")
        border = get_color("graytext")
        tick_label = get_color("text")
        axis_label = get_color("text")
        empty_text = get_color("graytext")

        ml, mr, mt, mb = self._ml, self._mr, self._mt, self._mb
        pw, ph = W - ml - mr, H - mt - mb

        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, ml, H)
        gc.DrawRectangle(ml, 0, pw, mt)
        gc.DrawRectangle(ml, mt + ph, pw, mb)
        gc.DrawRectangle(ml + pw, 0, mr, H)

        gc.SetPen(wx.Pen(border, 1))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.StrokeLine(ml, mt + ph, ml + pw, mt + ph)
        gc.StrokeLine(ml, mt, ml, mt + ph)

        font_small = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        ranges = self._data_ranges()

        if ranges is None:
            gc.SetBrush(wx.Brush(get_color("bg")))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(ml, mt, pw, ph)
            gc.SetFont(
                wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                empty_text,
            )
            msg = "No data"
            tw, th = gc.GetTextExtent(msg)
            gc.DrawText(msg, ml + pw / 2 - tw / 2, mt + ph / 2 - th / 2)
        else:
            x_min, x_max, y_min, y_max = ranges

            gc.SetFont(font_small, tick_label)
            for i in range(5):
                t = i / 4
                y_val = y_min + t * (y_max - y_min)
                py = mt + ph - t * ph
                av = abs(y_val)
                if av == 0:
                    lbl = "0"
                elif av >= 1e6 or (0 < av < 0.01):
                    lbl = f"{y_val:.2e}"
                elif av >= 1000:
                    lbl = f"{y_val:,.0f}"
                elif av >= 10:
                    lbl = f"{y_val:.1f}"
                else:
                    lbl = f"{y_val:.3f}"
                tw, th = gc.GetTextExtent(lbl)
                gc.DrawText(lbl, ml - tw - 4, py - th / 2)

            for i in range(5):
                t = i / 4
                x_val = x_min + t * (x_max - x_min)
                px = ml + t * pw
                gc.SetPen(wx.Pen(border, 1))
                gc.StrokeLine(px, mt + ph, px, mt + ph + 3)
                lbl = f"{x_val:.4g}"
                tw, _ = gc.GetTextExtent(lbl)
                gc.DrawText(lbl, px - tw / 2, mt + ph + 5)

            gc.SetFont(font_small, axis_label)
            x_lw, _ = gc.GetTextExtent(self._x_label)
            gc.DrawText(self._x_label, ml + pw / 2 - x_lw / 2, H - mb + 20)

            y_lw, y_lh = gc.GetTextExtent(self._y_label)
            gc.PushState()
            gc.Translate(y_lh, mt + ph / 2 + y_lw / 2)
            gc.Rotate(-math.pi / 2)
            gc.DrawText(self._y_label, 0, 0)
            gc.PopState()

        if self._hover_data_x is not None and self._hover_data_y is not None:
            hover_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            gc.SetFont(hover_font, get_theme().green)
            text = self.format_hover_info(self._hover_data_x, self._hover_data_y)
            tw, th = gc.GetTextExtent(text)
            gc.DrawText(text, ml + pw - tw - 6, mt + 4)

        self.draw_overlays(gc, W, H)

    def render_to_array(self) -> np.ndarray:
        """Render the full plot (axes + embedded VisPy curve) to an RGB numpy array."""
        W, H = self.GetSize()
        ml, mr, mt, mb = self._ml, self._mr, self._mt, self._mb
        pw, ph = W - ml - mr, H - mt - mb

        # Axes, labels, overlays using memory DC
        bmp = wx.Bitmap(W, H)
        mem_dc = wx.MemoryDC(bmp)
        mem_dc.SetBackground(wx.Brush(get_color("bg")))
        mem_dc.Clear()
        gc = wx.GraphicsContext.Create(mem_dc)
        if gc is not None:
            self._draw_axes(gc, W, H)
        mem_dc.SelectObject(wx.NullBitmap)
        img = bmp.ConvertToImage()
        axes_rgb = np.frombuffer(img.GetData(), dtype=np.uint8).reshape(H, W, 3)

        # Embedded VisPy curve using framebuffer readback
        canvas_rgba = self._canvas.render()
        canvas_rgb = canvas_rgba[:, :, :3]
        ch, cw = canvas_rgb.shape[:2]
        if (ch, cw) != (ph, pw):
            img_c = wx.Image(cw, ch)
            img_c.SetData(canvas_rgb.tobytes())
            img_c = img_c.Scale(pw, ph, wx.IMAGE_QUALITY_HIGH)
            canvas_rgb = np.frombuffer(img_c.GetData(), dtype=np.uint8).reshape(ph, pw, 3)

        result = axes_rgb.copy()
        result[mt:mt + ph, ml:ml + pw] = canvas_rgb
        return result

