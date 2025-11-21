#!/usr/bin/env python3
"""
Helper Utilities for AutoDiag Pro
Common utility functions and helpers
"""

from datetime import datetime


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_brand_list():
    """Get list of supported brands - fallback if shared module not available"""
    try:
        from shared.brand_database import get_brand_list
        return get_brand_list()
    except ImportError:
        return ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen"]


def get_theme_info():
    """Get theme information - fallback if shared module not available"""
    try:
        from shared.style_manager import style_manager
        return style_manager.get_theme_info()
    except ImportError:
        return {
            "futuristic": {"name": "Futuristic"},
            "dark_clinic": {"name": "Dark Clinic"},
            "neon_clinic": {"name": "Neon Clinic"},
            "security": {"name": "Security"},
            "dark": {"name": "Dark"},
            "light": {"name": "Light"},
            "professional": {"name": "Professional"},
            "dacos": {"name": "Dacos"}
        }