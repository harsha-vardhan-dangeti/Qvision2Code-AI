"""
Figma Integration API Routes
Simplified and optimized for better performance and maintainability
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from .figma_service import FigmaService, FigmaConfig

# Configure logging
logger = logging.getLogger(__name__)

# Create router
figma_router = APIRouter(prefix="/figma", tags=["Figma Integration"])

# Request Models
class FigmaAnalysisRequest(BaseModel):
    """Request model for Figma file analysis"""
    file_key: str = Field(..., description="Figma file key from URL")
    node_ids: Optional[list] = Field(None, description="Specific node IDs to analyze")
    target_platform: str = Field(default="web", description="Target platform for analysis")
    llm_model: Optional[str] = Field(default="gpt-4o-mini", description="LLM model for preprocessing")

class FigmaPreprocessRequest(BaseModel):
    """Request model for preprocessing raw Figma data"""
    figma_data: Dict[str, Any] = Field(..., description="Raw Figma data to preprocess")
    llm_model: Optional[str] = Field(default="gpt-4o-mini", description="LLM model for preprocessing")
    llm_api_key: Optional[str] = Field(None, description="LLM API key (optional, uses env var if not provided)")

# Dependency to get Figma service
def get_figma_service(llm_model: str = "gpt-4o-mini", llm_api_key: Optional[str] = None) -> FigmaService:
    """Get configured Figma service instance"""
    access_token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(
            status_code=500,
            detail="FIGMA_ACCESS_TOKEN environment variable not set"
        )
    
    # Use provided API key or fall back to environment variable
    api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
    
    config = FigmaConfig(
        access_token=access_token,
        llm_model=llm_model,
        llm_api_key=api_key
    )
    return FigmaService(config)

@figma_router.post("/analyze")
async def analyze_figma_file(
    request: FigmaAnalysisRequest
) -> Dict[str, Any]:
    """
    Analyze a Figma file and return processed UI components using LLM
    
    This is the main endpoint for Figma file analysis with LLM-powered preprocessing.
    """
    try:
        logger.info(f"Analyzing Figma file: {request.file_key} with LLM model: {request.llm_model}")
        
        # Create Figma service with LLM configuration
        figma_service = get_figma_service(request.llm_model)
        
        # Get and process Figma file
        processed_data = figma_service.get_processed_figma_file(
            request.file_key, 
            request.node_ids
        )
        
        # Export to UI format
        ui_format = figma_service.export_to_ui_format(processed_data)
        
        return {
            "success": True,
            "message": f"Successfully analyzed Figma file with {len(ui_format['components'])} components using LLM",
            "ui_data": ui_format,
            "metadata": processed_data.get("metadata", {}),
            "component_tree": processed_data.get("component_tree", {}),
            "llm_info": {
                "model": request.llm_model,
                "processing_method": processed_data.get("metadata", {}).get("processing_method", "unknown")
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing Figma file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Figma file: {str(e)}"
        )

@figma_router.post("/preprocess")
async def preprocess_figma_data(
    request: FigmaPreprocessRequest
) -> Dict[str, Any]:
    """
    Preprocess raw Figma data using LLM
    
    This endpoint handles LLM-based preprocessing of raw Figma data.
    """
    try:
        figma_data = request.figma_data
        
        # Quick size check
        file_size_mb = len(json.dumps(figma_data)) / 1024 / 1024
        logger.info(f"Processing Figma file: {file_size_mb:.2f} MB with LLM model: {request.llm_model}")
        
        # Create Figma service instance with LLM configuration
        config = FigmaConfig(
            access_token="dummy",  # Not used for preprocessing
            llm_model=request.llm_model,
            llm_api_key=request.llm_api_key
        )
        figma_service = FigmaService(config)
        
        # LLM processing timeout (longer for API calls)
        timeout = 300.0  # 5 minutes for LLM processing
        
        logger.info(f"Using LLM timeout: {timeout} seconds")
        
        # Run LLM preprocessing with timeout
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:  # Single worker for LLM calls
            try:
                start_time = time.time()
                
                # LLM Preprocessing
                processed_data = await asyncio.wait_for(
                    loop.run_in_executor(
                        executor, 
                        figma_service.preprocess_figma_data, 
                        figma_data
                    ),
                    timeout=timeout
                )
                
                # Export to UI format
                ui_format = await asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        figma_service.export_to_ui_format,
                        processed_data
                    ),
                    timeout=60.0  # 1 minute for export
                )
                
                total_time = time.time() - start_time
                logger.info(f"Total LLM processing time: {total_time:.2f} seconds")
                
                return {
                    "success": True,
                    "message": f"Successfully preprocessed data with {len(ui_format['components'])} components using LLM",
                    "ui_data": ui_format,
                    "metadata": processed_data.get("metadata", {}),
                    "component_tree": processed_data.get("component_tree", {}),
                    "processing_info": {
                        "file_size_mb": round(file_size_mb, 2),
                        "processing_time_seconds": round(total_time, 2),
                        "total_components": len(ui_format.get("components", [])),
                        "llm_model": request.llm_model,
                        "processing_method": processed_data.get("metadata", {}).get("processing_method", "llm")
                    }
                }
                
            except asyncio.TimeoutError:
                logger.error(f"LLM preprocessing timed out after {timeout} seconds")
                raise HTTPException(
                    status_code=408,
                    detail=f"LLM preprocessing timed out after {timeout} seconds. File size: {file_size_mb:.1f} MB"
                )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error during LLM preprocessing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error preprocessing Figma data with LLM: {str(e)}"
        )

@figma_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for Figma service"""
    return {
        "success": True,
        "service": "figma",
        "status": "healthy",
        "message": "Figma service is running"
    }