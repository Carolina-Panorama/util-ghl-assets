import os
import requests
import json

GHL_API_BASE = "https://services.leadconnectorhq.com"


def get_ghl_token():
    """Load GHL token from environment variable."""
    return os.getenv("GHL_TOKEN")


def get_ghl_headers():
    """Return standard headers for GHL API requests, including auth and required version."""
    token = get_ghl_token()
    if not token:
        raise ValueError("GHL_TOKEN not set in environment.")
    return {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Version': '2021-07-28'
    }


def prepare_file_field(file_path, field_name='file'):
    """Prepare a file tuple for requests multipart upload."""
    file_name = os.path.basename(file_path)
    file_obj = open(file_path, 'rb')
    return {field_name: (file_name, file_obj)}


def send_ghl_post(endpoint, files=None, data=None):
    """Send a POST request to a GHL API endpoint and return the response object."""
    url = f"{GHL_API_BASE}{endpoint}"
    headers = get_ghl_headers()
    response = requests.post(url, headers=headers, files=files, data=data)
    # Close all file objects if any
    if files:
        for f in files.values():
            if hasattr(f, '__iter__') and not isinstance(f, (str, bytes)):
                # (filename, fileobj)
                f[1].close()
            elif hasattr(f, 'close'):
                f.close()
    return response


def upload_media(file_path, parent_id=None):
    """
    Uploads a file to GHL media storage.
    Returns a dict with 'fileId' and 'url' if successful, else None.
    """
    files = prepare_file_field(file_path, 'file')
    data = {
        'name': os.path.basename(file_path)
    }
    if parent_id:
        data['parentId'] = parent_id
    response = send_ghl_post('/medias/upload-file', files=files, data=data)
    if response.status_code in (200, 201):
        try:
            resp_json = response.json()
            return {
                'fileId': resp_json.get('fileId'),
                'url': resp_json.get('url')
            }
        except Exception as e:
            print(f"Error parsing upload response: {e}")
            return None
    else:
        print(f"Failed to upload {file_path}: {response.status_code} {response.text}")
        return None


def list_files(type_value='file', fetch_all='false'):
    """
    List uploaded files/folders from GHL media storage.
    type_value: 'file' (required by API)
    fetch_all: 'true' or 'false' (string, optional)
    Returns the API response as JSON.
    """
    endpoint = '/medias/files'
    headers = get_ghl_headers()
    params = {'type': str(type_value), 'fetchAll': str(fetch_all).lower()}
    response = requests.get(f"{GHL_API_BASE}{endpoint}", headers=headers, params=params)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            print(f"Error parsing list_files response: {e}")
            return None
    else:
        print(f"Failed to list files: {response.status_code} {response.text}")
        return None
