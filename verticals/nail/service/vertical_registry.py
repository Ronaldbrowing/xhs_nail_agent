"""
Vertical Registry — manages available verticals and their configurations.

This module is kept for backward compatibility.
The canonical registry is now at src.vertical_registry.
"""
# Re-export from platform-level registry for backward compatibility
from src.vertical_registry import VerticalDefinition, VerticalRegistry

__all__ = ["VerticalDefinition", "VerticalRegistry"]
