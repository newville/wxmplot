#!/usr/bin/python
"""
wxmplot ImageCanvas: a generic hardware-accelerated image viewer widget using VisPy
with pan/zoom, ROI selection, line ROI, and pixel info overlay.
"""

import time
from enum import StrEnum
from typing import Callable

import numpy as np
import wx

from wxmplot.vispy_utils import vispy_colour, vispy_init, vsync_for_platform
from wxmplot.colors import lookup_colormap
from wxutils.themes import get_theme
from wxutils.colors import get_color, register_darkdetect

vispy_init()

from vispy import scene  # noqa: E402

__all__ = ["ImageCanvas", "BinMethod"]


class BinMethod(StrEnum):
    """Live downsampling method for ImageCanvas."""

    NONE = "none"
    STRIDE = "stride"
    MEAN = "mean"


# Integer dtypes the GPU can sample natively via VisPy's Image visual.
_GPU_NATIVE_INT_DTYPES = frozenset({np.uint8, np.uint16, np.uint32, np.int8, np.int16, np.int32})

# Largest integer downsampling factor applied to a live frame.
_MAX_LIVE_BIN = 4


def _bin_stride(image: np.ndarray, n: int) -> np.ndarray:
    """Zero-copy stride: image[::n, ::n]."""
    if n <= 1:
        return image
    return image[::n, ::n]


