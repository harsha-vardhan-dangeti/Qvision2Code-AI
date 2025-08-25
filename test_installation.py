#!/usr/bin/env python3
"""
Test script to verify Vision2Code AI installation
"""

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import PIL
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test if the app package can be imported"""
    print("\n🔍 Testing app package imports...")
    
    try:
        from app import UI2JSONPipeline, UI2JSON
        print("✅ App package imported successfully")
    except ImportError as e:
        print(f"❌ App package import failed: {e}")
        return False
    
    return True

def test_web_imports():
    """Test if the web package can be imported"""
    print("\n🔍 Testing web package imports...")
    
    try:
        import web.ui_inspector
        print("✅ Web package imported successfully")
    except ImportError as e:
        print(f"❌ Web package import failed: {e}")
        return False
    
    return True

def test_optional_imports():
    """Test optional dependencies"""
    print("\n🔍 Testing optional dependencies...")
    
    # Test OCR
    try:
        import pytesseract
        print("✅ Tesseract OCR available")
    except ImportError:
        print("⚠️  Tesseract OCR not available (optional)")
    
    # Test YOLO
    try:
        import ultralytics
        print("✅ YOLO available")
    except ImportError:
        print("⚠️  YOLO not available (optional)")
    
    # Test matplotlib
    try:
        import matplotlib
        print("✅ Matplotlib available")
    except ImportError:
        print("⚠️  Matplotlib not available (optional)")

def main():
    """Main test function"""
    print("🔍 Vision2Code AI - Installation Test")
    print("=" * 50)
    
    # Test basic imports
    if not test_imports():
        print("\n❌ Basic dependencies test failed!")
        return False
    
    # Test app package
    if not test_app_imports():
        print("\n❌ App package test failed!")
        return False
    
    # Test web package
    if not test_web_imports():
        print("\n❌ Web package test failed!")
        return False
    
    # Test optional dependencies
    test_optional_imports()
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Vision2Code AI is ready to use.")
    print("\nTo start the application:")
    print("1. Run: python start_app.py")
    print("2. Or manually start backend: cd app && uvicorn main:app --reload")
    print("3. And frontend: cd web && streamlit run ui_inspector.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
