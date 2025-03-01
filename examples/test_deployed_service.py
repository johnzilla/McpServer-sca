"""
Test script for verifying the deployed MCP service
"""
import requests
import json
from datetime import datetime

def test_service(base_url):
    """
    Test the deployed MCP service with sample code
    """
    # Test code that includes known vulnerable packages
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
    
    # Test the analysis endpoint
    print(f"\nTesting MCP Service at {base_url}")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{base_url}/v1/sca/analyze",
            json={
                'code': test_code,
                'session_id': f"test_{datetime.now().timestamp()}",
                'file_path': 'test_script.py'
            },
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 200:
            results = response.json()
            print("\nAnalysis Results:")
            print(json.dumps(results, indent=2))
            
            # Verify MCP compliance
            if 'output' in results:
                output = results['output']
                print("\nMCP Compliance Check:")
                print(f"✓ Schema Version: {output.get('schema_version')}")
                print(f"✓ Analysis Type: {output.get('analysis_type')}")
                print(f"✓ Status: {output.get('status')}")
                print(f"✓ Results Count: {len(output.get('results', []))}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error testing service: {str(e)}")
        return False

if __name__ == "__main__":
    # Replace with your deployed Replit URL
    deployment_url = input("Enter your deployed Replit URL (e.g., https://your-app.repl.co): ")
    test_service(deployment_url.rstrip('/'))