def _bin_mean(image: np.ndarray, n: int) -> np.ndarray:
    """Block mean binning: reshape then average. Full downsampling."""
    if n <= 1:
        return image
    h, w = image.shape[:2]
    h2 = (h // n) * n
    w2 = (w // n) * n
    if h2 == 0 or w2 == 0:
        return image
    cropped = image[:h2, :w2]
    if cropped.ndim == 2:
        return cropped.reshape(h2 // n, n, w2 // n, n).mean(axis=(1, 3), dtype=np.float32).astype(image.dtype, copy=False)
    c = cropped.shape[2]
    return cropped.reshape(h2 // n, n, w2 // n, n, c).mean(axis=(1, 3), dtype=np.float32).astype(image.dtype, copy=False)


def _bin_for_display(image: np.ndarray, n: int, method: BinMethod) -> np.ndarray:
    """Downsample image by factor n using BinMethod."""
    if n <= 1:
        return image
    if method == BinMethod.MEAN:
        return _bin_mean(image, n)
    return _bin_stride(image, n)


class ImageCanvas(wx.Panel):
    """Generic hardware-accelerated image viewer using VisPy."""

    _AUTO_CLIM_SAMPLE_BUDGET = 256_000

    def __init__(self, parent: wx.Window) -> None:
        """Initializes the ImageCanvas."""
        super().__init__(parent)

        self._canvas = scene.SceneCanvas(
            keys=None,
            parent=self,
            app="wx",
            vsync=vsync_for_platform(),
            size=(100, 100),
            bgcolor=tuple(c / 255 for c in get_color("bg")),
            config={"samples": 0, "double_buffer": True, "depth_size": 0, "stencil_size": 0},
        )
        self._view = self._canvas.central_widget.add_view()
        self._view.camera = scene.PanZoomCamera(aspect=1)
        self._view.camera.flip = (0, 1, 0)
        self._view.camera.interactive = False

        self._image_visual = scene.visuals.Image(
            np.zeros((512, 512), dtype=np.float32),
            parent=self._view.scene,
            cmap="grays",
            clim="auto",
        )

        self._raw_image = None
        self._colormap = "grays"
        self._first_image = True
        self._auto_scale = True
        self._filter_gaps = False
        self._min_value = 0.0
        self._max_value = 255.0
        self._data_min = 0.0
        self._data_max = 255.0

        self._pending_image = None
        self._redraw_interval_ms = 16
        self._redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_redraw_tick, self._redraw_timer)

        self._bin_method = BinMethod.NONE

        self._panning = False
        self._last_mouse_pos = None

        self._roi_selecting = False
        self._roi_start = None
        self._roi_img_coords = None
        self._roi_dragging = False
        self._roi_drag_start_img = None
        self._roi_drag_orig_coords = None
        self._on_roi_changed = None
        self._on_roi_cleared = None

        self._line_start_img = None
        self._line_end_img = None
        self._line_coords = None
        self._on_line_changed = None

        self._last_pixel_info_text = ""
        self._last_pixel_info_time = 0.0
        self._pixel_info_min_interval = 1.0 / 60.0

        self._roi_line = scene.visuals.Line(
            pos=np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=np.float32),
            color=vispy_colour("plot_selection"),
            width=2,
            method="gl",
            parent=self._view.scene,
        )
        self._roi_line.visible = False

        self._line_visual = scene.visuals.Line(
            pos=np.array([[0, 0], [1, 1]], dtype=np.float32),
            color=self._theme_yellow(200),
            width=2,
            method="gl",
            parent=self._view.scene,
        )
        self._line_visual.visible = False

        self._line_start_marker = scene.visuals.Markers(parent=self._view.scene)
        self._line_start_marker.set_data(
            pos=np.array([[0, 0, 0]], dtype=np.float32),
            face_color=(0, 0, 0, 0),
            edge_color=(0, 0, 0, 0),
            size=1,
        )
        self._line_start_marker.visible = False

        self._pixel_info_text = scene.visuals.Text(
            text="",
            color=vispy_colour("green"),
            font_size=6,
            bold=True,
            anchor_x="left",
            anchor_y="top",
            parent=self._canvas.scene,
        )
        self._pixel_info_text.visible = False

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._canvas.native, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self._canvas.show()

        register_darkdetect(self._on_theme_change)

        self._canvas.native.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self._canvas.native.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self._canvas.native.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self._canvas.native.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
        self._canvas.native.Bind(wx.EVT_RIGHT_UP, self._on_right_up)
        self._canvas.native.Bind(wx.EVT_MOTION, self._on_mouse_move)
        self._canvas.native.Bind(wx.EVT_RIGHT_DCLICK, self._on_right_dclick)

    def set_colormap(self, colormap: str) -> None:
        """Set the colormap by name."""
        self._colormap = colormap
        self._image_visual.cmap = lookup_colormap(colormap)
        self._canvas.update()

    def set_image(self, image: np.ndarray) -> None:
        """Stash the latest frame and pass it to the redraw timer."""
        if image is None or image.size == 0:
            return
        self._pending_image = image
        if not self._redraw_timer.IsRunning():
            self._redraw_timer.StartOnce(self._redraw_interval_ms)

    def set_contrast(self, min_val: float, max_val: float) -> None:
        """Set contrast limits and disable auto-scaling."""
        self._auto_scale = False
        self._min_value = min_val
        self._max_value = max_val
        self._image_visual.clim = (min_val, max_val)
        self._canvas.update()

    def set_auto_scale(self, enabled: bool) -> None:
        """Enable or disable automatic contrast scaling."""
        self._auto_scale = enabled
        if enabled and self._raw_image is not None:
            self._min_value, self._max_value = self._compute_auto_clim(self._raw_image)
            self._image_visual.clim = (self._min_value, self._max_value)
            self._canvas.update()

    def set_filter_gaps(self, enabled: bool) -> None:
        """Enable or disable zero-pixel filtering."""
        self._filter_gaps = enabled
        if self._auto_scale and self._raw_image is not None:
            self.set_auto_scale(True)

    def set_bin_method(self, method: BinMethod | str) -> None:
        """Switch the live downsampling method; accepts a BinMethod value or a plain string."""
        try:
            method = BinMethod(method)
        except ValueError:
            raise ValueError(f"Unknown bin method: {method!r}; expected one of {[m.value for m in BinMethod]}")
        self._bin_method = method
        if self._raw_image is not None:
            self._apply_image(self._raw_image)

    def reset_view(self) -> None:
        """Reset pan/zoom to fit the image and clear any active ROI."""
        if self._raw_image is not None:
            h, w = self._raw_image.shape[:2]
            self._view.camera.set_range(x=(0, w), y=(0, h))
        self._roi_img_coords = None
        self._roi_line.visible = False
        self._hide_line_visual()
        self._canvas.update()

    def get_roi_coords(self) -> tuple[int, int, int, int] | None:
        """Return the current ROI as (x1, y1, x2, y2) in image pixels, or None."""
        return self._roi_img_coords

    def get_line_coords(self) -> tuple[int, int, int, int] | None:
        """Return the current line ROI as (x1, y1, x2, y2) in image pixels, or None."""
        return self._line_coords

    def get_data_range(self) -> tuple[float, float]:
        """Return the (min, max) of the last auto-scaled frame."""
        return self._data_min, self._data_max

    def get_contrast_range(self) -> tuple[float, float]:
        """Return the current contrast (min, max) limits."""
        return self._min_value, self._max_value

    def format_pixel_info(self, ix: int, iy: int, intensity: float) -> str:
        """Return the pixel info string shown in the overlay. Override in a subclass to append specific fields."""
        return f"x: {ix}  y: {iy}  I: {intensity:.4g}"

    @property
    def bin_method(self) -> str:
        """Current live downsampling method."""
        return self._bin_method

    @property
    def native(self) -> wx.Window:
        """The VisPy native wx.Window."""
        return self._canvas.native

    def set_roi_changed_callback(self, callback: Callable) -> None:
        """Register a callback with (x1, y1, x2, y2) when the ROI changes."""
        self._on_roi_changed = callback

    def set_roi_cleared_callback(self, callback: Callable) -> None:
        """Register a callback when the ROI is cleared."""
        self._on_roi_cleared = callback

    def set_line_changed_callback(self, callback: Callable) -> None:
        """Register a callback with (x1, y1, x2, y2) when the line ROI changes."""
        self._on_line_changed = callback

    def _theme_yellow(self, alpha: int) -> tuple:
        """Return the theme yellow as a normalised (r, g, b, a) float tuple for VisPy."""
        c = get_theme().yellow
        return (c.Red() / 255, c.Green() / 255, c.Blue() / 255, alpha / 255)

    def _theme_green(self, alpha: int) -> tuple:
        """Return the theme green as a normalised (r, g, b, a) float tuple for VisPy."""
        c = get_theme().green
        return (c.Red() / 255, c.Green() / 255, c.Blue() / 255, alpha / 255)

    def _on_theme_change(self, is_dark: bool = False) -> None:
        """Update VisPy visual colours when the system theme changes."""
        self._canvas.bgcolor = tuple(c / 255 for c in get_color("bg"))
        self._roi_line.set_data(color=vispy_colour("plot_selection"))
        self._line_visual.set_data(color=self._theme_yellow(200))
        self._pixel_info_text.color = vispy_colour("green")
        self._canvas.update()

    def _on_redraw_tick(self, _: wx.TimerEvent) -> None:
        """Apply the latest pending frame and re-arm the timer if more arrived."""
        image = self._pending_image
        self._pending_image = None
        if image is not None:
            self._apply_image(image)
        if self._pending_image is not None:
            self._redraw_timer.StartOnce(self._redraw_interval_ms)

    def _apply_image(self, image: np.ndarray) -> None:
        """Sanitize, bin, and upload image to the GPU. Auto-scale if enabled."""
        is_rgb = image.ndim == 3 and image.shape[2] in (3, 4)
        if is_rgb and image.shape[2] == 4:
            image = image[:, :, :3]

        if image.dtype.type in _GPU_NATIVE_INT_DTYPES:
            full_res = image if image.flags.c_contiguous else np.ascontiguousarray(image)
        else:
            full_res = np.nan_to_num(image.astype(np.float32, copy=False), nan=0.0, posinf=0.0, neginf=0.0, copy=False)
        self._raw_image = full_res

        bin_factor = self._pick_live_bin_factor(full_res.shape[:2])
        gpu_image = _bin_for_display(full_res, bin_factor, self._bin_method)
        if not gpu_image.flags.c_contiguous:
            gpu_image = np.ascontiguousarray(gpu_image)

        if self._auto_scale:
            self._min_value, self._max_value = self._compute_auto_clim(gpu_image)
            self._data_min, self._data_max = self._min_value, self._max_value
            self._image_visual.clim = (self._min_value, self._max_value)

        self._image_visual.set_data(gpu_image)
        if self._first_image:
            self.reset_view()
            self._first_image = False
        self._canvas.update()

    def _pick_live_bin_factor(self, image_hw: tuple[int, int]) -> int:
        """Return the smallest integer bin factor that keeps the image larger than the canvas."""
        if self._bin_method == BinMethod.NONE:
            return 1
        cw, ch = self._canvas.size
        if cw <= 0 or ch <= 0:
            return 1
        ih, iw = image_hw
        ratio = max(iw / cw, ih / ch)
        if ratio <= 1.0:
            return 1
        return min(_MAX_LIVE_BIN, int(ratio))

    def _compute_auto_clim(self, img: np.ndarray) -> tuple[float, float]:
        """Estimate display clim from a sampled subset of pixels. Uses percentiles when filter_gaps is on."""
        flat = img.reshape(-1)
        step = max(1, flat.size // self._AUTO_CLIM_SAMPLE_BUDGET)
        sample = flat[::step]
        if self._filter_gaps:
            nonzero = sample[sample > 0]
            n = nonzero.size
            if n >= 3:
                k_lo = min(max(int(n * 0.01), 0), n - 1)
                k_hi = min(max(int(n * 0.99), k_lo + 1), n - 1)
                part = np.partition(nonzero, (k_lo, k_hi))
                return float(part[k_lo]), float(part[k_hi])
            if n > 0:
                return float(nonzero.min()), float(nonzero.max())
        return float(sample.min()), float(sample.max())

    def _screen_to_image(self, sx: int, sy: int) -> tuple[float, float] | None:
        """Map a canvas screen position to image pixel coordinates, or None if no image is loaded."""
        if self._raw_image is None:
            return None
        tr = self._image_visual.transforms.get_transform("canvas", "visual")
        img_pos = tr.map((sx, sy))
        return float(img_pos[0]), float(img_pos[1])

    def _is_inside_roi(self, ix: float, iy: float) -> bool:
        """Return True if the image coordinate falls within the current ROI bounds."""
        if self._roi_img_coords is None:
            return False
        x1, y1, x2, y2 = self._roi_img_coords
        return x1 <= ix <= x2 and y1 <= iy <= y2

    def _set_roi_visual(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Update and show the ROI rectangle visual."""
        pts = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]], dtype=np.float32)
        self._roi_line.set_data(pos=pts)
        self._roi_line.visible = True
        self._canvas.update()

    def _set_line_visual(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Update and show the line ROI visual."""
        self._line_visual.set_data(pos=np.array([[x1, y1], [x2, y2]], dtype=np.float32))
        self._line_visual.visible = True
        self._canvas.update()

    def _set_line_start_marker(self, x: float, y: float) -> None:
        """Place and show the line start marker at the given image coordinate."""
        c = self._theme_yellow(255)
        self._line_start_marker.set_data(
            pos=np.array([[x, y, 0]], dtype=np.float32),
            face_color=c,
            edge_color=c,
            size=8,
        )
        self._line_start_marker.visible = True
        self._canvas.update()

    def _hide_line_visual(self) -> None:
        """Hide the line ROI visual and clear all line state."""
        self._line_visual.visible = False
        self._line_start_marker.visible = False
        self._line_start_img = None
        self._line_end_img = None
        self._line_coords = None

    def _update_pixel_info(self, sx: int, sy: int) -> None:
        """Update the pixel info overlay text for the given screen position, rate-limited to 60 Hz."""
        now = time.perf_counter()
        if now - self._last_pixel_info_time < self._pixel_info_min_interval:
            return
        self._last_pixel_info_time = now
        img_pos = self._screen_to_image(sx, sy)
        if img_pos is None or self._raw_image is None:
            if self._pixel_info_text.visible:
                self._pixel_info_text.visible = False
                self._last_pixel_info_text = ""
                self._canvas.update()
            return
        ix, iy = int(img_pos[0]), int(img_pos[1])
        h, w = self._raw_image.shape[:2]
        if 0 <= ix < w and 0 <= iy < h:
            pixel = self._raw_image[iy, ix]
            _, canvas_h = self._canvas.size
            intensity = float(np.mean(pixel)) if self._raw_image.ndim == 3 else float(pixel)
            text = self.format_pixel_info(ix, iy, intensity)
            if text != self._last_pixel_info_text:
                self._pixel_info_text.text = text
                self._pixel_info_text.pos = (8, canvas_h - 20)
                self._pixel_info_text.visible = True
                self._last_pixel_info_text = text
                self._canvas.update()
        elif self._pixel_info_text.visible:
            self._pixel_info_text.visible = False
            self._last_pixel_info_text = ""
            self._canvas.update()

    def _on_mouse_wheel(self, event: wx.MouseEvent) -> None:
        """Zoom around the cursor position on mouse wheel."""
        if event.GetWheelRotation() == 0:
            return
        zoom = 1.1 ** (-event.GetWheelRotation() / 120.0)
        before = self._screen_to_image(event.GetX(), event.GetY())
        self._view.camera.zoom(zoom)
        if before is not None:
            after = self._screen_to_image(event.GetX(), event.GetY())
            if after is not None:
                self._view.camera.pan((before[0] - after[0], before[1] - after[1]))
        self._canvas.update()

    def _on_left_down(self, event: wx.MouseEvent) -> None:
        """Handle line ROI (alt+click) and ROI selection or drag (plain left drag)."""
        if event.AltDown():
            img_pos = self._screen_to_image(event.GetX(), event.GetY())
            if img_pos is not None:
                if self._line_start_img is None:
                    self._line_start_img = img_pos
                    self._roi_line.visible = False
                    self._roi_img_coords = None
                    self._set_line_start_marker(*img_pos)
                else:
                    x1, y1 = int(round(self._line_start_img[0])), int(round(self._line_start_img[1]))
                    x2, y2 = int(round(img_pos[0])), int(round(img_pos[1]))
                    self._line_start_img = None
                    self._line_end_img = img_pos
                    self._line_coords = (x1, y1, x2, y2)
                    self._line_start_marker.visible = False
                    self._set_line_visual(x1, y1, x2, y2)
                    if self._on_line_changed:
                        self._on_line_changed(x1, y1, x2, y2)
        else:
            self._line_start_img = None
            self._line_end_img = None
            self._line_coords = None
            self._hide_line_visual()
            img_pos = self._screen_to_image(event.GetX(), event.GetY())
            if img_pos is not None and self._is_inside_roi(*img_pos):
                self._roi_dragging = True
                self._roi_drag_start_img = img_pos
                self._roi_drag_orig_coords = self._roi_img_coords
            else:
                self._roi_selecting = True
                self._roi_start = (event.GetX(), event.GetY())
                self._roi_img_coords = None
                self._roi_line.visible = False
                self._canvas.update()
        event.Skip()

    def _on_right_down(self, event: wx.MouseEvent) -> None:
        """Start pan on right down."""
        self._panning = True
        self._last_mouse_pos = (event.GetX(), event.GetY())
        event.Skip()

    def _on_right_up(self, event: wx.MouseEvent) -> None:
        """End pan on right up."""
        self._panning = False
        self._last_mouse_pos = None
        event.Skip()

    def _on_left_up(self, event: wx.MouseEvent) -> None:
        """Finalise ROI drag or ROI selection on mouse release."""
        if self._roi_dragging:
            self._roi_dragging = False
            self._roi_drag_start_img = None
            self._roi_drag_orig_coords = None
            if self._on_roi_changed and self._roi_img_coords is not None:
                self._on_roi_changed(*self._roi_img_coords)
            self._canvas.update()
            event.Skip()
            return

        if self._roi_selecting and self._roi_start is not None:
            start_img = self._screen_to_image(*self._roi_start)
            end_img = self._screen_to_image(event.GetX(), event.GetY())
            if start_img is not None and end_img is not None:
                x1 = int(min(start_img[0], end_img[0]))
                y1 = int(min(start_img[1], end_img[1]))
                x2 = int(max(start_img[0], end_img[0]))
                y2 = int(max(start_img[1], end_img[1]))
                if x2 > x1 and y2 > y1:
                    self._roi_img_coords = (x1, y1, x2, y2)
                    self._set_roi_visual(x1, y1, x2, y2)
                    if self._on_roi_changed:
                        self._on_roi_changed(x1, y1, x2, y2)
                else:
                    self._roi_line.visible = False
            else:
                self._roi_line.visible = False

        self._roi_selecting = False
        self._roi_start = None
        self._canvas.update()
        event.Skip()

    def _on_mouse_move(self, event: wx.MouseEvent) -> None:
        """Drive pan, ROI drag, ROI rubber-band, line preview, and pixel info on mouse move."""
        if self._panning and self._last_mouse_pos:
            dx = event.GetX() - self._last_mouse_pos[0]
            dy = event.GetY() - self._last_mouse_pos[1]
            self._view.camera.pan((-dx, -dy))
            self._canvas.update()
            self._last_mouse_pos = (event.GetX(), event.GetY())
        elif self._roi_dragging and self._roi_drag_start_img is not None:
            cur = self._screen_to_image(event.GetX(), event.GetY())
            if cur is not None and self._roi_drag_orig_coords is not None:
                dx = cur[0] - self._roi_drag_start_img[0]
                dy = cur[1] - self._roi_drag_start_img[1]
                ox1, oy1, ox2, oy2 = self._roi_drag_orig_coords
                if self._raw_image is not None:
                    h, w = self._raw_image.shape[:2]
                    rw, rh = ox2 - ox1, oy2 - oy1
                    nx1 = max(0, min(int(ox1 + dx), w - rw))
                    ny1 = max(0, min(int(oy1 + dy), h - rh))
                    nx2, ny2 = nx1 + rw, ny1 + rh
                else:
                    nx1, ny1 = int(ox1 + dx), int(oy1 + dy)
                    nx2, ny2 = int(ox2 + dx), int(oy2 + dy)
                self._roi_img_coords = (nx1, ny1, nx2, ny2)
                self._set_roi_visual(nx1, ny1, nx2, ny2)
        elif self._roi_selecting and self._roi_start is not None:
            start_img = self._screen_to_image(*self._roi_start)
            end_img = self._screen_to_image(event.GetX(), event.GetY())
            if start_img is not None and end_img is not None:
                x1 = min(start_img[0], end_img[0])
                y1 = min(start_img[1], end_img[1])
                x2 = max(start_img[0], end_img[0])
                y2 = max(start_img[1], end_img[1])
                if x2 > x1 and y2 > y1:
                    self._set_roi_visual(x1, y1, x2, y2)
        elif self._line_start_img is not None and event.AltDown():
            img_pos = self._screen_to_image(event.GetX(), event.GetY())
            if img_pos is not None:
                self._set_line_visual(self._line_start_img[0], self._line_start_img[1], img_pos[0], img_pos[1])
        else:
            img_pos = self._screen_to_image(event.GetX(), event.GetY())
            cursor = wx.CURSOR_SIZING if (img_pos is not None and self._is_inside_roi(*img_pos)) else wx.CURSOR_DEFAULT
            self._canvas.native.SetCursor(wx.Cursor(cursor))

        self._update_pixel_info(event.GetX(), event.GetY())
        event.Skip()

    def _on_right_dclick(self, event: wx.MouseEvent) -> None:
        """Reset view and clear ROI on right double-click."""
        if self._raw_image is not None:
            h, w = self._raw_image.shape[:2]
            self._view.camera.set_range(x=(0, w), y=(0, h))
        self._roi_img_coords = None
        self._roi_line.visible = False
        self._hide_line_visual()
        self._canvas.update()
        if self._on_roi_cleared:
            self._on_roi_cleared()
        event.Skip()
