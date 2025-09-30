
import requests

def find_image_fill_nodes(figma_document):
    """
    Traverse the Figma document tree and identify nodes with fills of type 'IMAGE'.

    Parameters:
        figma_document (dict): Parsed JSON response from Figma Files API.

    Returns:
        List[str]: List of node IDs with image fills.
    """
    image_nodes = []

    def traverse(node):
        # Check if the node has fills and any fill is of type 'IMAGE'
        if 'fills' in node and isinstance(node['fills'], list):
            for fill in node['fills']:
                if fill.get('type') == 'IMAGE':
                    image_nodes.append(node.get('id', node.get('name', 'unknown')))
                    break  # Only need to record once per node

        # Recursively traverse children
        for child in node.get('children', []):
            traverse(child)

    # Start traversal from the document root
    if 'document' in figma_document:
        traverse(figma_document['document'])

    return image_nodes


# Replace with your actual Figma API token and file key
headers = { "X-Figma-Token": "figd_eG7Z6TrMOiFJBDuMHzv7DZpwbQjS4UICLSVhxBLN" }
file_key = "pv7W1INwSfygXFnX90BgFn"

response = requests.get(f"https://api.figma.com/v1/files/{file_key}", headers=headers)
figma_data = response.json()


image_node_ids = find_image_fill_nodes(figma_data)
print("Nodes with image fills:", image_node_ids)




