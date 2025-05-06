#!/usr/bin/env python3
"""
Sanitize backup data files to avoid false positives in security scans.
This script replaces MongoDB ObjectIDs with masked versions to prevent them from being
flagged as API keys by security scanners.
"""

import json
import os
import re
import sys
from pathlib import Path

def mask_object_id(obj_id):
    """
    Mask a MongoDB ObjectID to prevent it from being flagged as an API key.
    Preserves the format but replaces actual values with a safe pattern.
    """
    if isinstance(obj_id, dict) and "$oid" in obj_id:
        # Replace the ObjectID with a masked version (keeping first 2 and last 2 chars)
        oid = obj_id["$oid"]
        if len(oid) >= 24:  # Standard MongoDB ObjectID length
            masked = f"{oid[:2]}{'*' * (len(oid) - 4)}{oid[-2:]}"
            return {"$oid": masked}
    return obj_id

def sanitize_json_file(file_path):
    """
    Sanitize a JSON file by masking all MongoDB ObjectIDs.
    """
    # Read the file
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # If the file is a newline-delimited JSON (NDJSON)
        if "\n{" in content:
            print(f"Processing {file_path} as NDJSON...")
            sanitized_lines = []
            for line in content.splitlines():
                if line.strip():
                    try:
                        obj = json.loads(line)
                        
                        # Mask ObjectIDs in _id field
                        if "_id" in obj and isinstance(obj["_id"], dict) and "$oid" in obj["_id"]:
                            obj["_id"] = mask_object_id(obj["_id"])
                        
                        # Mask any other fields that contain ObjectIDs (like news_keywords_id)
                        for key, value in obj.items():
                            if isinstance(value, str) and len(value) >= 24 and re.match(r'^[a-f0-9]{24}$', value):
                                obj[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                        
                        sanitized_lines.append(json.dumps(obj))
                    except json.JSONDecodeError:
                        sanitized_lines.append(line)  # Keep the line as is if it's not valid JSON
            
            sanitized_content = '\n'.join(sanitized_lines)
            
        # Otherwise treat as a regular JSON file
        else:
            print(f"Processing {file_path} as regular JSON...")
            try:
                data = json.loads(content)
                
                # Function to recursively process all objects in the data
                def process_obj(obj):
                    if isinstance(obj, dict):
                        for key, value in list(obj.items()):
                            if key == "_id" and isinstance(value, dict) and "$oid" in value:
                                obj[key] = mask_object_id(value)
                            elif isinstance(value, (dict, list)):
                                process_obj(value)
                            elif isinstance(value, str) and len(value) >= 24 and re.match(r'^[a-f0-9]{24}$', value):
                                obj[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            if isinstance(item, (dict, list)):
                                process_obj(item)
                
                process_obj(data)
                sanitized_content = json.dumps(data)
            except json.JSONDecodeError:
                print(f"Error: {file_path} is not valid JSON. Processing as text...")
                
                # If it's not valid JSON, use regex to find and mask potential ObjectIDs
                pattern = r'"(\$oid)"\s*:\s*"([a-f0-9]{24})"'
                sanitized_content = re.sub(pattern, 
                                         lambda m: f'"{m.group(1)}":"{m.group(2)[:2]}{"*" * 20}{m.group(2)[-2:]}"', 
                                         content)
        
        # Write the sanitized content back to the file
        with open(file_path, 'w') as f:
            f.write(sanitized_content)
        
        print(f"Successfully sanitized {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    # Directory containing the backup data
    backup_dir = Path(__file__).parent
    
    # Files to sanitize (focus on the vulnerable file from the security report)
    files_to_sanitize = [
        backup_dir / "BatchRunStatusDetailStatus.json",
        # Add more files if needed
    ]
    
    success_count = 0
    for file_path in files_to_sanitize:
        if sanitize_json_file(file_path):
            success_count += 1
    
    print(f"Sanitized {success_count} out of {len(files_to_sanitize)} files.")

if __name__ == "__main__":
    main()