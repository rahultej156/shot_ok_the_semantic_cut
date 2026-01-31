import json
import requests
import sys

# Since the file contains concatenated JSON objects (not a single list),
# we need to parse it manually.
INPUT_FILE = "d:/Rahul/cineAI/the_godfather_scene_5 to 10.json"
API_URL = "http://localhost:8000/api/v1/index"

def parse_multiple_json_objects(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple hack: The file content is like {obj1}\n{obj2}...
    # We can try to split by "}\n{" or just scan for start/end braces if simple.
    # A more robust way for concatenated JSON is using a decoder.
    
    decoder = json.JSONDecoder()
    pos = 0
    objs = []
    
    while pos < len(content):
        # Skip whitespace
        content = content.lstrip()
        if not content:
            break
            
        try:
            obj, idx = decoder.raw_decode(content)
            objs.append(obj)
            content = content[idx:]
        except json.JSONDecodeError as e:
            print(f"Parsing finished or error at pos {pos}: {e}")
            break
            
    return objs

def index_data():
    print(f"Reading {INPUT_FILE}...")
    try:
        scenes = parse_multiple_json_objects(INPUT_FILE)
        print(f"Found {len(scenes)} scenes.")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    payload = {
        "scenes": scenes,
        "recreate_collection": True  # As requested, clear existing data
    }

    print("Sending data to API...")
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print("\nSuccess!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nError {response.status_code}:")
            print(response.text)
    except Exception as e:
        print(f"Failed to connect to API: {e}")

if __name__ == "__main__":
    index_data()
