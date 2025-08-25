import os
import json
import numpy as np
from PIL import Image
import cv2
from dotenv import load_dotenv
from schemas import make_empty_ui_json, add_component
from utils import to_cv, to_pil, merge_overlaps

load_dotenv()

USE_YOLO = os.getenv("UI2JSON_USE_YOLO", "false").lower() == "true"
USE_OCR  = os.getenv("UI2JSON_USE_OCR",  "true").lower() == "true"
USE_VLM  = os.getenv("UI2JSON_USE_VLM",  "false").lower() == "true"
YOLO_MODEL = os.getenv("YOLO_MODEL", "")

# Optional YOLO detector
try:
    if USE_YOLO:
        from ultralytics import YOLO
        yolo = YOLO(YOLO_MODEL) if YOLO_MODEL else YOLO("yolov8n.pt")  # fallback to generic
    else:
        yolo = None
except Exception:
    yolo = None

# Optional OCR
try:
    import pytesseract
except Exception:
    pytesseract = None

# Optional VLM refinement (OpenAI shown; similar for Anthropic)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if USE_VLM and OPENAI_KEY:
    import requests

UI_LABELS = [
    "navbar", "button", "link", "input", "textarea", "checkbox", "radio",
    "image", "icon", "logo", "card", "list", "table", "footer", "sidebar",
    "heading", "paragraph", "badge", "tab", "dropdown", "switch"
]


def load_image(fp):
    return Image.open(fp).convert("RGB")


def detect_rule_based(img: Image.Image):
    """Very simple geometric grouping baseline.
    Returns list of dicts: {bbox: [x1,y1,x2,y2], conf: float, label: str}
    """
    cv = to_cv(img)
    h, w = cv.shape[:2]
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thr = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 41, 7)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,3))
    morphed = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel, iterations=2)

    cnts, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    preds = []
    for c in cnts:
        x,y,wc,hc = cv2.boundingRect(c)
        if wc*hc < (w*h)*0.0005:  # skip tiny noise
            continue
        x1,y1,x2,y2 = x, y, x+wc, y+hc
        ar = wc / max(hc,1)
        # Coarse heuristics → labels
        if y1 < 0.12*h and ar > 5:
            label = "navbar"
        elif ar > 3 and hc < 0.15*h:
            label = "heading"
        elif hc > 0.2*h and ar < 2:
            label = "card"
        else:
            label = "block"
        preds.append({"bbox":[x1,y1,x2,y2], "conf":0.35, "label":label})

    preds = merge_overlaps(preds, iou_thresh=0.3)
    return preds


def detect_yolo(img: Image.Image):
    if yolo is None:
        return []
    res = yolo.predict(source=np.array(img)[:,:,::-1], verbose=False)
    out = []
    for r in res:
        for b in r.boxes:
            x1,y1,x2,y2 = b.xyxy[0].tolist()
            conf = float(b.conf[0])
            cls = int(b.cls[0])
            label = r.names.get(cls, "component")
            out.append({"bbox":[int(x1),int(y1),int(x2),int(y2)], "conf":conf, "label":label})
    return out


def ocr_text(img: Image.Image, boxes):
    if pytesseract is None:
        return {}
    texts = {}
    for i, b in enumerate(boxes):
        x1,y1,x2,y2 = map(int, b["bbox"])
        crop = img.crop((x1,y1,x2,y2))
        txt = pytesseract.image_to_string(crop, config='--psm 6').strip()
        if txt:
            texts[i] = txt
    return texts


def refine_with_vlm(img: Image.Image, components, page_size):
    if not (USE_VLM and OPENAI_KEY):
        return components
    sys = (
        "You convert UI detections into a clean JSON of components. "
        "Return strictly valid JSON with keys: id,type,bbox,text,role,children."
    )
    payload = {
        "page": {"width": page_size[0], "height": page_size[1]},
        "components": components,
        "ui_labels": UI_LABELS
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role":"system","content":sys},
            {"role":"user","content":json.dumps(payload)}
        ],
        "response_format": {"type":"json_object"}
    }
    try:
        import requests
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()["choices"][0]["message"]["content"]
        parsed = json.loads(data)
        return parsed.get("components", components)
    except Exception:
        return components


def assign_component_type(b):
    label = b.get("label", "block")
    if label in UI_LABELS:
        return label
    # Map generic boxes to common UI types using heuristics
    x1,y1,x2,y2 = b["bbox"]
    w = x2 - x1; h = y2 - y1
    ar = w / max(h,1)
    if ar > 4 and h < 80:
        return "navbar"
    if 30 <= h <= 70 and 80 <= w <= 220:
        return "button"
    if ar > 6 and 32 <= h <= 56:
        return "input"
    if h > 220 and ar < 2:
        return "card"
    return "block"


def process_detections(img: Image.Image, dets, texts):
    W, H = img.size
    ui = make_empty_ui_json(W, H)
    for idx, d in enumerate(dets):
        comp_id = f"comp_{idx+1}"
        ctype = assign_component_type(d)
        text = texts.get(idx, "") if isinstance(texts, dict) else ""
        add_component(ui, comp_id, ctype, d["bbox"], text)
    return ui


def merge_sources(d1, d2):
    boxes = d1 + d2
    return merge_overlaps(boxes, iou_thresh=0.5, prefer_label_from="yolo")


def to_detections(img: Image.Image):
    rb = detect_rule_based(img)
    yl = detect_yolo(img) if USE_YOLO else []
    if yl:
        return merge_sources(rb, yl)
    return rb


def UI2JSON(img: Image.Image):
    dets = to_detections(img)
    texts = ocr_text(img, dets) if USE_OCR else {}
    ui = process_detections(img, dets, texts)
    if USE_VLM:
        refined = refine_with_vlm(img, ui["components"], (ui["page"]["width"], ui["page"]["height"]))
        if isinstance(refined, list):
            ui["components"] = refined
    return ui

class UI2JSONPipeline:
    def __init__(self):
        pass
    def process(self, pil_img: Image.Image, target: str = "web"):
        return UI2JSON(pil_img)