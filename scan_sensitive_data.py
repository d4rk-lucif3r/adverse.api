#!/usr/bin/env python3
"""
Scan repository for potential sensitive data.
This script scans files in the repository for patterns that might be sensitive data.
"""

import os
import re
import sys
from pathlib import Path

# Regex patterns for common sensitive data
PATTERNS = {
    'api_key': r'(?i)(api[_-]?key|access[_-]?key|secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{16,})["\']\s*',
    'mongodb_id': r'(?i)["\']\$oid["\']\s*:\s*["\']([\w]{24})[\'"]',
    'aws_key': r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)["\']\s*[:=]\s*["\']?([a-zA-Z0-9/+]{20,})[\'"]',
    'password': r'(?i)(password|passwd|pwd)["\']\s*[:=]\s*["\']([\w@#$%^&*-]{8,})[\'"]',
    'connection_string': r'(?i)(mongodb://|postgres://|mysql://|jdbc:)[\w:@\.\-/]+',
}

# File extensions to scan
EXTENSIONS_TO_SCAN = {
    '.py', '.js', '.json', '.ts', '.yaml', '.yml', '.xml', '.csv', '.md', '.txt', '.env'
}

# Directories to ignore
DIRS_TO_IGNORE = {
    '.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build'
}

def scan_file(file_path):
    """
    Scan a file for sensitive data patterns.
    Returns a list of findings with line numbers.
    """
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            for pattern_name, pattern in PATTERNS.items():
                matches = re.findall(pattern, line)
                if matches:
                    # Mask the actual sensitive data before logging
                    masked_line = re.sub(pattern, lambda m: re.sub(r'[a-zA-Z0-9/+]{4,}', lambda x: x.group(0)[:2] + '*' * (len(x.group(0)) - 4) + x.group(0)[-2:], m.group(0)), line)
                    findings.append({
                        'file': file_path,
                        'line': i,
                        'pattern': pattern_name,
                        'masked_content': masked_line.strip()
                    })
    except Exception as e:
        print(f"Error scanning {file_path}: {str(e)}")
    
    return findings

def scan_directory(directory):
    """
    Recursively scan a directory for sensitive data.
    """
    all_findings = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in DIRS_TO_IGNORE]
        
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            if ext in EXTENSIONS_TO_SCAN:
                findings = scan_file(file_path)
                all_findings.extend(findings)
    
    return all_findings

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Scanning repository: {repo_dir}")
    
    findings = scan_directory(repo_dir)
    
    if findings:
        print(f"\nFound {len(findings)} potential sensitive data instances:")
        for finding in findings:
            print(f"\n{finding['file']}:{finding['line']} - {finding['pattern']}:")
            print(f"  {finding['masked_content']}")
    else:
        print("\nNo sensitive data found.")

if __name__ == "__main__":
    main()