"""
styles.py - Design system stylesheet injector for maxanalysis platform.
Maintains backward compatibility by wrapping ui_shell.inject_styles.
Zero emojis.
"""

import base64
from pathlib import Path
from presentation_layer.components.ui_shell import inject_styles


def load_custom_css():
    """Injects the cinematic black-and-white editorial design system."""
    inject_styles()


def get_image_base64(filename: str) -> str:
    """Return a base64 Data URI for a local image with WebP preferred."""
    candidate_paths = [
        Path(__file__).parent.parent.parent / "static" / "images" / filename,
        Path(__file__).parent.parent.parent / "public" / "assets" / filename,
        Path(__file__).parent.parent / "assets" / "images" / filename
    ]
    for img_path in candidate_paths:
        if img_path.exists():
            with open(img_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            ext = img_path.suffix.lower().replace(".", "")
            mime = "webp" if ext == "webp" else ("jpeg" if ext in ("jpg", "jpeg") else ext)
            return f"data:image/{mime};base64,{encoded}"
    return ""
