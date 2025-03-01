# McpServer-sca

A Flask-based Software Composition Analysis (SCA) server providing advanced dependency security insights for Python projects. The service follows the MCP specification for standardized tool integration.

## API Reference

### Analyze Code Endpoint

```
POST /v1/sca/analyze
```

#### Request Format

```json
{
  "code": "string",
  "session_id": "string (optional)",
  "file_path": "string (optional)"
}
```

#### Response Format

```json
{
  "status": "success",
  "output": {
    "schema_version": "mcp-0.1",
    "timestamp": "ISO-8601 timestamp",
    "analysis_type": "security_composition",
    "status": "success",
    "results": [
      {
        "type": "vulnerability",
        "severity": "low|medium|high",
        "package": {
          "name": "string",
          "version": "string"
        },
        "identifier": "CVE-ID",
        "description": "string",
        "recommendation": "string",
        "metadata": {
          "cve": "string",
          "discovered_at": "ISO-8601 timestamp"
        }
      }
    ]
  }
}
```

## Example Usage

```python
import requests
import json

code = """
import requests
import json

def fetch_data():
    response = requests.get('https://api.example.com/data')
    return json.loads(response.text)
"""

response = requests.post(
    'https://your-domain.com/v1/sca/analyze',
    json={
        'code': code,
        'session_id': 'optional-session-id'
    }
)

results = response.json()
print(json.dumps(results, indent=2))
```

## Admin Dashboard

Access the admin dashboard at `/dashboard` to monitor:
- Real-time analysis metrics
- Active sessions
- Performance statistics
- Recent analyses

## Performance

The service typically processes requests within milliseconds, with total round-trip time varying based on network conditions. Each analysis request includes timing information in the response metadata.

## Deployment

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set required environment variables:
   - `SESSION_SECRET`: For session management
   - `DATABASE_URL`: PostgreSQL connection string
4. Run the application: `python main.py`

The service will be available on port 5000 by default.

## Security Considerations

- The API endpoint is public and does not require authentication
- The admin dashboard should be protected in production
- Rate limiting may be applied based on usage patterns