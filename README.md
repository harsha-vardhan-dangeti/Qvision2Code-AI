# 🔍 Vision2Code AI - UI Layout Analysis Tool

Vision2Code AI is a powerful tool that converts UI screenshots into structured JSON layouts using advanced computer vision, OCR, and AI techniques. It can detect UI components, extract text, and provide detailed analysis of web interfaces, mobile apps, and desktop applications.

## ✨ Features

- **🖼️ Image Analysis**: Upload UI screenshots and get detailed component analysis
- **🔍 Component Detection**: Identify buttons, inputs, navigation bars, cards, and more
- **📝 Text Extraction**: OCR-powered text recognition from UI elements
- **🤖 AI Refinement**: Optional VLM (Vision Language Model) integration for enhanced accuracy
- **🌐 Multi-Platform**: Support for web, mobile, and desktop UI analysis
- **📊 Visual Results**: Interactive visualization of detected components
- **🚀 Fast API**: RESTful API for easy integration
- **💻 Web Interface**: Beautiful Streamlit-based web application

## 🏗️ Architecture

The project consists of two main components:

1. **FastAPI Backend** (`app/`): Core analysis pipeline and REST API
2. **Streamlit Frontend** (`web/`): User-friendly web interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Vision2Code_AI
   ```

2. **Create virtual environment**

   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if using VLM features
   ```

### Running the Application

#### Option 1: Web Interface (Recommended)

1. **Start the FastAPI backend**

   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Streamlit frontend** (in a new terminal)

   ```bash
   cd web
   streamlit run ui_inspector.py --server.port 8501
   ```

3. **Open your browser**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

#### Option 2: API Only

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access the API at http://localhost:8000

## 📖 Usage

### Web Interface

1. Open the Streamlit app in your browser
2. Upload a UI screenshot (PNG, JPG, JPEG, BMP, TIFF)
3. Click "Analyze Image"
4. View the detected components and their properties
5. Explore the raw JSON output

### API Usage

#### Analyze an Image

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@your_screenshot.png" \
     -F "target=web"
```

#### Response Format

```json
{
  "page": {
    "width": 1920,
    "height": 1080
  },
  "components": [
    {
      "id": "comp_1",
      "type": "navbar",
      "role": "navigation",
      "bbox": [0, 0, 1920, 80],
      "text": "Navigation Menu",
      "children": []
    },
    {
      "id": "comp_2",
      "type": "button",
      "role": "submit",
      "bbox": [100, 200, 200, 240],
      "text": "Submit",
      "children": []
    }
  ]
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Enable/disable features
UI2JSON_USE_YOLO=false
UI2JSON_USE_OCR=true
UI2JSON_USE_VLM=false

# YOLO model path (if using YOLO)
YOLO_MODEL=path/to/your/model.pt

# OpenAI API key (if using VLM)
OPENAI_API_KEY=your_openai_api_key
```

### Feature Flags

- **YOLO Detection**: Set `UI2JSON_USE_YOLO=true` for ML-powered component detection
- **OCR Text Extraction**: Set `UI2JSON_USE_OCR=true` for text recognition
- **VLM Refinement**: Set `UI2JSON_USE_VLM=true` for AI-powered result refinement

## 🔧 Development

### Project Structure

```
Vision2Code_AI/
├── app/                    # FastAPI backend
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI app and endpoints
│   ├── pipeline.py        # Core analysis pipeline
│   ├── schemas.py         # Data models and utilities
│   └── utils.py           # Helper functions
├── web/                   # Streamlit frontend
│   └── ui_inspector.py    # Web interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .env.example          # Environment variables template
```

### Adding New Component Types

1. Add the component type to `UI_LABELS` in `pipeline.py`
2. Update the `assign_component_type` function with detection logic
3. Test with sample images

### Extending the Pipeline

The pipeline is modular and can be extended:

- **New Detectors**: Add detection functions and integrate them in `to_detections()`
- **Text Extractors**: Implement new OCR methods in `ocr_text()`
- **VLM Providers**: Add support for different AI models in `refine_with_vlm()`

## 🧪 Testing

### Test Images

Use various UI screenshots to test the system:

- Web applications
- Mobile app interfaces
- Desktop software
- Different resolutions and layouts

### API Testing

Use the built-in FastAPI docs at http://localhost:8000/docs for interactive testing.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- Tesseract for OCR functionality
- Ultralytics for YOLO integration
- FastAPI for the robust backend framework
- Streamlit for the beautiful web interface

## 🆘 Support

If you encounter any issues:

1. Check the console logs for error messages
2. Verify all dependencies are installed correctly
3. Ensure the FastAPI server is running
4. Check the API documentation at `/docs`

For feature requests or bug reports, please open an issue on the project repository.

✅ Application Status: RUNNING
Backend (FastAPI):
✅ Running on: http://localhost:8000
✅ Health check: http://localhost:8000/health
✅ API endpoint: http://localhost:8000/analyze
✅ API documentation: http://localhost:8000/docs
Frontend (Streamlit):
✅ Running on: http://localhost:8501
✅ Web interface is accessible
