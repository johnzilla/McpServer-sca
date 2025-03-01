"""
Example script demonstrating how to use the MCP-compliant code analysis API
"""
import requests
import json
from datetime import datetime

# Example Python code to analyze
test_code = """
import requests
from flask import Flask
import json

app = Flask(__name__)

@app.route('/data')
def get_data():
    response = requests.get('https://api.example.com/data')
    return json.loads(response.text)
"""

def analyze_code(code, api_url="http://localhost:5000/v1/sca/analyze"):
    """
    Send code to the analysis service and print results
    """
    session_id = f"test_{datetime.now().timestamp()}"
    
    response = requests.post(
        api_url,
        json={
            'code': code,
            'session_id': session_id,
            'file_path': 'test_script.py'
        }
    )
    
    if response.status_code == 200:
        results = response.json()
        print("Analysis Results:")
        print(json.dumps(results, indent=2))
        return results
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    print("Testing MCP Code Analysis Service...")
    analyze_code(test_code)
