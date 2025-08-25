import streamlit as st
import requests
import json
import io
from PIL import Image
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np

# Configure the page
st.set_page_config(
    page_title="Vision2Code - UI Inspector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 1rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .component-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 Vision2Code UI Inspector</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload UI screenshots and get structured JSON layout analysis</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    # API endpoint configuration
    api_endpoint = st.sidebar.text_input(
        "API Endpoint",
        value="http://localhost:8000",
        help="FastAPI server endpoint"
    )
    
    # Target platform selection
    target_platform = st.sidebar.selectbox(
        "Target Platform",
        options=["web", "mobile", "desktop"],
        index=0,
        help="Select the target platform for analysis"
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📤 Upload Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload a UI screenshot or image to analyze"
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Analyze button
            if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    try:
                        # Prepare the image for API call
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        # Make API call
                        files = {"image": ("image.png", img_byte_arr, "image/png")}
                        data = {"target": target_platform}
                        
                        response = requests.post(
                            f"{api_endpoint}/analyze",
                            files=files,
                            data=data,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.analysis_result = result
                            st.session_state.original_image = image
                            st.success("✅ Analysis completed successfully!")
                        else:
                            st.error(f"❌ API Error: {response.status_code} - {response.text}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API server. Make sure the FastAPI server is running.")
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'analysis_result' in st.session_state and 'original_image' in st.session_state:
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.subheader("📊 Analysis Results")
            
            result = st.session_state.analysis_result
            original_image = st.session_state.original_image
            
            # Display page information
            if "page" in result:
                page_info = result["page"]
                st.info(f"📏 Page Dimensions: {page_info.get('width', 'N/A')} × {page_info.get('height', 'N/A')} pixels")
            
            # Display components count
            components = result.get("components", [])
            st.success(f"🎯 Detected {len(components)} UI components")
            
            # Display components list
            if components:
                st.subheader("🔍 Detected Components")
                
                for i, comp in enumerate(components):
                    with st.expander(f"Component {i+1}: {comp.get('type', 'unknown')} (ID: {comp.get('id', 'N/A')})"):
                        col_a, col_b = st.columns([1, 1])
                        
                        with col_a:
                            st.write(f"**Type:** {comp.get('type', 'N/A')}")
                            st.write(f"**Role:** {comp.get('role', 'N/A')}")
                            st.write(f"**Text:** {comp.get('text', 'N/A')}")
                        
                        with col_b:
                            bbox = comp.get('bbox', [])
                            if len(bbox) == 4:
                                x1, y1, x2, y2 = bbox
                                st.write(f"**Position:** ({x1}, {y1}) to ({x2}, {y2})")
                                st.write(f"**Size:** {x2-x1} × {y2-y1} pixels")
                        
                        # Visualize component on image
                        if len(bbox) == 4:
                            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                            ax.imshow(original_image)
                            
                            # Draw bounding box
                            x1, y1, x2, y2 = bbox
                            rect = Rectangle((x1, y1), x2-x1, y2-y1, 
                                           linewidth=2, edgecolor='red', facecolor='none')
                            ax.add_patch(rect)
                            
                            # Add label
                            ax.text(x1, y1-10, comp.get('type', 'unknown'), 
                                   color='red', fontsize=12, fontweight='bold',
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
                            
                            ax.set_title(f"Component: {comp.get('type', 'unknown')}")
                            ax.axis('off')
                            st.pyplot(fig)
                            plt.close()
            
            # Display raw JSON
            with st.expander("📄 Raw JSON Output"):
                st.json(result)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.subheader("📊 Analysis Results")
            st.info("👆 Upload an image and click 'Analyze Image' to see results here.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Vision2Code AI - UI Layout Analysis Tool | Built with FastAPI & Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
