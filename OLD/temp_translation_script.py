import json

def load_json_robustly(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Apply the fixing logic from extract_specialties.py
        content = content.strip()
        if not content.startswith('[') and not content.endswith(']'):
            content = f"[{content}]"
        content = content.replace('}\r\n    },', '},{')
        content = content.replace('}\r\n    }', '}]')
        content = content.replace('{\r\n    "name"', '[{\r\n    "name"')
        data = json.loads(content)
    return data

# Load foreigner_specialities.json
foreigner_specialities_data = load_json_robustly("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\foreigner_specialities.json")

# Load university_details.json (corrected path)
university_details_data = load_json_robustly("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\university_details.json")

# Extract unique specialty names
unique_specialty_names = set()
for item in foreigner_specialities_data:
    if 'name' in item:
        unique_specialty_names.add(item['name'])

# Extract unique university names and descriptions
unique_university_names = set()
unique_university_descriptions = set()
for item in university_details_data:
    if 'name' in item:
        unique_university_names.add(item['name'])
    if 'description' in item:
        unique_university_descriptions.add(item['description'])

# Combine all unique texts for translation
all_texts_to_translate = unique_specialty_names.union(unique_university_names).union(unique_university_descriptions)

# Perform translations (simulated for now, will use actual translation in next step)
translated_texts = {}
for text in all_texts_to_translate:
    translated_texts[text] = f"{text}_ru" # Placeholder for actual translation

# Save the translated texts to a temporary file for later use
with open("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\translated_texts_temp.json", "w", encoding="utf-8") as f:
    json.dump(translated_texts, f, ensure_ascii=False, indent=4)

print("Unique texts extracted and simulated translations saved to translated_texts_temp.json")