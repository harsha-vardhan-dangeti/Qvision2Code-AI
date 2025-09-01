# Figma Integration Service

This service integrates with the Figma API to fetch design files, preprocess the data, and extract UI components while maintaining the hierarchical tree structure.

## Features

- **Figma API Integration**: Fetch files, projects, and team information
- **Data Preprocessing**: Remove verbose fields while preserving essential information
- **Tree Structure Preservation**: Maintain hierarchical component relationships
- **UI Component Extraction**: Convert Figma nodes to standardized UI components
- **Multiple Output Formats**: Raw data, processed components, and UI-ready format

## Setup

### 1. Environment Variables

Create a `.env` file in your project root:

```bash
# Figma API Configuration
FIGMA_ACCESS_TOKEN=your_figma_access_token_here
FIGMA_BASE_URL=https://api.figma.com/v1
FIGMA_TIMEOUT=30
FIGMA_MAX_RETRIES=3

# Backend Configuration
API_HOST=localhost
API_PORT=8000
```

### 2. Get Figma Access Token

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Navigate to "Personal access tokens"
3. Click "Create new token"
4. Copy the token and add it to your `.env` file

### 3. Install Dependencies

```bash
pip install requests fastapi python-multipart
```

## API Endpoints

### Core Analysis

#### `POST /figma/analyze`

Analyze a Figma file and return processed UI components.

**Request Body:**

```json
{
  "file_key": "figma_file_key_here",
  "node_ids": ["node_id_1", "node_id_2"],
  "target_platform": "web",
  "include_raw": false,
  "include_tree": true
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully analyzed Figma file with 15 components",
  "ui_data": {
    "page": {"width": 1440, "height": 1024},
    "components": [...],
    "metadata": {...}
  },
  "component_tree": {...}
}
```

### File Operations

#### `GET /figma/file/{file_key}`

Get processed Figma file data.

**Query Parameters:**

- `node_ids`: Comma-separated node IDs (optional)
- `target_platform`: Target platform (web, mobile, desktop)

#### `GET /figma/file/{file_key}/raw`

Get raw Figma data without preprocessing.

#### `GET /figma/file/{file_key}/components`

Get only extracted UI components.

#### `GET /figma/file/{file_key}/tree`

Get component tree structure.

### Project & Team Management

#### `GET /figma/project/{project_id}/files`

Get all files in a project.

#### `GET /figma/team/{team_id}/projects`

Get all projects in a team.

#### `GET /figma/team/{team_id}`

Get team information.

### Utilities

#### `POST /figma/preprocess`

Preprocess raw Figma data without API call.

#### `GET /figma/health`

Health check endpoint.

## Usage Examples

### Python Client

```python
import requests

# Analyze a Figma file
response = requests.post("http://localhost:8000/figma/analyze", json={
    "file_key": "your_file_key",
    "target_platform": "web"
})

if response.status_code == 200:
    data = response.json()
    components = data["ui_data"]["components"]
    print(f"Found {len(components)} components")
```

### cURL Examples

```bash
# Analyze a Figma file
curl -X POST "http://localhost:8000/figma/analyze" \
  -H "Content-Type: application/json" \
  -d '{"file_key": "your_file_key", "target_platform": "web"}'

# Get file components
curl "http://localhost:8000/figma/file/your_file_key/components"

# Get component tree
curl "http://localhost:8000/figma/file/your_file_key/tree"
```

## Data Structure

### Processed Component Format

```json
{
  "id": "node_id",
  "type": "container",
  "name": "Button Container",
  "text": "Click me",
  "bbox": [100, 200, 200, 250],
  "width": 100,
  "height": 50,
  "role": "button",
  "properties": {
    "fills": [...],
    "cornerRadius": 8,
    "constraints": {...}
  }
}
```

### Component Tree Structure

```json
{
  "id": "root_node",
  "name": "Main Frame",
  "type": "FRAME",
  "visible": true,
  "bbox": { "x": 0, "y": 0, "width": 1440, "height": 1024 },
  "children": [
    {
      "id": "child_node",
      "name": "Header",
      "type": "FRAME",
      "visible": true,
      "bbox": { "x": 0, "y": 0, "width": 1440, "height": 80 }
    }
  ]
}
```

## Data Preprocessing

The service automatically:

1. **Removes verbose fields**: `createdAt`, `updatedAt`, `user`, etc.
2. **Preserves essential fields**: Layout, visual properties, text content
3. **Maintains hierarchy**: Keeps parent-child relationships
4. **Extracts components**: Converts Figma nodes to UI components
5. **Standardizes types**: Maps Figma types to component types

### Essential Fields Preserved

- **Core**: `id`, `name`, `type`, `visible`
- **Layout**: `x`, `y`, `width`, `height`, `absoluteBoundingBox`
- **Visual**: `fills`, `strokes`, `effects`, `cornerRadius`
- **Text**: `characters`, `fontSize`, `fontName`
- **Layout**: `constraints`, `layoutMode`, `constraints`
- **Hierarchy**: `children`

## Error Handling

The service includes comprehensive error handling:

- **API Errors**: Network issues, timeouts, authentication failures
- **Data Errors**: Invalid file keys, malformed responses
- **Processing Errors**: Data preprocessing failures

All errors return appropriate HTTP status codes and detailed error messages.

## Performance Considerations

- **Caching**: Consider implementing Redis caching for frequently accessed files
- **Rate Limiting**: Figma API has rate limits (1000 requests per hour)
- **Timeout**: Configurable timeout for API requests
- **Retries**: Automatic retry mechanism for failed requests

## Security

- **Access Tokens**: Store securely in environment variables
- **API Keys**: Never commit tokens to version control
- **Rate Limiting**: Implement rate limiting for public endpoints
- **Validation**: Validate all input parameters

## Troubleshooting

### Common Issues

1. **Invalid Access Token**

   - Verify token in Figma account settings
   - Check environment variable configuration

2. **File Not Found**

   - Verify file key from Figma URL
   - Check file permissions and access

3. **Timeout Errors**

   - Increase timeout configuration
   - Check network connectivity

4. **Rate Limit Exceeded**
   - Wait for rate limit reset
   - Implement request caching

### Debug Mode

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

## Contributing

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Follow Python coding standards (PEP 8)

## License

This service is part of the Vision2Code AI project.
