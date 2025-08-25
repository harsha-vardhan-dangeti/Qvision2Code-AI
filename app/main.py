from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pipeline import UI2JSONPipeline, load_image
import io

app = FastAPI(title="UI Image → JSON Layout API", version="0.1.0")

pipeline = UI2JSONPipeline()

@app.post("/analyze")
async def analyze(image: UploadFile = File(...), target: str = Form("web")):
    """Accept an image (screenshot) and return structured JSON of layout/components."""
    content = await image.read()
    pil_img = load_image(io.BytesIO(content))
    ui_json = pipeline.process(pil_img, target=target)
    return JSONResponse(content=ui_json)

@app.get("/")
def root():
    return {"ok": True, "msg": "POST /analyze with form-data: image=<file>"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Vision2Code AI Backend"}