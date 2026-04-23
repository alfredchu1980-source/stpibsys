# reference_module/ui.py
"""
UI 元件包裝器
提供統一的 UI 介面
"""

from .scanner import render_reference_scanner
from .uploader import render_reference_uploader

__all__ = [
    'render_reference_scanner',
    'render_reference_uploader',
]
