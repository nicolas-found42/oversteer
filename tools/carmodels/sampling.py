"""Explicit colour-space and alpha-aware image sampling for mesh-baked sprites."""

import numpy as np
from PIL import Image

FILTERS = {
    "nearest": Image.Resampling.NEAREST,
    "box": Image.Resampling.BOX,
    "bilinear": Image.Resampling.BILINEAR,
    "bicubic": Image.Resampling.BICUBIC,
    "lanczos": Image.Resampling.LANCZOS,
}


def to_linear(rgb):
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def to_srgb(rgb):
    return np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.maximum(rgb, 0) ** (1 / 2.4) - 0.055)


def resample(image, pixels, method, space, alpha):
    """Explicit channels avoid Pillow silently changing the alpha experiment."""
    values = np.asarray(image.convert("RGBA"), dtype=np.float32) / 255
    rgb, coverage = values[..., :3], values[..., 3:4]
    if space == "linear":
        rgb = to_linear(rgb)
    if alpha == "premultiplied":
        rgb = rgb * coverage
    source = np.concatenate([rgb, coverage], axis=2)
    result = np.stack(
        [
            np.asarray(Image.fromarray(source[..., c]).resize((pixels, pixels), FILTERS[method]))
            for c in range(4)
        ],
        axis=2,
    )
    coverage = np.clip(result[..., 3:4], 0, 1)
    rgb = result[..., :3]
    if alpha == "premultiplied":
        rgb = np.divide(rgb, coverage, out=np.zeros_like(rgb), where=coverage > 1e-8)
    rgb = np.clip(rgb, 0, 1)
    if space == "linear":
        rgb = to_srgb(rgb)
    return Image.fromarray(
        np.round(np.clip(np.concatenate([rgb, coverage], axis=2), 0, 1) * 255).astype(np.uint8)
    )


def mip_chain(image):
    """Nine 256→1 levels from a 512px source, without intermediate quantization."""
    if image.size != (512, 512):
        raise ValueError("Production mip baking requires a 512px source")
    values = np.asarray(image.convert("RGBA"), dtype=np.float32) / 255
    values[..., :3] = to_linear(values[..., :3]) * values[..., 3:4]
    while values.shape[0] > 1:
        size = values.shape[0] // 2
        values = values.reshape(size, 2, size, 2, 4).mean(axis=(1, 3))
        coverage = values[..., 3:4]
        rgb = np.divide(
            values[..., :3], coverage, out=np.zeros_like(values[..., :3]), where=coverage > 1e-8
        )
        rgba = np.concatenate([to_srgb(np.clip(rgb, 0, 1)), coverage], axis=2)
        yield Image.fromarray(np.round(np.clip(rgba, 0, 1) * 255).astype(np.uint8))
