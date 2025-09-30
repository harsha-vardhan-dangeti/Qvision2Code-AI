"""
Vision2Code AI - Main FastAPI Application
Simplified and optimized with proper error handling
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import logging
from typing import Dict, Any

# Import local modules
from .pipeline import UI2JSONPipeline, load_image
from .figma_routes import figma_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vision2Code AI - UI Analysis & Figma Integration", 
    version="1.0.0",
    description="AI-powered UI analysis and Figma integration service",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Figma router
app.include_router(figma_router)

# Initialize pipeline
try:
    pipeline = UI2JSONPipeline()
    logger.info("UI2JSONPipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize UI2JSONPipeline: {e}")
    pipeline = None

@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "ok": True, 
        "message": "Vision2Code AI Backend is running",
        "version": "1.0.0",
        "endpoints": {
            "image_analysis": "POST /analyze - Upload image for UI analysis",
            "figma_integration": "POST /figma/analyze - Analyze Figma files",
            "figma_preprocess": "POST /figma/preprocess - Preprocess Figma data",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        }
    }

@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint"""
    status = "healthy"
    pipeline_status = "ok" if pipeline else "error"
    
    return {
        "status": status,
        "service": "Vision2Code AI Backend",
        "version": "1.0.0",
        "pipeline": pipeline_status,
        "figma_service": "ok"
    }

@app.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...), 
    target: str = Form("web")
) -> JSONResponse:
    """
    Analyze an uploaded image and return structured JSON of UI components
    
    Args:
        image: Uploaded image file (PNG, JPG, etc.)
        target: Target platform (web, mobile, desktop)
    
    Returns:
        JSONResponse with analyzed UI components
    """
    try:
        # Validate pipeline
        if pipeline is None:
            raise HTTPException(
                status_code=500,
                detail="UI analysis pipeline is not available"
            )
        
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (PNG, JPG, etc.)"
            )
        
        # Read and process image
        content = await image.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        # Load and process image
        pil_img = load_image(io.BytesIO(content))
        ui_json = pipeline.process(pil_img, target=target)
        
        logger.info(f"Successfully analyzed image: {image.filename}")
        return JSONResponse(content=ui_json)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing image: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "message": "Check /docs for available endpoints"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Please try again later"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)