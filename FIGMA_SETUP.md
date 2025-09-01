# 🚀 Quick Setup Guide - Figma Integration

## 1. Get Your Figma Access Token

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Navigate to "Personal access tokens"
3. Click "Create new token"
4. Give it a name (e.g., "Vision2Code AI")
5. Copy the generated token

## 2. Configure Environment

```bash
# Copy the environment template
cp env_template.txt .env

# Edit .env file and add your Figma token
nano .env
```

Set your token:

```bash
FIGMA_ACCESS_TOKEN=your_actual_token_here
```

## 3. Test the Service

```bash
# Test the Figma service functionality
python3 test_figma_service.py

# Start the server
python3 start_figma_service.py
```

## 4. Use the API

Once the server is running, you can:

- **View API docs**: http://localhost:8000/docs
- **Test Figma endpoints**: http://localhost:8000/figma/health
- **Analyze a Figma file**: POST to http://localhost:8000/figma/analyze

## 5. Example Usage

```bash
# Analyze a Figma file
curl -X POST "http://localhost:8000/figma/analyze" \
  -H "Content-Type: application/json" \
  -d '{"file_key": "your_file_key", "target_platform": "web"}'

# Get file components
curl "http://localhost:8000/figma/file/your_file_key/components"
```

## 6. Troubleshooting

- **Import errors**: Make sure you're in the project root directory
- **Token errors**: Verify your Figma access token is correct
- **Server won't start**: Check if port 8000 is available
- **API errors**: Check the server logs for detailed error messages

## 7. File Structure

```
app/
├── figma_service.py      # Core Figma service
├── figma_routes.py       # API endpoints
└── main.py              # Main FastAPI app

env_template.txt          # Environment template
test_figma_service.py     # Test script
start_figma_service.py    # Startup script
FIGMA_INTEGRATION.md      # Full documentation
```

## 8. Next Steps

- Read the full [FIGMA_INTEGRATION.md](FIGMA_INTEGRATION.md) for detailed API documentation
- Test with your own Figma files
- Integrate with your existing applications
- Customize the preprocessing logic as needed

---

**Need help?** Check the logs or run the test script to diagnose issues.
