import ast
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    @staticmethod
    def analyze_ast(code):
        try:
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(f"{node.module}")

            return imports
        except Exception as e:
            logger.error(f"AST analysis failed: {str(e)}")
            return []

    @staticmethod
    def check_security(imports):
        # Known vulnerable package versions with severity
        vulnerable_packages = {
            'requests': {
                'version': '2.28.1',
                'cve': 'CVE-2023-XYZ',
                'severity': 'Medium',
                'description': 'Potential security issue...'
            },
            'flask': {
                'version': '2.0.1',
                'cve': 'CVE-2021-ABC',
                'severity': 'Low',
                'description': 'Outdated version...'
            }
        }

        security_warnings = []
        for imp in imports:
            base_package = imp.split('.')[0].lower()
            if base_package in vulnerable_packages:
                package_info = vulnerable_packages[base_package]
                security_warnings.append({
                    'package': base_package,
                    'version': package_info['version'],
                    'description': package_info['description'],
                    'cve': package_info['cve'],
                    'severity': package_info['severity']
                })

        return security_warnings

def analyze_code(code):
    analyzer = CodeAnalyzer()
    imports = analyzer.analyze_ast(code)
    vulnerabilities = analyzer.check_security(imports)

    mcp_output = {
        "schema_version": "mcp-0.1",
        "timestamp": datetime.utcnow().isoformat(),
        "analysis_type": "security_composition",
        "status": "success",
        "results": []
    }

    for vuln in vulnerabilities:
        mcp_output["results"].append({
            "type": "vulnerability",
            "severity": vuln["severity"].lower(),
            "package": {
                "name": vuln["package"],
                "version": vuln["version"]
            },
            "identifier": vuln["cve"],
            "description": vuln["description"],
            "recommendation": f"Update {vuln['package']} to a newer version",
            "metadata": {
                "cve": vuln["cve"],
                "discovered_at": datetime.utcnow().isoformat()
            }
        })

    return {
        'status': 'success',
        'output': mcp_output
    }