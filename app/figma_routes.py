from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import os
import json
import logging
from figma_service import FigmaService, FigmaConfig

# Configure logging
logger = logging.getLogger(__name__)

# Create router
figma_router = APIRouter(prefix="/figma", tags=["Figma Integration"])

# Pydantic models for request/response
class FigmaFileRequest(BaseModel):
    file_key: str = Field(..., description="Figma file key from URL")
    node_ids: Optional[List[str]] = Field(None, description="Specific node IDs to fetch")
    target_platform: str = Field(default="web", description="Target platform for analysis")

class FigmaProjectRequest(BaseModel):
    project_id: str = Field(..., description="Figma project ID")
    target_platform: str = Field(default="web", description="Target platform for analysis")

class FigmaTeamRequest(BaseModel):
    team_id: str = Field(..., description="Figma team ID")
    target_platform: str = Field(default="web", description="Target platform for analysis")

class FigmaAnalysisRequest(BaseModel):
    file_key: str = Field(..., description="Figma file key")
    node_ids: Optional[List[str]] = Field(None, description="Specific node IDs to analyze")
    target_platform: str = Field(default="web", description="Target platform for analysis")
    include_raw: bool = Field(default=False, description="Include raw Figma data in response")
    include_tree: bool = Field(default=True, description="Include component tree structure")

# Dependency to get Figma service
def get_figma_service() -> FigmaService:
    """Get configured Figma service instance"""
    access_token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(
            status_code=500,
            detail="FIGMA_ACCESS_TOKEN environment variable not set"
        )
    
    config = FigmaConfig(access_token=access_token)
    return FigmaService(config)

