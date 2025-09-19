"""
Figma Service - LLM-Powered Preprocessing
Handles Figma API interactions and LLM-based data preprocessing
"""

import requests
import json
import time
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class FigmaConfig:
    """Configuration for Figma API service"""
    access_token: str
    base_url: str = "https://api.figma.com/v1"
    timeout: int = 30
    max_retries: int = 3
    llm_provider: str = "openai"  # openai, anthropic, or local
    llm_model: str = "gpt-4o-mini"
    llm_api_key: Optional[str] = None

class FigmaService:
    """Simplified service for Figma API interactions and data preprocessing"""
    
    def __init__(self, config: FigmaConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-Figma-Token': config.access_token,
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Figma API"""
        url = f"{self.config.base_url}/{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"Failed to fetch data from Figma API: {e}")
                time.sleep(1)  # Wait before retry
    
    def get_file(self, file_key: str, node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch Figma file data"""
        params = {}
        if node_ids:
            params['ids'] = ','.join(node_ids)
        
        logger.info(f"Fetching Figma file: {file_key}")
        return self._make_request(f"files/{file_key}", params)
    
    def get_processed_figma_file(self, file_key: str, node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get and preprocess Figma file data"""
        raw_data = self.get_file(file_key, node_ids)
        return self.preprocess_figma_data(raw_data)
    
    def preprocess_figma_data(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess Figma data using LLM for intelligent extraction"""
        logger.info("Starting LLM-based Figma data preprocessing...")
        
        try:
            # Use LLM to preprocess the data
            llm_result = self._preprocess_with_llm(figma_data)
            
            return {
                "document": llm_result.get("document", {}),
                "components": llm_result.get("components", []),
                "component_tree": llm_result.get("component_tree", {}),
                "metadata": {
                    "name": figma_data.get("name", "Unknown"),
                    "lastModified": figma_data.get("lastModified", ""),
                    "version": figma_data.get("version", ""),
                    "thumbnailUrl": figma_data.get("thumbnailUrl", ""),
                    "total_components": len(llm_result.get("components", [])),
                    "processing_time": time.time(),
                    "processing_method": "llm",
                    "llm_model": self.config.llm_model
                }
            }
            
        except Exception as e:
            logger.error(f"Error in LLM preprocessing: {e}")
            # Fallback to basic preprocessing if LLM fails
            logger.info("Falling back to basic preprocessing...")
            return self._fallback_preprocessing(figma_data)
    
    def _preprocess_with_llm(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to preprocess Figma data intelligently"""
        logger.info(f"Using LLM ({self.config.llm_model}) for preprocessing...")
        
        # Get API key from config or environment
        api_key = self.config.llm_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("LLM API key not provided. Set OPENAI_API_KEY environment variable or configure in FigmaConfig.")
        
        # Prepare the prompt for LLM
        prompt = self._create_preprocessing_prompt(figma_data)
        
        # Call LLM API
        if self.config.llm_provider.lower() == "openai":
            return self._call_openai_api(prompt, api_key)
        else:
            raise Exception(f"LLM provider '{self.config.llm_provider}' not supported yet. Use 'openai'.")
    
    def _create_preprocessing_prompt(self, figma_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for LLM preprocessing"""
        
        # Sample the data to avoid token limits (keep it under 50KB)
        sampled_data = self._sample_figma_data(figma_data)
        
        prompt = f"""
You are an expert UI/UX analyst specializing in Figma design data preprocessing. Your task is to analyze raw Figma JSON data and extract structured, clean information for UI component generation.

**Instructions:**
1. Analyze the provided Figma data and extract all UI components
2. Identify component types (button, input, text, container, image, etc.)
3. Extract positioning, styling, and text content
4. Build a hierarchical component tree
5. Remove verbose/unnecessary fields
6. Return ONLY valid JSON in the exact format specified below

**Input Data:**
{json.dumps(sampled_data, indent=2)}

**Required Output Format:**
{{
  "document": {{
    "id": "document_id",
    "name": "document_name",
    "type": "DOCUMENT",
    "children": [...]
  }},
  "components": [
    {{
      "id": "component_id",
      "name": "component_name", 
      "type": "button|input|text|container|image|icon|etc",
      "visible": true,
      "bbox": {{"x": 0, "y": 0, "width": 100, "height": 50}},
      "text": "component_text_content",
      "style": {{"fontSize": 16, "color": "#000000"}},
      "parent_id": "parent_component_id"
    }}
  ],
  "component_tree": {{
    "id": "root_id",
    "name": "root_name",
    "type": "container",
    "children": [...]
  }}
}}

**Component Type Guidelines:**
- button: Clickable elements with button-like appearance
- input: Text input fields, form controls
- text: Text labels, headings, paragraphs
- container: Frames, groups, layout containers
- image: Image elements, photos, graphics
- icon: Small graphical elements, symbols
- navbar: Navigation bars, headers
- card: Card-like containers with content
- list: List items, menu items
- modal: Popup dialogs, overlays

**Important:**
- Return ONLY the JSON response, no additional text
- Ensure all component IDs are unique
- Include proper parent-child relationships
- Extract all visible text content
- Preserve layout positioning and dimensions
- Focus on components that would be rendered in a UI
"""
        
        return prompt
    
    def _sample_figma_data(self, figma_data: Dict[str, Any], max_size: int = 50000) -> Dict[str, Any]:
        """Sample Figma data to stay within token limits"""
        data_str = json.dumps(figma_data)
        
        if len(data_str) <= max_size:
            return figma_data
        
        # If too large, sample the document structure
        sampled = {
            "name": figma_data.get("name", ""),
            "lastModified": figma_data.get("lastModified", ""),
            "version": figma_data.get("version", ""),
            "document": self._sample_document(figma_data.get("document", {}), max_size // 2)
        }
        
        return sampled
    
    def _sample_document(self, document: Dict[str, Any], max_size: int) -> Dict[str, Any]:
        """Sample document to fit within size limits"""
        if not document:
            return {}
        
        # Keep essential fields
        sampled = {
            "id": document.get("id", ""),
            "name": document.get("name", ""),
            "type": document.get("type", ""),
            "children": []
        }
        
        # Sample children (limit to first 20 to avoid size issues)
        children = document.get("children", [])[:20]
        for child in children:
            child_str = json.dumps(child)
            if len(json.dumps(sampled)) + len(child_str) < max_size:
                sampled["children"].append(child)
            else:
                break
        
        return sampled
    
    def _call_openai_api(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Call OpenAI API for preprocessing"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.llm_model,
            "messages": [
                {"role": "system", "content": "You are an expert UI/UX analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            return json.loads(content)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise Exception(f"LLM API call failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise Exception(f"LLM returned invalid JSON: {e}")
    
    def _fallback_preprocessing(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback preprocessing when LLM fails"""
        logger.info("Using fallback preprocessing...")
        
        document = figma_data.get("document", {})
        
        return {
            "document": document,
            "components": [],
            "component_tree": {},
            "metadata": {
                "name": figma_data.get("name", "Unknown"),
                "lastModified": figma_data.get("lastModified", ""),
                "version": figma_data.get("version", ""),
                "thumbnailUrl": figma_data.get("thumbnailUrl", ""),
                "total_components": 0,
                "processing_time": time.time(),
                "processing_method": "fallback",
                "error": "LLM preprocessing failed, using fallback"
            }
        }
    
    def export_to_ui_format(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export processed data to UI format"""
        components = processed_data.get("components", [])
        
        # Convert to UI format
        ui_components = []
        for comp in components:
            bbox = comp.get("bbox", {})
            ui_comp = {
                "id": comp.get("id", ""),
                "type": comp.get("type", "unknown"),
                "name": comp.get("name", ""),
                "bbox": [
                    bbox.get("x", 0),
                    bbox.get("y", 0),
                    bbox.get("x", 0) + bbox.get("width", 0),
                    bbox.get("y", 0) + bbox.get("height", 0)
                ],
                "text": comp.get("text", ""),
                "visible": comp.get("visible", True),
                "style": comp.get("style", {}),
                "children": []
            }
            ui_components.append(ui_comp)
        
        return {
            "page": {
                "width": 1920,  # Default page width
                "height": 1080  # Default page height
            },
            "components": ui_components
        }