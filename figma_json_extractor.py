import requests
import json

# Replace with your actual Figma credentials
FIGMA_API_TOKEN = 'figd_eG7Z6TrMOiFJBDuMHzv7DZpwbQjS4UICLSVhxBLN'
FILE_KEY = 'pv7W1INwSfygXFnX90BgFn'

headers = {
    'X-Figma-Token': FIGMA_API_TOKEN
}
base_url = 'https://api.figma.com/v1'

# Step 1: Get file structure
file_response = requests.get(f'{base_url}/files/{FILE_KEY}', headers=headers)
file_data = file_response.json()

# Step 2: Traverse document tree
def extract_nodes(node):
    elements = []
    for child in node.get('children', []):
        element = {
            'id': child.get('id'),
            'name': child.get('name'),
            'type': child.get('type'),
            'position': child.get('absoluteBoundingBox', {}),
            'style': child.get('style', {}),
            'layout': {
                'layoutMode': child.get('layoutMode'),
                'constraints': child.get('constraints')
            },
            'fills': child.get('fills', []),
            'text': child.get('characters') if child.get('type') == 'TEXT' else None,
            'children': extract_nodes(child)
        }
        elements.append(element)
    return elements

frames = []
for canvas in file_data['document'].get('children', []):
    frames.append({
        'frameName': canvas.get('name'),
        'type': canvas.get('type'),
        'size': canvas.get('absoluteBoundingBox', {}),
        'children': extract_nodes(canvas)
    })

# Step 3: Identify image fill node IDs
def find_image_fill_nodes(node, image_ids):
    for fill in node.get('fills', []):
        if fill.get('type') == 'IMAGE':
            image_ids.append(node.get('id'))
            break
    for child in node.get('children', []):
        find_image_fill_nodes(child, image_ids)

image_node_ids = []
for canvas in file_data['document'].get('children', []):
    find_image_fill_nodes(canvas, image_node_ids)

# Step 4: Get image URLs
image_response = requests.get(f'{base_url}/images/{FILE_KEY}?ids={",".join(image_node_ids)}', headers=headers)
image_data = image_response.json()
assets = [{'nodeId': nid, 'type': 'IMAGE', 'url': url} for nid, url in image_data.get('images', {}).items()]

# Step 5: Get components
components_response = requests.get(f'{base_url}/files/{FILE_KEY}/components', headers=headers)
components_data = components_response.json()
components = [{
    'name': comp.get('name'),
    'description': comp.get('description'),
    'nodeId': comp.get('node_id'),
    'containingFrame': comp.get('containing_frame', {}).get('name')
} for comp in components_data.get('meta', {}).get('components', [])]

# Step 6: Get styles
styles_response = requests.get(f'{base_url}/files/{FILE_KEY}/styles', headers=headers)
styles_data = styles_response.json()
styles = {
    'textStyles': [],
    'colorStyles': [],
    'effectStyles': []
}
for style in styles_data.get('meta', {}).get('styles', []):
    entry = {
        'name': style.get('name'),
        'styleType': style.get('style_type'),
        'nodeId': style.get('node_id'),
        'description': style.get('description')
    }
    if style['style_type'] == 'TEXT':
        styles['textStyles'].append(entry)
    elif style['style_type'] == 'FILL':
        styles['colorStyles'].append(entry)
    elif style['style_type'] == 'EFFECT':
        styles['effectStyles'].append(entry)

# Final structured JSON
structured_json = {
    'file': {
        'name': file_data.get('name'),
        'id': FILE_KEY,
        'frames': frames
    },
    'assets': assets,
    'components': components,
    'styles': styles
}

# Save to file
with open('figma_structured.json', 'w') as f:
    json.dump(structured_json, f, indent=2)

print("✅ Structured JSON saved to figma_structured.json")
