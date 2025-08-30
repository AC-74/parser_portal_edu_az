import json
from pathlib import Path

# Load simulated translations
translated_texts_temp_path = Path("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\translated_texts_temp.json")
with open(translated_texts_temp_path, 'r', encoding='utf-8') as f:
    simulated_translations = json.load(f)

# Load extracted UNI_MAP
uni_map_temp_path = Path("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\uni_map_temp.json")
with open(uni_map_temp_path, 'r', encoding='utf-8') as f:
    uni_map_from_client = json.load(f)

# Load extracted SPEC_MAP
spec_map_temp_path = Path("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\spec_map_temp.json")
with open(spec_map_temp_path, 'r', encoding='utf-8') as f:
    spec_map_from_client = json.load(f)

# Create full translation map
full_translation_map = {}

# Add simulated translations first
for az_text, ru_text_simulated in simulated_translations.items():
    actual_ru_text = ru_text_simulated[:-3] if ru_text_simulated.endswith("_ru") else ru_text_simulated
    full_translation_map[az_text] = actual_ru_text

# Overlay with hardcoded translations from client.py (prioritize these)
for az_text, ru_text in uni_map_from_client.items():
    full_translation_map[az_text] = ru_text

for az_text, ru_text in spec_map_from_client.items():
    full_translation_map[az_text] = ru_text

# Save the full translation map to a new JSON file
full_translation_map_path = Path("C:\\Users\\Fluffy\\Downloads\\parser_portal_edu_az\\full_translation_map.json")
with open(full_translation_map_path, 'w', encoding='utf-8') as f:
    json.dump(full_translation_map, f, ensure_ascii=False, indent=4)

print(f"Full translation map saved to {full_translation_map_path}")
