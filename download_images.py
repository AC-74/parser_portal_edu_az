import json
import requests
import os

# Define project root for relative path calculation
project_root = 'C:/Users/Fluffy/Downloads/parser_portal_edu_az/'

def download_and_update_images(university_details_path, images_dir):
    with open(university_details_path, 'r', encoding='utf-8') as f:
        universities = json.load(f)

    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    updated_universities = []
    for uni in universities:
        atis_id = uni['ATIS_ID']
        photo_url = uni.get('photo_url')
        
        if photo_url:
            # Check if the photo_url is a web URL before attempting to download
            if photo_url.startswith('http://') or photo_url.startswith('https://'):
                try:
                    response = requests.get(photo_url, stream=True, timeout=10)
                    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                    # Determine file extension
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'gif' in content_type:
                        ext = '.gif'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        print(f"Warning: Unknown content type for {atis_id} ({content_type}). Skipping download.")
                        # Fallback to placeholder relative path
                        uni['photo_url'] = os.path.relpath(os.path.join(images_dir, 'placeholder.png'), start=project_root).replace('\\', '/')
                        updated_universities.append(uni)
                        continue

                    local_image_path = os.path.join(images_dir, f"{atis_id}{ext}")
                    with open(local_image_path, 'wb') as out_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            out_file.write(chunk)
                    print(f"Downloaded {atis_id} to {local_image_path}")
                    # Update to local relative path with forward slashes
                    uni['photo_url'] = os.path.relpath(local_image_path, start=project_root).replace('\\', '/')
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download image for {atis_id} from {photo_url}: {e}")
                    # Fallback to placeholder relative path
                    uni['photo_url'] = os.path.relpath(os.path.join(images_dir, 'placeholder.png'), start=project_root).replace('\\', '/')
            else:
                # If it's not a web URL, it's already a local path or invalid, so use placeholder
                print(f"Skipping download for {atis_id}: photo_url is not a web URL ({photo_url}). Using placeholder.")
                uni['photo_url'] = os.path.relpath(os.path.join(images_dir, 'placeholder.png'), start=project_root).replace('\\', '/')
        else:
            print(f"No photo_url found for {atis_id}. Using placeholder.")
            # Fallback to placeholder relative path
            uni['photo_url'] = os.path.relpath(os.path.join(images_dir, 'placeholder.png'), start=project_root).replace('\\', '/')
        
        updated_universities.append(uni)

    # Debugging: Print photo_url before writing
    for uni in updated_universities:
        print(f"DEBUG: {uni['ATIS_ID']} photo_url before write: {uni['photo_url']}")

    try:
        with open(university_details_path, 'w', encoding='utf-8') as f:
            json.dump(updated_universities, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {university_details_path} with local image paths.")
    except Exception as e:
        print(f"ERROR: Failed to write to {university_details_path}: {e}")

# Define paths
university_details_file = os.path.join(project_root, 'university_details.json')
images_directory = os.path.join(project_root, 'images')

# Run the function
download_and_update_images(university_details_file, images_directory)
