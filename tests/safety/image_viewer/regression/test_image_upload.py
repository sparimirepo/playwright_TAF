import os
import pytest
import requests
from utils.YAML_Loader import YamlLoader

# Load the YAML test data
image_upload_yaml_path = 'testData/image_upload/image_viewer.yaml'
image_upload_data = YamlLoader.load_yaml(image_upload_yaml_path)['image_uploads']

@pytest.mark.parametrize("image_data", image_upload_data)
def test_image_upload(self, image_data):
    '''
    This test supports both local repository images and high-quality images from a remote bucket.
    '''

    # Determine the image path based on source type
    temp_path = None
    if image_data.get('source', 'local') == 'local':
        # Build local file path
        image_path = os.path.join('testData', 'image_upload', 'images', image_data['file_name'])
    else:
        # Download the file from the external URL to a temp file
        file_url = image_data['file_url']
        temp_path = os.path.join('/tmp', f"test_upload_{os.path.basename(file_url)}")
        response = requests.get(file_url)
        response.raise_for_status()
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        image_path = temp_path

    # Playwright file upload (adapt selector/method as needed)
    self.admin_page.navigate_to_image_upload_form()
    self.admin_page.upload_file_to_form(image_path)
    self.admin_page.fill_image_description(image_data.get('description', ''))
    self.admin_page.submit_image_upload()
    self.admin_page.validate_upload_success()

    # Clean up downloaded temp files after test
    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)
