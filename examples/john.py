import requests
import json
import os
from pprint import pprint
from datetime import datetime
try:
    from termcolor import colored  # For colored output
except ImportError:
    print("Install termcolor for colored output: `pip install termcolor`")
    def colored(text, *args, **kwargs):
        return text  # Fallback if not installed

# Replace with your Replit MCP server URL
BASE_URL = "https://mcp-sca-demo.yourusername.repl.co"  # Update this!

# Headers for POST requests
HEADERS = {"Content-Type": "application/json"}

def test_mcp_sca(endpoint, payload, test_name="Unnamed Test"):
    """Send a request to the MCP SCA server and return the response."""
    url = f"{BASE_URL}/{endpoint}"
    print(colored(f"Running: {test_name}", "cyan"))
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(colored(f"Error in {test_name}: {e}", "red"))
        return None

def print_results(test_name, result):
    """Display SCA results with color coding."""
    print(f"\n=== {test_name} ===")
    if result and result.get("status") == "success":
        if result["results"]:
            print(colored(f"Vulnerabilities found in {test_name}:", "yellow"))
            for vuln in result["results"]:
                print(colored(f"- {vuln['package']} ({vuln['version']})", "white"))
                print(f"  Issue: {vuln['vulnerability']}")
                print(colored(f"  CVE: {vuln['cve']}, Severity: {vuln['severity']}", "red" if vuln['severity'] in ["High", "Critical"] else "yellow"))
        else:
            print(colored("No vulnerabilities found!", "green"))
    else:
        print(colored("Failed or no valid response.", "red"))

def log_results(test_name, result):
    """Log results to a file for adopters to review later."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"sca_results_{timestamp}.txt", "a") as f:
        f.write(f"{test_name}:\n")
        f.write(json.dumps(result, indent=2) + "\n\n")

# Test Cases with Different Vulnerabilities
# Test 1: Vulnerable Django version
test1_payload = {"dependencies": "django==4.1.0"}  # Known vulns in older Django

# Test 2: Vulnerable Pillow (image processing lib)
test2_payload = {"dependencies": "pillow==9.0.0"}  # Pre-9.2.0 had CVEs

# Test 3: Mixed Python deps
test3_payload = {
    "dependencies": "django==4.1.0\npillow==9.0.0\ncryptography==38.0.1"
}  # Crypto should be safer

# Test 4: Node.js-style vulnerable package (simulated)
test4_payload = {"dependencies": "lodash==4.17.15"}  # Older lodash had vulns

# Test 5: Large multi-line input
test5_payload = {
    "dependencies": (
        "django==4.1.0\n"
        "pillow==9.0.0\n"
        "numpy==1.22.0\n"  # Older numpy, potential issues
        "lodash==4.17.15\n"
        "cryptography==38.0.1"
    )
}

# Test 6: Empty input (edge case)
test6_payload = {"dependencies": ""}

# Test 7: Malformed input (edge case)
test7_payload = {"dependencies": "broken_package==invalid_version!!!"}

def main():
    """Run all test cases and log results."""
    # Check server health
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print(colored("MCP Server is healthy!", "green"))
        else:
            print(colored("Warning: Server might be down.", "yellow"))
    except requests.RequestException:
        print(colored("Couldn’t reach server—check URL or network.", "red"))
        return

    # Run tests
    tests = [
        ("Test 1: Vulnerable Django", test1_payload),
        ("Test 2: Vulnerable Pillow", test2_payload),
        ("Test 3: Mixed Python Deps", test3_payload),
        ("Test 4: Node.js Lodash", test4_payload),
        ("Test 5: Large Multi-Dep", test5_payload),
        ("Test 6: Empty Input", test6_payload),
        ("Test 7: Malformed Input", test7_payload),
    ]

    for test_name, payload in tests:
        result = test_mcp_sca("mcp", payload, test_name)
        print_results(test_name, result)
        if result:
            log_results(test_name, result)

if __name__ == "__main__":
    print(colored("Starting MCP SCA Extended Test Suite...", "blue"))
    main()
    print(colored("Tests complete! Check sca_results_*.txt for logs.", "blue"))
