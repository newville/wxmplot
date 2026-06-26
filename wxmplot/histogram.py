#!/usr/bin/python

import numpy as np

__all__ = ["compute_histogram_data"]

_DEFAULT_MAX_PIXELS = 500_000


def compute_histogram_data(image: np.ndarray, max_pixels: int = _DEFAULT_MAX_PIXELS) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
    """Returns (bin_centers, log_counts) for a log-log histogram. Samples up to max_pixels pixels from the image before computing the histogram."""
    flat = image.ravel()
    if flat.size > max_pixels:
        flat = flat[:: flat.size // max_pixels]
    flat = flat.astype(np.float64)
    positive = flat[flat >= 0]
    if positive.size == 0:
        return None, None

    log_data = np.log1p(positive)
    log_data = log_data[np.isfinite(log_data)]
    if log_data.size == 0:
        return None, None

    hist, bin_edges = np.histogram(log_data, bins=1500)
    mask = hist > 0
    if not mask.any():
        return None, None

    return bin_edges[:-1][mask], np.log(hist[mask].astype(np.float64))
