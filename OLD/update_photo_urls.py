import json
from pathlib import Path

def update_university_photo_urls(university_details_path: Path, images_dir_name: str = "images"):
    try:
        with open(university_details_path, 'r', encoding='utf-8') as f:
            university_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {university_details_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {university_details_path}.")
        return

    updated_count = 0
    for university in university_data:
        atis_id = university.get("ATIS_ID")
        photo_url = university.get("photo_url")

        if atis_id and photo_url and photo_url.startswith("http"):
            local_filename = f"{atis_id}.jpg"
            local_path_relative = Path(images_dir_name) / local_filename
            
            # Check if the local file actually exists before updating the URL
            # This assumes the images have already been downloaded by cli.py
            if (university_details_path.parent / local_path_relative).exists():
                university["photo_url"] = str(local_path_relative)
                updated_count += 1
            else:
                print(f"Warning: Local image for {atis_id} not found at {university_details_path.parent / local_path_relative}. Skipping update for this entry.")

    if updated_count > 0:
        with open(university_details_path, 'w', encoding='utf-8') as f:
            json.dump(university_data, f, ensure_ascii=False, indent=4)
        print(f"Updated {updated_count} photo URLs in {university_details_path}.")
    else:
        print("No photo URLs needed updating in university_details.json.")

if __name__ == "__main__":
    university_details_file = Path("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\university_details.json")
    update_university_photo_urls(university_details_file)
