"""
Vision2Code AI - UI Layout Analysis Tool

A comprehensive tool for converting UI screenshots into structured JSON layouts
using computer vision, OCR, and AI techniques.
"""

__version__ = "0.1.0"
__author__ = "Vision2Code Team"

from .pipeline import UI2JSONPipeline, UI2JSON
from .schemas import make_empty_ui_json, add_component, normalize_bbox
from .utils import to_cv, to_pil, iou, merge_overlaps

__all__ = [
    "UI2JSONPipeline",
    "UI2JSON", 
    "make_empty_ui_json",
    "add_component",
    "normalize_bbox",
    "to_cv",
    "to_pil",
    "iou",
    "merge_overlaps"
]
