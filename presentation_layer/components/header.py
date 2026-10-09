"""
header.py - Header component for maxanalysis platform.
Maintains backward compatibility by wrapping ui_shell.render_header.
Zero emojis.
"""

from typing import Callable, Optional
from presentation_layer.components.ui_shell import render_header as shell_render_header


def render_header(current_page: str = "home", refresh_callback: Optional[Callable[[], bool]] = None):
    """
    Renders the unified sticky maxanalysis top header on every page.
    Delegates to ui_shell.render_header.
    """
    shell_render_header(active_page=current_page, refresh_callback=refresh_callback)
