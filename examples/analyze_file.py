#!/usr/bin/env python3
"""
Script to analyze Python source files using the MCP service
"""
import argparse
import requests
import json
import sys
from pathlib import Path
from datetime import datetime

def analyze_file(file_path, api_url="http://localhost:5000/v1/sca/analyze"):
    """
    Analyze a Python source file
    """
    try:
        # Read the source file
        code = Path(file_path).read_text()
        
        # Create a session ID based on filename and timestamp
        session_id = f"file_{Path(file_path).stem}_{datetime.now().timestamp()}"
        
        # Send for analysis
        response = requests.post(
            api_url,
            json={
                'code': code,
                'session_id': session_id,
                'file_path': str(file_path)
            },
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        return response.json()
        
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

def format_results(results):
    """Format the analysis results for display"""
    if not results.get('output', {}).get('results'):
        return "No vulnerabilities found."
        
    output = []
    for vuln in results['output']['results']:
        severity = vuln['severity'].upper()
        package = vuln['package']['name']
        version = vuln['package']['version']
        desc = vuln['description']
        
        output.append(f"[{severity}] {package} {version}")
        output.append(f"Description: {desc}")
        output.append(f"Recommendation: {vuln['recommendation']}")
        output.append("-" * 80)
        
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='Analyze Python source files for security vulnerabilities')
    parser.add_argument('file', help='Python file to analyze')
    parser.add_argument('--url', default='http://localhost:5000/v1/sca/analyze',
                      help='MCP service URL (default: http://localhost:5000/v1/sca/analyze)')
    parser.add_argument('--json', action='store_true',
                      help='Output raw JSON instead of formatted text')
    
    args = parser.parse_args()
    
    results = analyze_file(args.file, args.url)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results))

if __name__ == "__main__":
    main()
