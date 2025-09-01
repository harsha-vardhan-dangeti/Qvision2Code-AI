import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FigmaConfig:
    """Configuration for Figma API service"""
    access_token: str
    base_url: str = "https://api.figma.com/v1"
    timeout: int = 30
    max_retries: int = 3

class FigmaService:
    """Service for interacting with Figma API and preprocessing data"""
    
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
                    raise Exception(f"Failed to fetch data from Figma API after {self.config.max_retries} attempts: {e}")
                continue
    
    def get_file(self, file_key: str, node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch Figma file data"""
        params = {}
        if node_ids:
            params['ids'] = ','.join(node_ids)
        
        logger.info(f"Fetching Figma file: {file_key}")
        return self._make_request(f"files/{file_key}", params)
    
    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        """Fetch specific nodes from Figma file"""
        logger.info(f"Fetching nodes from Figma file: {file_key}")
        return self._make_request(f"files/{file_key}/nodes", {'ids': ','.join(node_ids)})
    
    def get_project_files(self, project_id: str) -> Dict[str, Any]:
        """Fetch all files in a project"""
        logger.info(f"Fetching project files: {project_id}")
        return self._make_request(f"projects/{project_id}/files")
    
    def get_team_projects(self, team_id: str) -> Dict[str, Any]:
        """Fetch all projects in a team"""
        logger.info(f"Fetching team projects: {team_id}")
        return self._make_request(f"teams/{team_id}/projects")
    
    def get_team(self, team_id: str) -> Dict[str, Any]:
        """Fetch team information"""
        logger.info(f"Fetching team: {team_id}")
        return self._make_request(f"teams/{team_id}")
    
    def _is_essential_field(self, key: str, value: Any) -> bool:
        """Determine if a field is essential for rendering"""
        essential_fields = {
            # Core identification
            'id', 'name', 'type', 'visible',
            
            # Layout and positioning
            'x', 'y', 'width', 'height', 'absoluteBoundingBox',
            'relativeTransform', 'constraints', 'layoutMode', 'layoutAlign',
            'layoutGrow', 'layoutSizing', 'paddingLeft', 'paddingRight',
            'paddingTop', 'paddingBottom', 'itemSpacing',
            
            # Visual properties
            'fills', 'strokes', 'strokeWeight', 'strokeAlign', 'cornerRadius',
            'effects', 'opacity', 'blendMode', 'isMask', 'fills',
            
            # Text properties
            'characters', 'style', 'fontSize', 'fontName', 'textAlignHorizontal',
            'textAlignVertical', 'textAutoResize', 'lineHeightPx', 'letterSpacing',
            
            # Component properties
            'componentId', 'componentProperties', 'componentSetId',
            
            # Auto layout
            'primaryAxisSizingMode', 'counterAxisSizingMode',
            'primaryAxisAlignItems', 'counterAxisAlignItems',
            
            # Constraints and responsive behavior
            'constraints', 'layoutSizingHorizontal', 'layoutSizingVertical',
            
            # Vector properties
            'vectorPaths', 'strokeCap', 'strokeJoin', 'dashPattern',
            
            # Effects and shadows
            'effects', 'blendMode', 'isMask', 'fills',
            
            # Children and hierarchy
            'children'
        }
        
        # Always include children for tree structure
        if key == 'children':
            return True
        
        # Include essential fields
        if key in essential_fields:
            return True
        
        # Include non-empty values for important fields
        if key in ['fills', 'strokes', 'effects'] and value:
            return True
        
        # Include component properties
        if key == 'componentProperties' and value:
            return True
        
        return False
    
    def _clean_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single node by removing verbose fields"""
        if not isinstance(node, dict):
            return node
        
        cleaned = {}
        
        for key, value in node.items():
            # Skip null/empty values
            if value is None or value == "":
                continue
            
            # Skip verbose metadata fields
            if key in ['createdAt', 'updatedAt', 'user', 'lastModified', 'thumbnailUrl']:
                continue
            
            # Skip empty arrays
            if isinstance(value, list) and len(value) == 0:
                continue
            
            # Skip empty objects
            if isinstance(value, dict) and len(value) == 0:
                continue
            
            # Process children recursively
            if key == 'children' and isinstance(value, list):
                cleaned_children = [self._clean_node(child) for child in value if child is not None]
                if cleaned_children:
                    cleaned[key] = cleaned_children
                continue
            
            # Process nested objects
            if isinstance(value, dict):
                cleaned_value = self._clean_node(value)
                if cleaned_value:
                    cleaned[key] = cleaned_value
                continue
            
            # Include essential fields
            if self._is_essential_field(key, value):
                cleaned[key] = value
        
        return cleaned
    
    def _extract_ui_components(self, node: Dict[str, Any], components: List[Dict[str, Any]]) -> None:
        """Extract UI components from Figma nodes"""
        if not isinstance(node, dict):
            return
        
        # Extract component if it's a UI element
        if self._is_ui_component(node):
            component = self._create_component_from_node(node)
            if component:
                components.append(component)
        
        # Process children recursively
        children = node.get('children', [])
        for child in children:
            self._extract_ui_components(child, components)
    
    def _is_ui_component(self, node: Dict[str, Any]) -> bool:
        """Determine if a node is a UI component"""
        node_type = node.get('type', '')
        
        # UI component types
        ui_types = {
            'FRAME', 'GROUP', 'COMPONENT', 'COMPONENT_SET', 'INSTANCE',
            'RECTANGLE', 'ELLIPSE', 'POLYGON', 'STAR', 'VECTOR',
            'TEXT', 'LINE', 'BOOLEAN_OPERATION', 'VECTOR'
        }
        
        return node_type in ui_types
    
    def _create_component_from_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a standardized component from Figma node"""
        try:
            # Get bounding box
            bbox = node.get('absoluteBoundingBox', {})
            if not bbox:
                return None
            
            # Extract text content
            text_content = ""
            if node.get('type') == 'TEXT':
                text_content = node.get('characters', '')
            elif 'characters' in node:
                text_content = node.get('characters', '')
            
            # Determine component type
            component_type = self._map_figma_type_to_component_type(node.get('type', ''))
            
            # Create component
            component = {
                'id': node.get('id', ''),
                'type': component_type,
                'name': node.get('name', ''),
                'text': text_content,
                'bbox': [
                    bbox.get('x', 0),
                    bbox.get('y', 0),
                    bbox.get('x', 0) + bbox.get('width', 0),
                    bbox.get('y', 0) + bbox.get('height', 0)
                ],
                'width': bbox.get('width', 0),
                'height': bbox.get('height', 0),
                'role': self._determine_component_role(node),
                'properties': self._extract_component_properties(node)
            }
            
            return component
            
        except Exception as e:
            logger.error(f"Error creating component from node: {e}")
            return None
    
    def _map_figma_type_to_component_type(self, figma_type: str) -> str:
        """Map Figma node types to component types"""
        type_mapping = {
            'FRAME': 'container',
            'GROUP': 'group',
            'COMPONENT': 'component',
            'COMPONENT_SET': 'component_set',
            'INSTANCE': 'instance',
            'RECTANGLE': 'rectangle',
            'ELLIPSE': 'ellipse',
            'POLYGON': 'polygon',
            'STAR': 'star',
            'VECTOR': 'vector',
            'TEXT': 'text',
            'LINE': 'line',
            'BOOLEAN_OPERATION': 'boolean_operation',
            'SLICE': 'slice',
            'IMAGE': 'image'
        }
        
        return type_mapping.get(figma_type, 'unknown')
    
    def _determine_component_role(self, node: Dict[str, Any]) -> str:
        """Determine the role of a component based on its properties"""
        name = node.get('name', '').lower()
        
        # Common UI component roles
        if any(keyword in name for keyword in ['button', 'btn']):
            return 'button'
        elif any(keyword in name for keyword in ['input', 'textfield', 'field']):
            return 'input'
        elif any(keyword in name for keyword in ['label', 'text']):
            return 'label'
        elif any(keyword in name for keyword in ['header', 'title', 'heading']):
            return 'heading'
        elif any(keyword in name for keyword in ['nav', 'navigation', 'menu']):
            return 'navigation'
        elif any(keyword in name for keyword in ['card', 'panel', 'container']):
            return 'container'
        elif any(keyword in name for keyword in ['icon', 'image', 'img']):
            return 'icon'
        else:
            return 'element'
    
    def _extract_component_properties(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant component properties"""
        properties = {}
        
        # Visual properties
        if 'fills' in node and node['fills']:
            properties['fills'] = node['fills']
        
        if 'strokes' in node and node['strokes']:
            properties['strokes'] = node['strokes']
        
        if 'effects' in node and node['effects']:
            properties['effects'] = node['effects']
        
        if 'cornerRadius' in node:
            properties['cornerRadius'] = node['cornerRadius']
        
        if 'opacity' in node:
            properties['opacity'] = node['opacity']
        
        # Layout properties
        if 'constraints' in node:
            properties['constraints'] = node['constraints']
        
        if 'layoutMode' in node:
            properties['layoutMode'] = node['layoutMode']
        
        # Text properties
        if node.get('type') == 'TEXT':
            if 'fontSize' in node:
                properties['fontSize'] = node['fontSize']
            if 'fontName' in node:
                properties['fontName'] = node['fontName']
            if 'textAlignHorizontal' in node:
                properties['textAlignHorizontal'] = node['textAlignHorizontal']
        
        return properties
    
    def preprocess_figma_data(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess Figma data to extract essential information with optimizations"""
        logger.info("Starting optimized Figma data preprocessing...")
        
        try:
            # Quick validation and size check
            file_size = len(json.dumps(figma_data))
            logger.info(f"Raw data size: {file_size / 1024 / 1024:.2f} MB")
            
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                logger.warning("Very large file detected, using aggressive chunked processing")
                return self._process_very_large_file(figma_data)
            elif file_size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning("Large file detected, using chunked processing")
                return self._process_file_optimized(figma_data)
            elif file_size > 25 * 1024 * 1024:  # 25MB limit
                logger.info("Medium file detected, using optimized processing")
                return self._process_file_optimized(figma_data)
            else:  # Normal files
                logger.info("Normal file, using standard processing")
                return self._process_file_optimized(figma_data)
            
        except Exception as e:
            logger.error(f"Error preprocessing Figma data: {e}")
            raise
    
    def _process_file_optimized(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized processing for normal-sized files"""
        logger.info("Using optimized processing...")
        
        # Extract only essential data first
        essential_data = self._extract_essential_data(figma_data)
        
        # Process in smaller batches
        components = []
        self._extract_ui_components_batched(essential_data, components, batch_size=100)
        
        # Build simplified component tree
        component_tree = self._build_simplified_tree(essential_data.get('document', {}))
        
        processed_data = {
            'metadata': {
                'source': 'figma',
                'processed_at': datetime.now().isoformat(),
                'total_components': len(components),
                'processing_mode': 'optimized',
                'file_info': {
                    'name': figma_data.get('name', 'Unknown'),
                    'lastModified': figma_data.get('lastModified', ''),
                    'version': figma_data.get('version', ''),
                    'thumbnailUrl': figma_data.get('thumbnailUrl', '')
                }
            },
            'document': essential_data.get('document', {}),
            'components': components,
            'component_tree': component_tree
        }
        
        logger.info(f"Optimized preprocessing completed. Extracted {len(components)} components.")
        return processed_data
    
    def _process_very_large_file(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggressive processing for very large files (>100MB)"""
        logger.info("Using aggressive processing for very large file...")
        
        # Extract only top-level essential data with minimal depth
        essential_data = self._extract_essential_data(figma_data, max_depth=2)
        
        # Process components in very small chunks
        components = []
        self._extract_ui_components_chunked(essential_data, components, chunk_size=25)
        
        # Build minimal component tree
        component_tree = self._build_minimal_tree(essential_data.get('document', {}))
        
        processed_data = {
            'metadata': {
                'source': 'figma',
                'processed_at': datetime.now().isoformat(),
                'total_components': len(components),
                'processing_mode': 'aggressive',
                'file_info': {
                    'name': figma_data.get('name', 'Unknown'),
                    'lastModified': figma_data.get('lastModified', ''),
                    'version': figma_data.get('version', ''),
                    'thumbnailUrl': figma_data.get('thumbnailUrl', '')
                }
            },
            'document': essential_data.get('document', {}),
            'components': components,
            'component_tree': component_tree
        }
        
        logger.info(f"Aggressive preprocessing completed. Extracted {len(components)} components.")
        return processed_data
    
    def _process_large_file_chunked(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Chunked processing for large files (50-100MB)"""
        logger.info("Using chunked processing for large file...")
        
        # Extract only top-level essential data
        essential_data = self._extract_essential_data(figma_data, max_depth=3)
        
        # Process components in chunks
        components = []
        self._extract_ui_components_chunked(essential_data, components, chunk_size=50)
        
        # Build minimal component tree
        component_tree = self._build_minimal_tree(essential_data.get('document', {}))
        
        processed_data = {
            'metadata': {
                'source': 'figma',
                'processed_at': datetime.now().isoformat(),
                'total_components': len(components),
                'processing_mode': 'chunked',
                'file_info': {
                    'name': figma_data.get('name', 'Unknown'),
                    'lastModified': figma_data.get('lastModified', ''),
                    'version': figma_data.get('version', ''),
                    'thumbnailUrl': figma_data.get('thumbnailUrl', '')
                }
            },
            'document': essential_data.get('document', {}),
            'components': components,
            'component_tree': component_tree
        }
        
        logger.info(f"Chunked preprocessing completed. Extracted {len(components)} components.")
        return processed_data
    
    def _extract_essential_data(self, figma_data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """Extract only essential data to reduce processing time"""
        logger.info(f"Extracting essential data (max depth: {max_depth})...")
        
        def clean_node_essential(node, depth=0):
            if depth > max_depth or not isinstance(node, dict):
                return None
            
            # Keep only essential fields
            essential_fields = {
                'id', 'name', 'type', 'visible', 'absoluteBoundingBox',
                'characters', 'children'
            }
            
            cleaned = {}
            for key in essential_fields:
                if key in node:
                    if key == 'children' and isinstance(node[key], list):
                        # Process children with depth limit and size limit
                        children = []
                        max_children = 50 if max_depth <= 2 else 100  # Limit children for very large files
                        for child in node[key][:max_children]:
                            child_cleaned = clean_node_essential(child, depth + 1)
                            if child_cleaned:
                                children.append(child_cleaned)
                        if children:
                            cleaned[key] = children
                    else:
                        cleaned[key] = node[key]
            
            return cleaned if cleaned else None
        
        # Clean the document structure
        if 'document' in figma_data:
            cleaned_doc = clean_node_essential(figma_data['document'])
            if cleaned_doc:
                return {'document': cleaned_doc}
        
        return {'document': {}}
    
    def _extract_ui_components_batched(self, essential_data: Dict[str, Any], components: List, batch_size: int = 100):
        """Extract UI components in batches to avoid timeouts"""
        logger.info(f"Extracting UI components in batches of {batch_size}...")
        
        def process_node_batch(nodes, batch_num):
            batch_components = []
            for i, node in enumerate(nodes):
                if i >= batch_size:
                    break
                
                if self._is_ui_component(node):
                    component = self._create_component_from_node_optimized(node)
                    if component:
                        batch_components.append(component)
                
                # Process children if available
                if 'children' in node and isinstance(node['children'], list):
                    batch_components.extend(process_node_batch(node['children'], batch_num + 1))
            
            return batch_components
        
        document = essential_data.get('document', {})
        if 'children' in document:
            batch_components = process_node_batch(document['children'], 1)
            components.extend(batch_components)
        
        logger.info(f"Batch processing completed. Total components: {len(components)}")
    
    def _extract_ui_components_chunked(self, essential_data: Dict[str, Any], components: List, chunk_size: int = 50):
        """Chunked processing for very large files"""
        logger.info(f"Using chunked processing (chunk size: {chunk_size})...")
        
        def process_chunk(nodes, chunk_num):
            chunk_components = []
            start_idx = chunk_num * chunk_size
            end_idx = start_idx + chunk_size
            
            for node in nodes[start_idx:end_idx]:
                if self._is_ui_component(node):
                    component = self._create_component_from_node_optimized(node)
                    if component:
                        chunk_components.append(component)
            
            return chunk_components
        
        document = essential_data.get('document', {})
        if 'children' in document:
            children = document['children']
            total_chunks = (len(children) + chunk_size - 1) // chunk_size
            
            logger.info(f"Processing {len(children)} nodes in {total_chunks} chunks...")
            
            for chunk_num in range(total_chunks):
                chunk_components = process_chunk(children, chunk_num)
                components.extend(chunk_components)
                logger.info(f"Processed chunk {chunk_num + 1}/{total_chunks} - Total components so far: {len(components)}")
                
                # Add a small delay to prevent overwhelming the system
                if chunk_num % 5 == 0 and chunk_num > 0:
                    import time
                    time.sleep(0.1)  # 100ms delay every 5 chunks
        
        logger.info(f"Chunked processing completed. Total components: {len(components)}")
    
    def _create_component_from_node_optimized(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimized component creation with minimal processing"""
        try:
            # Get bounding box
            bbox = node.get('absoluteBoundingBox', {})
            if not bbox:
                return None
            
            # Extract text content (simplified)
            text_content = ""
            if node.get('type') == 'TEXT' and 'characters' in node:
                text_content = node.get('characters', '')[:200]  # Limit text length
            
            # Create minimal component
            component = {
                'id': node.get('id', ''),
                'type': self._map_figma_type_to_component_type(node.get('type', '')),
                'name': node.get('name', '')[:100],  # Limit name length
                'text': text_content,
                'bbox': [
                    bbox.get('x', 0),
                    bbox.get('y', 0),
                    bbox.get('x', 0) + bbox.get('width', 0),
                    bbox.get('y', 0) + bbox.get('height', 0)
                ],
                'width': bbox.get('width', 0),
                'height': bbox.get('height', 0),
                'role': self._determine_component_role_simple(node)
            }
            
            return component
            
        except Exception as e:
            logger.warning(f"Error creating component from node: {e}")
            return None
    
    def _determine_component_role_simple(self, node: Dict[str, Any]) -> str:
        """Simplified role determination"""
        name = node.get('name', '').lower()[:50]  # Limit name length
        
        # Quick role mapping
        if any(keyword in name for keyword in ['button', 'btn']):
            return 'button'
        elif any(keyword in name for keyword in ['input', 'field']):
            return 'input'
        elif any(keyword in name for keyword in ['text', 'label']):
            return 'text'
        else:
            return 'element'
    
    def _build_simplified_tree(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Build simplified component tree"""
        if not document or not isinstance(document, dict):
            return {}
        
        def build_simple_tree(node, depth=0):
            if depth > 3 or not isinstance(node, dict):  # Limit depth
                return None
            
            tree_node = {
                'id': node.get('id', ''),
                'name': node.get('name', '')[:50],  # Limit name length
                'type': node.get('type', ''),
                'visible': node.get('visible', True)
            }
            
            # Add bounding box if available
            bbox = node.get('absoluteBoundingBox')
            if bbox:
                tree_node['bbox'] = {
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0),
                    'width': bbox.get('width', 0),
                    'height': bbox.get('height', 0)
                }
            
            # Process children (limit to first 20)
            children = node.get('children', [])[:20]
            if children:
                tree_children = []
                for child in children:
                    child_tree = build_simple_tree(child, depth + 1)
                    if child_tree:
                        tree_children.append(child_tree)
                
                if tree_children:
                    tree_node['children'] = tree_children
            
            return tree_node
        
        return build_simple_tree(document)
    
    def _build_minimal_tree(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Build minimal component tree for large files"""
        if not document or not isinstance(document, dict):
            return {}
        
        def build_minimal_tree(node, depth=0):
            if depth > 2 or not isinstance(node, dict):  # Very limited depth
                return None
            
            tree_node = {
                'id': node.get('id', ''),
                'name': node.get('name', '')[:30],  # Very short names
                'type': node.get('type', ''),
                'visible': node.get('visible', True)
            }
            
            # Process only first 10 children
            children = node.get('children', [])[:10]
            if children and depth < 2:
                tree_children = []
                for child in children:
                    child_tree = build_minimal_tree(child, depth + 1)
                    if child_tree:
                        tree_children.append(child_tree)
                
                if tree_children:
                    tree_node['children'] = tree_children
            
            return tree_node
        
        return build_minimal_tree(document)
    
    def _build_component_tree(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Build a simplified component tree structure"""
        if not document or not isinstance(document, dict):
            return {}
        
        def build_tree(node):
            if not isinstance(node, dict):
                return None
            
            tree_node = {
                'id': node.get('id', ''),
                'name': node.get('name', ''),
                'type': node.get('type', ''),
                'visible': node.get('visible', True)
            }
            
            # Add bounding box if available
            bbox = node.get('absoluteBoundingBox')
            if bbox:
                tree_node['bbox'] = {
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0),
                    'width': bbox.get('width', 0),
                    'height': bbox.get('height', 0)
                }
            
            # Process children
            children = node.get('children', [])
            if children:
                tree_children = []
                for child in children:
                    child_tree = build_tree(child)
                    if child_tree:
                        tree_children.append(child_tree)
                
                if tree_children:
                    tree_node['children'] = tree_children
            
            return tree_node
        
        return build_tree(document)
    
    def get_processed_figma_file(self, file_key: str, node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get and preprocess a Figma file"""
        try:
            # Fetch raw data
            raw_data = self.get_file(file_key, node_ids)
            
            # Preprocess the data
            processed_data = self.preprocess_figma_data(raw_data)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing Figma file {file_key}: {e}")
            raise
    
    def export_to_ui_format(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export processed data to UI rendering format"""
        try:
            components = processed_data.get('components', [])
            
            # Convert to UI format
            ui_format = {
                'page': {
                    'width': self._get_page_dimensions(processed_data, 'width'),
                    'height': self._get_page_dimensions(processed_data, 'height')
                },
                'components': components,
                'metadata': {
                    'source': 'figma',
                    'total_components': len(components),
                    'exported_at': datetime.now().isoformat()
                }
            }
            
            return ui_format
            
        except Exception as e:
            logger.error(f"Error exporting to UI format: {e}")
            raise
    
    def _get_page_dimensions(self, processed_data: Dict[str, Any], dimension: str) -> int:
        """Get page dimensions from processed data"""
        document = processed_data.get('document', {})
        
        # Try to get from document
        if document and 'absoluteBoundingBox' in document:
            bbox = document['absoluteBoundingBox']
            if dimension in bbox:
                return bbox[dimension]
        
        # Try to get from components
        components = processed_data.get('components', [])
        if components:
            max_dim = 0
            for comp in components:
                if dimension == 'width':
                    max_dim = max(max_dim, comp.get('width', 0))
                elif dimension == 'height':
                    max_dim = max(max_dim, comp.get('height', 0))
            return max_dim
        
        return 800  # Default fallback