@figma_router.post("/analyze")
async def analyze_figma_file(
    request: FigmaAnalysisRequest,
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Analyze a Figma file and return processed UI components
    
    This endpoint fetches data from Figma API, preprocesses it to remove verbose fields,
    and maintains the tree structure while extracting essential UI components.
    """
    try:
        # Get and process Figma file
        processed_data = figma_service.get_processed_figma_file(
            request.file_key, 
            request.node_ids
        )
        
        # Export to UI format
        ui_format = figma_service.export_to_ui_format(processed_data)
        
        # Prepare response
        response = {
            "success": True,
            "message": f"Successfully analyzed Figma file with {len(ui_format['components'])} components",
            "ui_data": ui_format,
            "metadata": processed_data.get("metadata", {})
        }
        
        # Include additional data if requested
        if request.include_raw:
            response["raw_figma_data"] = processed_data.get("document", {})
        
        if request.include_tree:
            response["component_tree"] = processed_data.get("component_tree", {})
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing Figma file: {str(e)}"
        )

@figma_router.get("/file/{file_key}")
async def get_figma_file(
    file_key: str,
    node_ids: Optional[str] = Query(None, description="Comma-separated node IDs"),
    target_platform: str = Query("web", description="Target platform"),
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get a Figma file and return processed data
    
    Query parameters:
    - node_ids: Comma-separated list of specific node IDs to fetch
    - target_platform: Target platform for analysis (web, mobile, desktop)
    """
    try:
        # Parse node IDs if provided
        parsed_node_ids = None
        if node_ids:
            parsed_node_ids = [nid.strip() for nid in node_ids.split(",")]
        
        # Get and process Figma file
        processed_data = figma_service.get_processed_figma_file(
            file_key, 
            parsed_node_ids
        )
        
        # Export to UI format
        ui_format = figma_service.export_to_ui_format(processed_data)
        
        return {
            "success": True,
            "file_key": file_key,
            "target_platform": target_platform,
            "ui_data": ui_format,
            "metadata": processed_data.get("metadata", {}),
            "component_tree": processed_data.get("component_tree", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Figma file: {str(e)}"
        )

@figma_router.get("/file/{file_key}/raw")
async def get_raw_figma_file(
    file_key: str,
    node_ids: Optional[str] = Query(None, description="Comma-separated node IDs"),
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get raw Figma file data without preprocessing
    
    This endpoint returns the raw data from Figma API for debugging purposes.
    """
    try:
        # Parse node IDs if provided
        parsed_node_ids = None
        if node_ids:
            parsed_node_ids = [nid.strip() for nid in node_ids.split(",")]
        
        # Get raw data
        raw_data = figma_service.get_file(file_key, parsed_node_ids)
        
        return {
            "success": True,
            "file_key": file_key,
            "raw_data": raw_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching raw Figma file: {str(e)}"
        )

@figma_router.get("/file/{file_key}/components")
async def get_figma_components(
    file_key: str,
    node_ids: Optional[str] = Query(None, description="Comma-separated node IDs"),
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get only the extracted UI components from a Figma file
    
    This endpoint returns just the processed components without the full UI data structure.
    """
    try:
        # Parse node IDs if provided
        parsed_node_ids = None
        if node_ids:
            parsed_node_ids = [nid.strip() for nid in node_ids.split(",")]
        
        # Get and process Figma file
        processed_data = figma_service.get_processed_figma_file(
            file_key, 
            parsed_node_ids
        )
        
        return {
            "success": True,
            "file_key": file_key,
            "components": processed_data.get("components", []),
            "total_components": len(processed_data.get("components", [])),
            "metadata": processed_data.get("metadata", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Figma components: {str(e)}"
        )

@figma_router.get("/file/{file_key}/tree")
async def get_figma_component_tree(
    file_key: str,
    node_ids: Optional[str] = Query(None, description="Comma-separated node IDs"),
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get the component tree structure from a Figma file
    
    This endpoint returns the hierarchical tree structure of components.
    """
    try:
        # Parse node IDs if provided
        parsed_node_ids = None
        if node_ids:
            parsed_node_ids = [nid.strip() for nid in node_ids.split(",")]
        
        # Get and process Figma file
        processed_data = figma_service.get_processed_figma_file(
            file_key, 
            parsed_node_ids
        )
        
        return {
            "success": True,
            "file_key": file_key,
            "component_tree": processed_data.get("component_tree", {}),
            "metadata": processed_data.get("metadata", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Figma component tree: {str(e)}"
        )

@figma_router.get("/project/{project_id}/files")
async def get_project_files(
    project_id: str,
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get all files in a Figma project
    """
    try:
        files_data = figma_service.get_project_files(project_id)
        
        return {
            "success": True,
            "project_id": project_id,
            "files": files_data.get("files", []),
            "total_files": len(files_data.get("files", []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching project files: {str(e)}"
        )

@figma_router.get("/team/{team_id}/projects")
async def get_team_projects(
    team_id: str,
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get all projects in a Figma team
    """
    try:
        projects_data = figma_service.get_team_projects(team_id)
        
        return {
            "success": True,
            "team_id": team_id,
            "projects": projects_data.get("projects", []),
            "total_projects": len(projects_data.get("projects", []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching team projects: {str(e)}"
        )

@figma_router.get("/team/{team_id}")
async def get_team_info(
    team_id: str,
    figma_service: FigmaService = Depends(get_figma_service)
) -> Dict[str, Any]:
    """
    Get team information
    """
    try:
        team_data = figma_service.get_team(team_id)
        
        return {
            "success": True,
            "team": team_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching team info: {str(e)}"
        )

@figma_router.post("/preprocess")
async def preprocess_figma_data(
    figma_data: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Preprocess raw Figma data with optimized processing
    
    This endpoint automatically detects file size and uses appropriate processing strategy
    to avoid timeouts and ensure successful processing.
    """
    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        # Quick size check before processing
        file_size_mb = len(json.dumps(figma_data)) / 1024 / 1024
        logger.info(f"Processing Figma file: {file_size_mb:.2f} MB")
        
        # Create a temporary Figma service instance for preprocessing
        config = FigmaConfig(access_token="dummy")  # Not used for preprocessing
        figma_service = FigmaService(config)
        
        # Adaptive timeout based on file size - More aggressive timeouts
        if file_size_mb > 100:  # Very large files
            timeout = 900.0  # 15 minutes
            logger.info("Very large file detected, using 15-minute timeout")
        elif file_size_mb > 50:  # Large files
            timeout = 600.0  # 10 minutes
            logger.info("Large file detected, using 10-minute timeout")
        elif file_size_mb > 25:  # Medium files
            timeout = 300.0  # 5 minutes
            logger.info("Medium file detected, using 5-minute timeout")
        else:  # Normal files
            timeout = 180.0  # 3 minutes
            logger.info("Normal file, using 3-minute timeout")
        
        # Run preprocessing with adaptive timeout
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:  # Increased workers
            try:
                start_time = time.time()
                
                # Preprocessing with progress logging
                logger.info("Starting preprocessing...")
                processed_data = await asyncio.wait_for(
                    loop.run_in_executor(
                        executor, 
                        figma_service.preprocess_figma_data, 
                        figma_data
                    ),
                    timeout=timeout
                )
                
                preprocessing_time = time.time() - start_time
                logger.info(f"Preprocessing completed in {preprocessing_time:.2f} seconds")
                
                # Export to UI format with shorter timeout
                logger.info("Exporting to UI format...")
                ui_format = await asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        figma_service.export_to_ui_format,
                        processed_data
                    ),
                    timeout=120.0  # 2 minutes for export
                )
                
                total_time = time.time() - start_time
                logger.info(f"Total processing time: {total_time:.2f} seconds")
                
                # Add processing info to response
                response = {
                    "success": True,
                    "message": f"Successfully preprocessed data with {len(ui_format['components'])} components",
                    "ui_data": ui_format,
                    "metadata": processed_data.get("metadata", {}),
                    "component_tree": processed_data.get("component_tree", {}),
                    "processing_info": {
                        "file_size_mb": round(file_size_mb, 2),
                        "processing_time_seconds": round(total_time, 2),
                        "processing_mode": processed_data.get("metadata", {}).get("processing_mode", "standard"),
                        "total_components": len(ui_format.get("components", []))
                    }
                }
                
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"Preprocessing timed out after {timeout} seconds")
                raise HTTPException(
                    status_code=408,
                    detail=f"Preprocessing timed out after {timeout} seconds. The file ({file_size_mb:.1f} MB) is very large. Try with a smaller file or specific node IDs."
                )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error during preprocessing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error preprocessing Figma data: {str(e)}"
        )

@figma_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for Figma service
    """
    return {
        "success": True,
        "service": "figma",
        "status": "healthy",
        "message": "Figma service is running"
    }
