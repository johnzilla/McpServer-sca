from flask import jsonify, request, render_template
from . import api
from code_analyzer import analyze_code
from models import Analysis, MCPSession, AnalysisCache
from app import db
from datetime import datetime

@api.route('/v1/sca/analyze', methods=['POST'])
def analyze():
    """
    Core MCP-compliant analysis endpoint.
    Accepts code submission and returns analysis results in MCP-compliant JSON format.
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        # Check cache first
        cached_results = AnalysisCache.get_cached_results(data['code'])
        if cached_results:
            return jsonify(cached_results)

        # Perform analysis
        analysis_results = analyze_code(data['code'])

        # Cache the results
        AnalysisCache.cache_results(data['code'], analysis_results)

        # Store analysis results asynchronously
        session_id = data.get('session_id', f'analysis_{datetime.utcnow().timestamp()}')
        analysis = Analysis(
            file_path=data.get('file_path', 'unknown'),
            status='completed',
            results=analysis_results
        )
        db.session.add(analysis)
        db.session.commit()

        return jsonify(analysis_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/docs')
def api_docs():
    """
    Serve the API documentation page
    """
    return render_template('api_docs.html')