# 🚀 Vision2Code AI - Quick Start Guide

## ⚡ **One-Click Startup**

### **Method 1: Python Script (Recommended)**

```bash
python start_vision2code.py
```

### **Method 2: Direct Execution**

```bash
./start_vision2code.py
```

## 🎯 **What This Script Does Automatically**

### **1. 🔍 Dependency Check**

- ✅ Verifies all required packages are installed
- ✅ Checks if ports 8000 and 8501 are available
- ✅ Validates Python environment

### **2. 🚀 Backend Startup**

- 🔧 Starts FastAPI server on port 8000
- 📡 Waits for backend to be ready
- 🔄 Enables auto-reload for development

### **3. 🌐 Frontend Startup**

- 📱 Starts Streamlit UI on port 8501
- ⏳ Waits for frontend to be ready
- 🎨 Loads the UI Inspector application

### **4. 📊 Service Monitoring**

- 👀 Monitors both services continuously
- 🚨 Alerts if any service stops unexpectedly
- 🛑 Graceful shutdown on Ctrl+C

## 🌐 **Access Your Application**

Once started, you can access:

- **📱 Main UI**: http://localhost:8501
- **📚 API Documentation**: http://localhost:8000/docs
- **🔍 Health Check**: http://localhost:8000/health

## 🛠️ **Features Available**

### **🖼️ Image Analysis**

- Upload UI screenshots
- Automatic component detection
- Structured JSON output

### **🎨 Figma Integration**

- Connect to Figma API
- Analyze design files
- Extract UI components
- View raw vs. processed data

### **📊 Component Extraction**

- Hierarchical tree structures
- Export options (JSON, component trees)
- Platform-specific analysis

## ⚠️ **Important Notes**

- **Keep the terminal open** while using the application
- **Press Ctrl+C** to stop all services gracefully
- **Backend auto-reloads** when you modify code
- **Frontend updates** automatically

## 🔧 **Troubleshooting**

### **Port Already in Use**

```bash
# Check what's using the ports
lsof -i :8000
lsof -i :8501

# Kill processes if needed
kill -9 <PID>
```

### **Missing Dependencies**

```bash
# Install missing packages
pip install fastapi uvicorn streamlit requests pillow matplotlib numpy
```

### **Permission Issues**

```bash
# Make script executable
chmod +x start_vision2code.py
```

## 🎉 **You're All Set!**

Just run `python start_vision2code.py` and everything will start automatically! 🚀

---

**Need Help?** Check the logs in the terminal for detailed information about what's happening during startup.
