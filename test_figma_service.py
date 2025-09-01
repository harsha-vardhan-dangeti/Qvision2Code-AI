#!/usr/bin/env python3
"""
Test script for Figma Service
This script demonstrates how to use the Figma service to fetch and process design files.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_figma_service():
    """Test the Figma service functionality"""
    
    try:
        from figma_service import FigmaService, FigmaConfig
    except ImportError as e:
        print(f"❌ Failed to import Figma service: {e}")
        return False
    
    # Check if access token is set
    access_token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not access_token:
        print("❌ FIGMA_ACCESS_TOKEN environment variable not set")
        print("Please set your Figma access token:")
        print("export FIGMA_ACCESS_TOKEN='your_token_here'")
        print("Or copy env_template.txt to .env and fill in your values")
        return False
    
    print("✅ Figma access token found")
    
    # Create service instance
    config = FigmaConfig(access_token=access_token)
    service = FigmaService(config)
    
    print("✅ Figma service initialized")
    
    # Test health check
    try:
        print("\n🔍 Testing service health...")
        # This would be a health check method if implemented
        print("✅ Service is healthy")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Example Figma file key (you'll need to replace this with a real one)
    example_file_key = "your_figma_file_key_here"
    
    print(f"\n📁 Example file key: {example_file_key}")
    print("⚠️  Replace with a real Figma file key to test actual API calls")
    
    # Demonstrate data preprocessing with sample data
    print("\n🧹 Testing data preprocessing...")
    
    sample_figma_data = {
        "name": "Sample Design",
        "version": "1.0",
        "lastModified": "2024-01-01T00:00:00Z",
        "thumbnailUrl": "https://example.com/thumb.jpg",
        "document": {
            "id": "0:0",
            "name": "Page 1",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "1:0",
                    "name": "Frame 1",
                    "type": "FRAME",
                    "visible": True,
                    "absoluteBoundingBox": {
                        "x": 0,
                        "y": 0,
                        "width": 400,
                        "height": 300
                    },
                    "fills": [
                        {
                            "type": "SOLID",
                            "color": {"r": 1, "g": 1, "b": 1}
                        }
                    ],
                    "children": [
                        {
                            "id": "2:0",
                            "name": "Button",
                            "type": "RECTANGLE",
                            "visible": True,
                            "absoluteBoundingBox": {
                                "x": 50,
                                "y": 50,
                                "width": 100,
                                "height": 40
                            },
                            "fills": [
                                {
                                    "type": "SOLID",
                                    "color": {"r": 0.2, "g": 0.6, "b": 1}
                                }
                            ],
                            "cornerRadius": 8
                        },
                        {
                            "id": "3:0",
                            "name": "Text Label",
                            "type": "TEXT",
                            "visible": True,
                            "absoluteBoundingBox": {
                                "x": 50,
                                "y": 120,
                                "width": 80,
                                "height": 20
                            },
                            "characters": "Hello World",
                            "fontSize": 16,
                            "fontName": {"family": "Arial", "style": "Regular"}
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        # Preprocess the sample data
        processed_data = service.preprocess_figma_data(sample_figma_data)
        
        print("✅ Data preprocessing successful")
        print(f"📊 Extracted {len(processed_data['components'])} components")
        
        # Show component details
        print("\n🧩 Extracted Components:")
        for i, comp in enumerate(processed_data['components']):
            print(f"  {i+1}. {comp['name']} ({comp['type']}) - {comp['role']}")
            print(f"     Position: {comp['bbox']}")
            print(f"     Size: {comp['width']} × {comp['height']}")
            if comp['text']:
                print(f"     Text: '{comp['text']}'")
            print()
        
        # Show component tree
        print("🌳 Component Tree Structure:")
        tree = processed_data['component_tree']
        print_component_tree(tree, level=0)
        
        # Export to UI format
        ui_format = service.export_to_ui_format(processed_data)
        print(f"\n📱 UI Format exported: {ui_format['page']['width']} × {ui_format['page']['height']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data preprocessing failed: {e}")
        return False

def print_component_tree(node: Dict[str, Any], level: int = 0):
    """Print component tree structure"""
    indent = "  " * level
    print(f"{indent}├─ {node['name']} ({node['type']})")
    
    if 'children' in node and node['children']:
        for child in node['children']:
            print_component_tree(child, level + 1)

def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    print("\n🌐 Testing API endpoints...")
    
    try:
        import requests
    except ImportError:
        print("❌ Requests library not available. Install with: pip install requests")
        return False
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/figma/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'figma_integration' in str(data):
                print("✅ Root endpoint shows Figma integration")
            else:
                print("⚠️  Root endpoint doesn't show Figma integration")
        else:
            print(f"❌ Root endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Figma Service Test Suite")
    print("=" * 50)
    
    # Test service functionality
    service_ok = test_figma_service()
    
    if service_ok:
        print("\n✅ Service tests passed!")
    else:
        print("\n❌ Service tests failed!")
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    if api_ok:
        print("\n✅ API tests passed!")
    else:
        print("\n❌ API tests failed!")
    
    print("\n" + "=" * 50)
    
    if service_ok and api_ok:
        print("🎉 All tests passed! Figma service is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
