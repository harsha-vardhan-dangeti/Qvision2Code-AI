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

def count_total_nodes(node):
    """Recursively count total nodes in the document tree"""
    if not isinstance(node, dict):
        return 0
    
    count = 1  # Count this node
    
    # Count children recursively
    if "children" in node:
        for child in node["children"]:
            count += count_total_nodes(child)
    
    return count

# Configure the page
st.set_page_config(
    page_title="Vision2Code - UI Inspector & Figma Integration",
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
    .figma-section {
        background-color: #f0f8ff;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #4CAF50;
    }
    .token-section {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin-bottom: 1rem;
    }
    .help-text {
        font-size: 0.9rem;
        color: #666;
        font-style: italic;
    }
    .file-helper {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #4CAF50;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def render_overlay(image: Image.Image, ui_json):
    try:
        comps = (ui_json or {}).get("components", [])
    except Exception:
        comps = []
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.imshow(image)
    for comp in comps:
        bbox = comp.get("bbox", [])
        if isinstance(bbox, list) and len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            rect = Rectangle((x1, y1), x2-x1, y2-y1, linewidth=2, edgecolor='#3b82f6', facecolor='none')
            ax.add_patch(rect)
            label = comp.get('type', 'comp')
            ax.text(x1, max(0, y1-6), label,
                    color='#111827', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#e5edff", edgecolor="#3b82f6", alpha=0.9))
    ax.axis('off')
    return fig

def get_figma_token_from_ui():
    """Get Figma access token from UI or session state"""
    if 'figma_token' not in st.session_state:
        st.session_state.figma_token = ""
    return st.session_state.figma_token

def render_figma_token_config():
    """Render Figma access token configuration section"""
    st.markdown('<div class="token-section">', unsafe_allow_html=True)
    st.subheader("🔑 Figma Access Token Configuration")
    
    st.markdown("""
    <div class="help-text">
    To use Figma integration, you need a personal access token from your Figma account.
    </div>
    """, unsafe_allow_html=True)
    
    # Token input
    figma_token = st.text_input(
        "Figma Access Token",
        value=get_figma_token_from_ui(),
        type="password",
        placeholder="Enter your Figma personal access token",
        help="Get this from Figma Settings → Personal Access Tokens"
    )
    
    # Store token in session state
    if figma_token:
        st.session_state.figma_token = figma_token
    
    # Token validation and help
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if figma_token:
            if len(figma_token) > 20:
                st.success("✅ Token configured")
            else:
                st.warning("⚠️ Token seems too short")
        else:
            st.info("ℹ️ Enter your Figma access token above")
    
    with col2:
        if st.button("🔍 Test Token", help="Test if your token is valid"):
            if figma_token:
                test_figma_token(figma_token)
            else:
                st.error("Please enter a token first")
    
    # Help section
    with st.expander("📖 How to get your Figma Access Token"):
        st.markdown("""
        1. **Go to Figma Account Settings**
           - Visit [figma.com/settings](https://www.figma.com/settings)
        
        2. **Navigate to Personal Access Tokens**
           - Click on "Personal access tokens" in the left sidebar
        
        3. **Create New Token**
           - Click "Create new token"
           - Give it a name (e.g., "Vision2Code AI")
           - Copy the generated token
        
        4. **Use the Token**
           - Paste it in the field above
           - Your token will be stored securely in this session
        
        **Note**: Tokens are stored only in your browser session and are not saved permanently.
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def test_figma_token(token):
    """Test if the Figma access token is valid"""
    with st.spinner("Testing token..."):
        try:
            headers = {
                'X-Figma-Token': token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                "https://api.figma.com/v1/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                st.success(f"✅ Token valid! Connected as: {user_data.get('email', 'Unknown user')}")
                st.session_state.figma_user = user_data
            elif response.status_code == 401:
                st.error("❌ Invalid token. Please check your Figma access token.")
            else:
                st.warning(f"⚠️ Token test returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error testing token: {str(e)}")

def render_figma_file_helper(figma_token):
    """Render helper section for getting Figma file endpoints"""
    st.markdown('<div class="file-helper">', unsafe_allow_html=True)
    st.subheader("📁 Figma File Helper")
    st.markdown("Easily find and access your Figma files")
    
    # File input methods
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔗 From URL**")
        figma_url = st.text_input(
            "Paste Figma URL",
            placeholder="https://figma.com/file/XXXXX/...",
            key="figma_url_input",
            help="Paste any Figma file URL"
        )
        
        if figma_url:
            # Extract file key from various Figma URL formats
            file_key = None
            if "figma.com/file/" in figma_url:
                file_key = figma_url.split("figma.com/file/")[1].split("/")[0]
            elif "figma.com/proto/" in figma_url:
                file_key = figma_url.split("figma.com/proto/")[1].split("/")[0]
            elif "figma.com/design/" in figma_url:
                file_key = figma_url.split("figma.com/design/")[1].split("/")[0]
            elif "figma.com/embed" in figma_url:
                if "url=" in figma_url:
                    embed_url = figma_url.split("url=")[1].split("&")[0]
                    if "figma.com/file/" in embed_url:
                        file_key = embed_url.split("figma.com/file/")[1].split("/")[0]
            
            if file_key:
                st.success(f"✅ File Key: `{file_key}`")
                if st.button("📋 Use This Key", key="use_url_key"):
                    st.session_state.extracted_file_key = file_key
                    st.success("File key extracted and ready to use!")
            else:
                st.warning("⚠️ Could not extract file key from this URL")
    
    with col2:
        st.markdown("**📝 Manual Input**")
        manual_key = st.text_input(
            "Enter File Key",
            placeholder="XXXXX",
            key="manual_key_input",
            help="Enter the file key manually"
        )
        
        if manual_key:
            st.info(f"File Key: `{manual_key}`")
            if st.button("📋 Use This Key", key="use_manual_key"):
                st.session_state.extracted_file_key = manual_key
                st.success("File key set!")
    
    with col3:
        st.markdown("**🔍 Manual Browse**")
        if st.button("📂 List My Files", key="list_files_btn"):
            if figma_token:
                list_user_files(figma_token)
            else:
                st.error("Please configure your Figma token first")
    
    # Show extracted file key if available
    if 'extracted_file_key' in st.session_state:
        st.markdown("---")
        st.markdown(f"**🎯 Selected File Key:** `{st.session_state.extracted_file_key}`")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Use This Key", type="primary", key="use_extracted_key"):
                st.session_state.current_file_key = st.session_state.extracted_file_key
                st.success("File key selected! You can now analyze this file.")
        
        with col2:
            if st.button("🗑️ Clear", key="clear_key_btn"):
                del st.session_state.extracted_file_key
                if 'current_file_key' in st.session_state:
                    del st.session_state.current_file_key
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def list_user_files(figma_token):
    """List user's accessible Figma files"""
    with st.spinner("Fetching your Figma files..."):
        try:
            headers = {
                'X-Figma-Token': figma_token,
                'Content-Type': 'application/json'
            }
            
            # Get user info first
            user_response = requests.get(
                "https://api.figma.com/v1/me",
                headers=headers,
                timeout=10
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get('id')
                
                if user_id:
                    st.success(f"✅ Connected as: {user_data.get('email', 'Unknown')}")
                    
                    # Try to get team projects first (most common case)
                    try:
                        # Get user's teams
                        teams_response = requests.get(
                            "https://api.figma.com/v1/teams",
                            headers=headers,
                            timeout=15
                        )
                        
                        if teams_response.status_code == 200:
                            teams_data = teams_response.json()
                            teams = teams_data.get('teams', [])
                            
                            if teams:
                                st.info(f"Found {len(teams)} teams")
                                
                                # Get files from team projects
                                for team in teams[:3]:  # Limit to first 3 teams
                                    team_id = team.get('id')
                                    team_name = team.get('name', 'Unnamed Team')
                                    
                                    with st.expander(f"🏢 {team_name}"):
                                        # Get team projects
                                        projects_response = requests.get(
                                            f"https://api.figma.com/v1/teams/{team_id}/projects",
                                            headers=headers,
                                            timeout=15
                                        )
                                        
                                        if projects_response.status_code == 200:
                                            projects_data = projects_response.json()
                                            projects = projects_data.get('projects', [])
                                            
                                            if projects:
                                                st.write(f"**Projects in {team_name}:**")
                                                for project in projects[:5]:  # Limit to first 5 projects
                                                    project_id = project.get('id')
                                                    project_name = project.get('name', 'Unnamed Project')
                                                    
                                                    # Get files in this project
                                                    files_response = requests.get(
                                                        f"https://api.figma.com/v1/projects/{project_id}/files",
                                                        headers=headers,
                                                        timeout=15
                                                    )
                                                    
                                                    if files_response.status_code == 200:
                                                        files_data = files_response.json()
                                                        files = files_data.get('files', [])
                                                        
                                                        if files:
                                                            st.write(f"📁 **{project_name}** ({len(files)} files):")
                                                            for file in files[:8]:  # Limit to first 8 files
                                                                file_name = file.get('name', 'Unnamed File')
                                                                file_key = file.get('key')
                                                                
                                                                col1, col2, col3 = st.columns([3, 2, 1])
                                                                with col1:
                                                                    st.write(f"📄 {file_name}")
                                                                with col2:
                                                                    st.write(f"`{file_key}`")
                                                                with col3:
                                                                    if st.button("📋 Use", key=f"use_file_{file_key}"):
                                                                        st.session_state.current_file_key = file_key
                                                                        st.success(f"Selected: {file_name}")
                                                                        st.rerun()
                                                        else:
                                                            st.info(f"No files in {project_name}")
                                                    else:
                                                        st.warning(f"Could not fetch files for {project_name}")
                                            else:
                                                st.info(f"No projects in {team_name}")
                                        else:
                                            st.warning(f"Could not fetch projects for {team_name}")
                            else:
                                st.info("No teams found - checking for personal files...")
                                
                                # Try to get personal files directly
                                personal_files_response = requests.get(
                                    "https://api.figma.com/v1/files",
                                    headers=headers,
                                    timeout=15
                                )
                                
                                if personal_files_response.status_code == 200:
                                    personal_files_data = personal_files_response.json()
                                    personal_files = personal_files_data.get('files', [])
                                    
                                    if personal_files:
                                        st.success(f"Found {len(personal_files)} personal files")
                                        st.write("**Your Personal Files:**")
                                        
                                        for file in personal_files[:10]:  # Limit to first 10 files
                                            file_name = file.get('name', 'Unnamed File')
                                            file_key = file.get('key')
                                            
                                            col1, col2, col3 = st.columns([3, 2, 1])
                                            with col1:
                                                st.write(f"📄 {file_name}")
                                            with col2:
                                                st.write(f"`{file_key}`")
                                            with col3:
                                                if st.button("📋 Use", key=f"use_file_{file_key}"):
                                                    st.session_state.current_file_key = file_key
                                                    st.success(f"Selected: {file_name}")
                                                    st.rerun()
                                    else:
                                        st.info("No personal files found")
                                else:
                                    st.warning("Could not fetch personal files")
                        else:
                            st.warning("Could not fetch teams - checking for personal files...")
                            
                            # Fallback to personal files
                            personal_files_response = requests.get(
                                "https://api.figma.com/v1/files",
                                headers=headers,
                                timeout=15
                            )
                            
                            if personal_files_response.status_code == 200:
                                personal_files_data = personal_files_response.json()
                                personal_files = personal_files_data.get('files', [])
                                
                                if personal_files:
                                    st.success(f"Found {len(personal_files)} personal files")
                                    st.write("**Your Personal Files:**")
                                    
                                    for file in personal_files[:10]:  # Limit to first 10 files
                                        file_name = file.get('name', 'Unnamed File')
                                        file_key = file.get('key')
                                        
                                        col1, col2, col3 = st.columns([3, 2, 1])
                                        with col1:
                                            st.write(f"📄 {file_name}")
                                        with col2:
                                            st.write(f"`{file_key}`")
                                        with col3:
                                            if st.button("📋 Use", key=f"use_file_{file_key}"):
                                                st.session_state.current_file_key = file_key
                                                st.success(f"Selected: {file_name}")
                                                st.rerun()
                                else:
                                    st.info("No personal files found")
                            else:
                                st.warning("Could not fetch personal files")
                                
                    except Exception as team_error:
                        st.warning(f"Team fetch error: {str(team_error)} - trying personal files...")
                        
                        # Final fallback to personal files
                        try:
                            personal_files_response = requests.get(
                                "https://api.figma.com/v1/files",
                                headers=headers,
                                timeout=15
                            )
                            
                            if personal_files_response.status_code == 200:
                                personal_files_data = personal_files_response.json()
                                personal_files = personal_files_data.get('files', [])
                                
                                if personal_files:
                                    st.success(f"Found {len(personal_files)} personal files")
                                    st.write("**Your Personal Files:**")
                                    
                                    for file in personal_files[:10]:  # Limit to first 10 files
                                        file_name = file.get('name', 'Unnamed File')
                                        file_key = file.get('key')
                                        
                                        col1, col2, col3 = st.columns([3, 2, 1])
                                        with col1:
                                            st.write(f"📄 {file_name}")
                                        with col2:
                                            st.write(f"`{file_key}`")
                                        with col3:
                                            if st.button("📋 Use", key=f"use_file_{file_key}"):
                                                st.session_state.current_file_key = file_key
                                                st.success(f"Selected: {file_name}")
                                                st.rerun()
                                else:
                                    st.info("No personal files found")
                            else:
                                st.warning("Could not fetch personal files")
                        except Exception as personal_error:
                            st.error(f"Error fetching personal files: {str(personal_error)}")
                else:
                    st.warning("Could not get user ID")
            else:
                st.error("Could not authenticate user")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching files: {str(e)}")

def render_figma_integration(api_endpoint):
    """Render Figma integration section"""
    st.markdown('<div class="figma-section">', unsafe_allow_html=True)
    st.subheader("🎨 Figma Integration")
    st.markdown("Connect to Figma and analyze design files directly")
    
    # Check if token is configured
    figma_token = get_figma_token_from_ui()
    if not figma_token:
        st.warning("⚠️ Please configure your Figma access token above first.")
        return
    
    # Show current user info if available
    if 'figma_user' in st.session_state:
        user_info = st.session_state.figma_user
        st.info(f"🔗 Connected as: {user_info.get('email', 'Unknown')}")
    
    # File helper section
    render_figma_file_helper(figma_token)
    
    # File analysis section
    st.markdown("---")
    st.subheader("🔍 File Analysis")
    
    # Get file key from various sources
    file_key = None
    if 'current_file_key' in st.session_state:
        file_key = st.session_state.current_file_key
        st.success(f"📁 Analyzing file: `{file_key}`")
    
    # File key input (with pre-filled value if available)
    figma_file_key = st.text_input(
        "Figma File Key",
        value=file_key or "",
        placeholder="Enter Figma file key from URL",
        help="Get this from your Figma file URL: figma.com/file/XXXXX/..."
    )
    
    # Update current file key
    if figma_file_key:
        st.session_state.current_file_key = figma_file_key
    
    # File key help
    if figma_file_key:
        # Extract file key from URL if user pasted full URL
        if "figma.com/file/" in figma_file_key:
            extracted_key = figma_file_key.split("figma.com/file/")[1].split("/")[0]
            if extracted_key != figma_file_key:
                st.info(f"📝 Extracted file key: {extracted_key}")
                figma_file_key = extracted_key
                st.session_state.current_file_key = extracted_key
    
    # Figma options
    col1, col2 = st.columns(2)
    
    with col1:
        figma_target_platform = st.selectbox(
            "Target Platform",
            options=["web", "mobile", "desktop"],
            index=0,
            key="figma_platform"
        )
        
        include_raw = st.checkbox("Include Raw Data", value=False)
    
    with col2:
        include_tree = st.checkbox("Include Component Tree", value=True)
        
        # Node IDs input (optional)
        node_ids_input = st.text_input(
            "Node IDs (optional)",
            placeholder="comma,separated,node,ids",
            help="Specific node IDs to analyze"
        )
    
    # Parse node IDs
    node_ids = None
    if node_ids_input:
        node_ids = [nid.strip() for nid in node_ids_input.split(",") if nid.strip()]
    
    # Analyze Figma button
    if st.button("🔍 Analyze Figma File", type="primary", use_container_width=True):
        if not figma_file_key:
            st.error("Please enter a Figma file key")
            return
        
        # Create a progress container
        progress_container = st.container()
        
        with progress_container:
            st.info("🚀 Starting Figma file analysis...")
            
        try:
            # Prepare request
            payload = {
                "file_key": figma_file_key,
                "target_platform": figma_target_platform,
                "include_raw": include_raw,
                "include_tree": include_tree
            }
            
            if node_ids:
                payload["node_ids"] = node_ids
            
            # Make API call with custom headers for token
            headers = {
                'Content-Type': 'application/json',
                'X-Figma-Token': figma_token
            }
            
            # Step 1: Fetch from Figma API
            with progress_container:
                st.info("📡 Step 1/4: Fetching file data from Figma...")
            
            # First, try to get the file directly from Figma API
            figma_response = requests.get(
                f"https://api.figma.com/v1/files/{figma_file_key}",
                headers=headers,
                timeout=60  # Increased timeout for Figma API
            )
            
            if figma_response.status_code == 200:
                figma_data = figma_response.json()
                
                # Step 2: Show raw data before preprocessing
                with progress_container:
                    st.info("📊 Step 2/4: Raw Figma data received - showing before preprocessing...")
                
                # Store raw Figma data for display
                st.session_state.raw_figma_data = figma_data
                
                # Show raw data preview before preprocessing
                st.markdown("### 🔍 Raw Figma Data Preview (Before Preprocessing)")
                st.markdown("**📋 This is the exact data received from Figma API:**")
                
                # Quick stats about raw data
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("File Name", figma_data.get("name", "N/A"))
                with col2:
                    st.metric("Last Modified", figma_data.get("lastModified", "N/A"))
                with col3:
                    st.metric("Version", figma_data.get("version", "N/A"))
                with col4:
                    st.metric("Thumbnail", "✅" if figma_data.get("thumbnailUrl") else "❌")
                
                # Document structure preview
                if "document" in figma_data:
                    doc = figma_data["document"]
                    st.markdown("**📁 Document Structure:**")
                    
                    # Count nodes at different levels
                    root_nodes = len(doc.get("children", []))
                    total_nodes = count_total_nodes(doc)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Root Nodes", root_nodes)
                    with col2:
                        st.metric("Total Nodes", total_nodes)
                    with col3:
                        st.metric("Document Type", doc.get("type", "N/A"))
                    
                    # Show first few root nodes
                    if root_nodes > 0:
                        st.markdown("**🔹 First 5 Root Nodes:**")
                        for i, child in enumerate(doc["children"][:5]):
                            st.markdown(f"**{child.get('name', f'Node {i+1}')} ({child.get('type', 'unknown')})**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**ID:** {child.get('id', 'N/A')}")
                                st.write(f"**Type:** {child.get('type', 'N/A')}")
                                st.write(f"**Visible:** {child.get('visible', True)}")
                            with col2:
                                if 'absoluteBoundingBox' in child:
                                    bbox = child['absoluteBoundingBox']
                                    st.write(f"**Position:** ({bbox.get('x', 0):.1f}, {bbox.get('y', 0):.1f})")
                                    st.write(f"**Size:** {bbox.get('width', 0):.1f} × {bbox.get('height', 0):.1f}")
                                
                                # Show child count
                                if "children" in child:
                                    st.write(f"**Children:** {len(child['children'])}")
                            st.markdown("---")
                
                # Raw JSON preview (first 1000 characters)
                st.markdown("**📄 Raw JSON Preview (First 1000 characters):**")
                raw_json_str = json.dumps(figma_data, indent=2)
                if len(raw_json_str) > 1000:
                    st.code(raw_json_str[:1000] + "...\n\n[Data truncated for preview. The complete raw data will be available after preprocessing.]")
                    st.info("💡 **Note:** This is a preview. The complete raw data will be available after preprocessing.")
                else:
                    st.code(raw_json_str)
                
                # Step 3: Send to preprocessing service
                with progress_container:
                    st.info("🔄 Step 3/4: Sending data to preprocessing service...")
                
                # Calculate file size for user info
                file_size_mb = len(json.dumps(figma_data)) / 1024 / 1024
                st.info(f"📊 File size: {file_size_mb:.2f} MB - Using optimized processing...")
                
                # Show processing strategy based on file size
                if file_size_mb > 100:
                    st.warning("⚠️ Very large file detected - using chunked processing (may take 5-10 minutes)")
                elif file_size_mb > 50:
                    st.info("📊 Large file detected - using extended processing (may take 3-5 minutes)")
                else:
                    st.success("✅ Normal file size - standard processing (should complete quickly)")
                
                # Now send to our preprocessing service
                # Server handles timeout based on file size automatically
                with st.spinner("🔄 Processing Figma data... This may take several minutes for large files."):
                    response = requests.post(
                        f"{api_endpoint}/figma/preprocess",
                        json=figma_data,
                        timeout=None  # Let server handle timeout, no client-side limit
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        with progress_container:
                            st.success("✅ Step 4/4: Analysis completed successfully!")
                        
                        # Store results in session state
                        st.session_state.figma_result = result
                        st.session_state.figma_file_key = figma_file_key
                        
                        # Show quick stats
                        ui_data = result.get("ui_data", {})
                        components = ui_data.get("components", [])
                        
                        # Show processing info if available
                        if "processing_info" in result:
                            processing_info = result["processing_info"]
                            st.success(f"⚡ Processing completed successfully!")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Components", len(components))
                            with col2:
                                st.metric("File Size", f"{processing_info.get('file_size_mb', 'N/A')} MB")
                            with col3:
                                st.metric("Processing Time", f"{processing_info.get('processing_time_seconds', 'N/A')}s")
                            with col4:
                                st.metric("Processing Mode", processing_info.get('processing_mode', 'N/A').title())
                        else:
                            # Fallback to old format
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Components", len(components))
                            with col2:
                                page = ui_data.get("page", {})
                                st.metric("Dimensions", f"{page.get('width', 'N/A')}×{page.get('height', 'N/A')}")
                            with col3:
                                metadata = result.get("metadata", {})
                                st.metric("Source", metadata.get("source", "Figma").title())
                        
                        # Show components
                        if components:
                            st.subheader("🧩 Extracted Components")
                            for i, comp in enumerate(components[:10]):  # Show first 10
                                with st.expander(f"{comp.get('name', f'Component {i+1}')} ({comp.get('type', 'unknown')})"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Role:** {comp.get('role', 'N/A')}")
                                        st.write(f"**Text:** {comp.get('text', 'N/A')}")
                                    with col2:
                                        st.write(f"**Position:** {comp.get('bbox', 'N/A')}")
                                        st.write(f"**Size:** {comp.get('width', 'N/A')} × {comp.get('height', 'N/A')}")
                        
                        # Show component tree if requested
                        if include_tree and result.get("component_tree"):
                            st.subheader("🌳 Component Tree")
                            tree = result.get("component_tree")
                            render_component_tree(tree)
                        
                        # Show raw data if requested
                        if include_raw and result.get("raw_figma_data"):
                            with st.expander("📄 Raw Figma Data"):
                                st.json(result.get("raw_figma_data"))
                        
                        # Show initial raw data from Figma API
                        if 'raw_figma_data' in st.session_state:
                            st.subheader("🔍 Raw Data Analysis")
                            
                            # Create tabs for different views
                            raw_tab1, raw_tab2, raw_tab3 = st.tabs(["📊 Quick Stats", "🌳 Document Structure", "📄 Full Raw Data"])
                            
                            with raw_tab1:
                                st.markdown("**📈 Raw Figma Data Statistics**")
                                raw_data = st.session_state.raw_figma_data
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Document Name", raw_data.get("name", "N/A"))
                                with col2:
                                    st.metric("Last Modified", raw_data.get("lastModified", "N/A"))
                                with col3:
                                    st.metric("Version", raw_data.get("version", "N/A"))
                                with col4:
                                    st.metric("Thumbnail URL", "✅" if raw_data.get("thumbnailUrl") else "❌")
                                
                                # Show document info
                                if "document" in raw_data:
                                    doc = raw_data["document"]
                                    st.markdown("**📋 Document Details**")
                                    st.write(f"**Type:** {doc.get('type', 'N/A')}")
                                    st.write(f"**ID:** {doc.get('id', 'N/A')}")
                                    st.write(f"**Name:** {doc.get('name', 'N/A')}")
                                    
                                    # Count nodes
                                    if "children" in doc:
                                        node_count = len(doc["children"])
                                        st.metric("Total Root Nodes", node_count)
                            
                            with raw_tab2:
                                st.markdown("**🌳 Document Structure Overview**")
                                raw_data = st.session_state.raw_figma_data
                                
                                if "document" in raw_data:
                                    doc = raw_data["document"]
                                    st.markdown("**📁 Root Level Structure**")
                                    
                                    # Show root level nodes
                                    if "children" in doc:
                                        for i, child in enumerate(doc["children"][:10]):  # Show first 10
                                            with st.expander(f"🔹 {child.get('name', f'Node {i+1}')} ({child.get('type', 'unknown')})"):
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    st.write(f"**ID:** {child.get('id', 'N/A')}")
                                                    st.write(f"**Type:** {child.get('type', 'N/A')}")
                                                    st.write(f"**Visible:** {child.get('visible', True)}")
                                                with col2:
                                                    if 'absoluteBoundingBox' in child:
                                                        bbox = child['absoluteBoundingBox']
                                                        st.write(f"**Position:** ({bbox.get('x', 0):.1f}, {bbox.get('y', 0):.1f})")
                                                        st.write(f"**Size:** {bbox.get('width', 0):.1f} × {bbox.get('height', 0):.1f}")
                                                
                                                # Show child count
                                                if "children" in child:
                                                    st.write(f"**Children:** {len(child['children'])}")
                                    
                                    if len(doc["children"]) > 10:
                                        st.info(f"Showing first 10 of {len(doc['children'])} root nodes. Use 'Full Raw Data' tab to see all.")
                                else:
                                    st.warning("No document structure found in raw data")
                            
                            with raw_tab3:
                                st.markdown("**📄 Complete Raw Figma Data**")
                                st.markdown("This is the exact data received from Figma API before any preprocessing:")
                                
                                # Add a search/filter option
                                search_term = st.text_input(
                                    "🔍 Search in raw data (optional)",
                                    placeholder="Enter text to search for...",
                                    help="Search for specific keys, values, or text in the raw data"
                                )
                                
                                # Display the raw data
                                raw_data = st.session_state.raw_figma_data
                                
                                if search_term:
                                    # Simple search functionality
                                    st.info(f"Searching for: '{search_term}'")
                                    # You could implement more sophisticated search here
                                
                                # Show the full raw data
                                st.json(raw_data)
                        
                        # Export options
                        st.subheader("💾 Export Options")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("📊 Export UI Data", use_container_width=True):
                                ui_data_str = json.dumps(ui_data, indent=2)
                                st.download_button(
                                    label="Download UI Data JSON",
                                    data=ui_data_str,
                                    file_name=f"figma_ui_data_{figma_file_key}.json",
                                    mime="application/json"
                                )
                        
                        with col2:
                            if st.button("🌳 Export Component Tree", use_container_width=True):
                                tree_data = result.get("component_tree", {})
                                tree_str = json.dumps(tree_data, indent=2)
                                st.download_button(
                                    label="Download Component Tree JSON",
                                    data=tree_str,
                                    file_name=f"figma_component_tree_{figma_file_key}.json",
                                    mime="application/json"
                                )
                        
                        with col3:
                            if st.button("📄 Export Raw Figma Data", use_container_width=True):
                                raw_data_str = json.dumps(st.session_state.raw_figma_data, indent=2)
                                st.download_button(
                                    label="Download Raw Figma Data JSON",
                                    data=raw_data_str,
                                    file_name=f"figma_raw_data_{figma_file_key}.json",
                                    mime="application/json"
                                )
                        
                    else:
                        st.error(f"Analysis failed: {result.get('message', 'Unknown error')}")
                elif response.status_code == 408:
                    st.error("⏰ Preprocessing timed out! The Figma file might be too large or complex. Try with a smaller file or specific node IDs.")
                    st.info("💡 **Tips to reduce processing time:**")
                    st.info("• Use specific node IDs instead of entire file")
                    st.info("• Try with smaller Figma files first")
                    st.info("• Check if the file has many complex components")
                else:
                    st.error(f"Preprocessing Error: {response.status_code} - {response.text}")
                    
            elif figma_response.status_code == 404:
                st.error("❌ Figma file not found. Check the file key and your access permissions.")
            elif figma_response.status_code == 403:
                st.error("❌ Access denied. Check if you have permission to view this file.")
            elif figma_response.status_code == 401:
                st.error("❌ Invalid token. Please check your Figma access token.")
            else:
                st.error(f"❌ Figma API Error: {figma_response.status_code} - {figma_response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to Figma API. Check your internet connection.")
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. The Figma file might be very large or the service is busy. Try again later.")
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_component_tree(node, level=0):
    """Render component tree structure"""
    if isinstance(node, dict):
        name = node.get('name', 'Unknown')
        node_type = node.get('type', 'unknown')
        
        # Create expandable section for each node
        with st.expander(f"🔹 {name} ({node_type})", expanded=level < 2):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {node.get('id', 'N/A')}")
                st.write(f"**Type:** {node_type}")
                st.write(f"**Visible:** {node.get('visible', True)}")
            
            with col2:
                if 'bbox' in node:
                    bbox = node['bbox']
                    st.write(f"**Position:** ({bbox.get('x', 0)}, {bbox.get('y', 0)})")
                    st.write(f"**Size:** {bbox.get('width', 0)} × {bbox.get('height', 0)}")
            
            # Render children
            children = node.get('children', [])
            if children:
                st.write("**Children:**")
                for child in children:
                    render_component_tree(child, level + 1)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 Vision2Code UI Inspector & Figma Integration</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload UI screenshots or analyze Figma designs to get structured JSON layout analysis</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    # API endpoint configuration
    api_endpoint = st.sidebar.text_input(
        "API Endpoint",
        value="http://localhost:8000",
        help="FastAPI server endpoint"
    )
    
    # Service selection
    service_type = st.sidebar.radio(
        "Service Type",
        ["Image Analysis", "Figma Integration"],
        help="Choose between image analysis or Figma integration"
    )
    
    # Target platform selection
    target_platform = st.sidebar.selectbox(
        "Target Platform",
        options=["web", "mobile", "desktop"],
        index=0,
        help="Select the target platform for analysis"
    )
    
    # Main content area based on service type
    if service_type == "Image Analysis":
        # Original image analysis functionality
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

                            files = {"image": ("image.png", img_byte_arr, "image/png")}
                            data = {"target": target_platform}

                            response = requests.post(
                                f"{api_endpoint}/analyze",
                                files=files,
                                data=data,
                                timeout=300
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.session_state.analysis_result = result
                                st.success("✅ Analysis completed! View results below.")
                                st.rerun()
                            else:
                                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Cannot connect to API server. Make sure the FastAPI server is running.")
                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.subheader("📊 Results")
            
            if 'analysis_result' in st.session_state:
                result = st.session_state.analysis_result
                components = result.get("components", [])
                
                st.success(f"🎯 Detected {len(components)} UI components")
                
                if "page" in result:
                    page_info = result["page"]
                    st.info(f"📏 {page_info.get('width', 'N/A')} × {page_info.get('height', 'N/A')} pixels")
                
                # Show components
                if components:
                    st.subheader("🧩 Components")
                    for i, comp in enumerate(components):
                        with st.expander(f"Component {i+1}: {comp.get('type', 'unknown')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Type:** {comp.get('type', 'N/A')}")
                                st.write(f"**Role:** {comp.get('role', 'N/A')}")
                                st.write(f"**Text:** {comp.get('text', 'N/A')}")
                            with col2:
                                bbox = comp.get('bbox', [])
                                if len(bbox) == 4:
                                    x1, y1, x2, y2 = bbox
                                    st.write(f"**Position:** ({x1}, {y1}) to ({x2}, {y2})")
                                    st.write(f"**Size:** {x2-x1} × {y2-y1} pixels")
                
                # Raw JSON
                with st.expander("📄 Raw JSON Output"):
                    st.json(result)
            else:
                st.info("👆 Upload an image and analyze to see results here.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # Figma Integration
        # Show token configuration first
        render_figma_token_config()
        
        # Then show Figma integration
        render_figma_integration(api_endpoint)

if __name__ == "__main__":
    main()
