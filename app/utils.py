from typing import List, Dict
import numpy as np
from PIL import Image
import cv2


def to_cv(img: Image.Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def to_pil(mat):
    return Image.fromarray(cv2.cvtColor(mat, cv2.COLOR_BGR2RGB))


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    iw = max(0, inter_x2 - inter_x1)
    ih = max(0, inter_y2 - inter_y1)
    inter = iw * ih
    area_a = (ax2-ax1) * (ay2-ay1)
    area_b = (bx2-bx1) * (by2-by1)
    union = area_a + area_b - inter
    return inter / max(union, 1e-6)


def merge_overlaps(detections: List[Dict], iou_thresh: float = 0.5, prefer_label_from: str = "yolo"):
    """Merge overlapping detections based on IoU threshold."""
    if not detections:
        return []
    
    # Sort by confidence (higher first)
    sorted_dets = sorted(detections, key=lambda x: x.get("conf", 0), reverse=True)
    merged = []
    
    for det in sorted_dets:
        should_merge = False
        for existing in merged:
            if iou(det["bbox"], existing["bbox"]) > iou_thresh:
                should_merge = True
                # Keep the one with higher confidence
                if det.get("conf", 0) > existing.get("conf", 0):
                    existing.update(det)
                break
        
        if not should_merge:
            merged.append(det.copy())
    
    return merged