# 🎯 Vision2Code AI

**AI-powered UI analysis and Figma integration service that converts designs into structured code-ready data.**

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Vision2Code_AI
   ```

2. **Create and activate virtual environment**

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**
   ```bash
   python start.py
   ```

## 📋 Features

### 🖼️ Image Analysis

- Upload screenshots or UI images
- Extract UI components automatically
- Generate structured JSON output
- Support for web, mobile, and desktop platforms

### 🎨 Figma Integration

- Connect to Figma API with personal access token
- **LLM-powered preprocessing** for intelligent component extraction
- Analyze Figma files with AI understanding
- Smart component type classification
- Context-aware data preprocessing

### 🔧 API Endpoints

- `POST /analyze` - Image analysis
- `POST /figma/analyze` - Figma file analysis
- `POST /figma/preprocess` - Preprocess Figma data
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Figma Integration (Required for Figma features)
FIGMA_ACCESS_TOKEN=your_figma_token_here

# LLM Integration (Required for intelligent preprocessing)
OPENAI_API_KEY=your_openai_key_here

# UI Analysis (Optional)
UI2JSON_USE_YOLO=false
UI2JSON_USE_OCR=true
UI2JSON_USE_VLM=false
YOLO_MODEL=
```

### Figma Setup

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Generate a personal access token
3. Add it to your `.env` file or configure in the UI

### LLM Setup

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `.env` file as `OPENAI_API_KEY`
3. Choose your preferred model in the UI (gpt-4o-mini recommended for cost efficiency)

## 🏃‍♂️ Running the Application

### Option 1: Simple Start (Recommended)

```bash
python start.py
```

This starts both backend and frontend automatically.

### Option 2: Manual Start

```bash
# Terminal 1 - Backend
source myenv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
source myenv/bin/activate
streamlit run web/ui_inspector.py --server.port 8501
```

## 🌐 Access Points

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
Vision2Code_AI/
├── app/                    # Backend application
│   ├── main.py            # FastAPI main application
│   ├── pipeline.py        # Image analysis pipeline
│   ├── figma_service.py   # Figma API service
│   ├── figma_routes.py    # Figma API routes
│   ├── schemas.py         # Data schemas
│   └── utils.py           # Utility functions
├── web/                   # Frontend application
│   └── ui_inspector.py    # Streamlit UI
├── start.py               # Simple startup script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Development

### Adding New Features

1. Backend changes go in `app/` directory
2. Frontend changes go in `web/` directory
3. Update API documentation in `main.py`
4. Test with both image and Figma workflows

### Code Style

- Use type hints
- Add docstrings for functions
- Follow PEP 8 guidelines
- Keep functions focused and simple

## 🐛 Troubleshooting

### Common Issues

**Import Errors**

```bash
# Make sure virtual environment is activated
source myenv/bin/activate
```

**Port Already in Use**

```bash
# Kill processes on ports 8000 and 8501
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

**Figma API Errors**

- Verify your access token is correct
- Check file permissions in Figma
- Ensure file key is from a `/file/` URL, not `/design/`

**Timeout Errors**

- Large Figma files may take longer to process
- The system automatically adjusts timeouts based on file size
- Try with smaller files or specific node IDs

### Logs

Check the terminal output for detailed error messages and processing logs.

## 📊 Performance

- **Image Analysis**: Typically 2-5 seconds
- **Figma Processing**: 10-60 seconds depending on file size
- **Memory Usage**: Optimized for files up to 100MB
- **Concurrent Users**: Supports multiple simultaneous requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs for detailed error messages
4. Create an issue with detailed information

---

**Vision2Code AI** - Bridging the gap between design and development 🚀
