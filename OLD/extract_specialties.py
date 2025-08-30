import json
import sys

unique_specialties = set()
language_ids = set()

with open('foreigner_specialities.json', 'r', encoding='utf-8') as f:
    content = f.read()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        content = content.strip()
        if not content.startswith('[') and not content.endswith(']'):
            content = f"[{content}]"
        
        content = content.replace('}\r\n    },', '},{')
        content = content.replace('}\r\n    }', '}]')
        content = content.replace('{\r\n    "name"', '[{\r\n    "name"')
        
        data = json.loads(content)


    for item in data:
        if 'name' in item and 'educationLanguageId' in item:
            unique_specialties.add(item['name'])
            if item['educationLanguageId'] is not None:
                language_ids.add(item['educationLanguageId'])

with open('specialties_output.txt', 'w', encoding='utf-8') as outfile:
    outfile.write("Unique Specialties:\n")
    for specialty in sorted(list(unique_specialties)):
        outfile.write(specialty + '\n')

    outfile.write("\nLanguage IDs found:\n")
    for lang_id in sorted(list(language_ids)):
        outfile.write(str(lang_id) + '\n')