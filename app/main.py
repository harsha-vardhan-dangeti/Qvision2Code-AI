from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import UI2JSONPipeline, load_image
from figma_routes import figma_router
import io
import uvicorn

# Create FastAPI app with custom settings
app = FastAPI(
    title="Vision2Code AI - UI Analysis & Figma Integration", 
    version="0.2.0",
    # Increase timeout for long-running operations
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include Figma router
app.include_router(figma_router)

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
    return {
        "ok": True, 
        "msg": "Vision2Code AI Backend",
        "endpoints": {
            "image_analysis": "POST /analyze with form-data: image=<file>",
            "figma_integration": "GET /figma/* for Figma API integration"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Vision2Code AI Backend"}
