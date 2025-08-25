from typing import Dict, Any

def make_empty_ui_json(w: int, h: int) -> Dict[str, Any]:
    return {
        "page": {"width": int(w), "height": int(h)},
        "components": []
    }

def normalize_bbox(bbox):
    x1,y1,x2,y2 = bbox
    return [int(x1), int(y1), int(x2), int(y2)]

def add_component(ui: Dict[str, Any], comp_id: str, ctype: str, bbox, text: str = "", role: str = ""):
    ui["components"].append({
        "id": comp_id,
        "type": ctype,
        "role": role,
        "bbox": normalize_bbox(bbox),
        "text": text,
        "children": []
    })