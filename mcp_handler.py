import json
import logging
from flask import request, jsonify, render_template
from flask_socketio import emit
from app import app, socketio, db
from models import Analysis, MCPSession
from code_analyzer import analyze_code
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@app.route('/')
def dashboard():
    recent_analyses = Analysis.query.order_by(Analysis.timestamp.desc()).limit(5).all()
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    active_sessions = MCPSession.query.filter(
        MCPSession.last_active >= hour_ago
    ).count()

    return render_template('dashboard.html', 
                         recent_analyses=recent_analyses,
                         active_sessions=active_sessions)

@app.route('/mcp/v1/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400

        # Perform analysis first
        analysis_results = analyze_code(data['code'])

        # Update session asynchronously after sending response
        @socketio.start_background_task
        def update_session():
            try:
                session = MCPSession.query.filter_by(session_id=session_id).first()
                if not session:
                    session = MCPSession(session_id=session_id)
                    db.session.add(session)

                analysis = Analysis(
                    file_path=data.get('file_path', 'unknown'),
                    status='completed',
                    results=analysis_results
                )
                db.session.add(analysis)
                db.session.commit()

                # Emit results via websocket
                socketio.emit('analysis_complete', {
                    'session_id': session_id,
                    'results': analysis_results
                })
            except Exception as e:
                logger.error(f"Background task error: {str(e)}")

        # Return results immediately
        return jsonify(analysis_results)

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    try:
        # Send initial data
        recent_analyses = Analysis.query.order_by(Analysis.timestamp.desc()).limit(5).all()
        active_sessions = MCPSession.query.filter(
            MCPSession.last_active >= datetime.utcnow() - timedelta(hours=1)
        ).count()

        emit('initial_data', {
            'recent_analyses': [
                {
                    'session_id': analysis.file_path,
                    'timestamp': analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': analysis.status
                } for analysis in recent_analyses
            ],
            'active_sessions': active_sessions
        })

        emit('connected', {'status': 'connected'})
    except Exception as e:
        logger.error(f"Error in connect handler: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    emit('disconnected', {'status': 'disconnected'})