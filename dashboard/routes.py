from flask import render_template
from flask_socketio import emit
from . import dashboard
from models import Analysis, MCPSession
from datetime import datetime, timedelta
from app import socketio

@dashboard.route('/')
def index():
    """Admin dashboard homepage"""
    recent_analyses = Analysis.query.order_by(Analysis.timestamp.desc()).limit(5).all()
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    active_sessions = MCPSession.query.filter(
        MCPSession.last_active >= hour_ago
    ).count()

    return render_template('dashboard/index.html', 
                         recent_analyses=recent_analyses,
                         active_sessions=active_sessions)

@socketio.on('connect')
def handle_connect():
    """WebSocket connection handler for dashboard"""
    try:
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
    except Exception as e:
        emit('error', {'message': str(e)})
