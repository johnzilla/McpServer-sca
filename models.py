from datetime import datetime, timedelta
from app import db
import hashlib
import json

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    results = db.Column(db.JSON)

class MCPSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="active")

class AnalysisCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_hash = db.Column(db.String(64), unique=True, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def get_code_hash(code):
        """Generate a unique hash for the code"""
        return hashlib.sha256(code.encode()).hexdigest()

    @classmethod
    def get_cached_results(cls, code):
        """Get cached results if they exist and haven't expired"""
        code_hash = cls.get_code_hash(code)
        cache_entry = cls.query.filter_by(code_hash=code_hash).first()

        if cache_entry and cache_entry.expires_at > datetime.utcnow():
            return cache_entry.results
        return None

    @classmethod
    def cache_results(cls, code, results, expire_hours=24):
        """Cache analysis results"""
        code_hash = cls.get_code_hash(code)
        expires_at = datetime.utcnow() + timedelta(hours=expire_hours)

        cache_entry = cls(
            code_hash=code_hash,
            results=results,
            expires_at=expires_at
        )
        db.session.add(cache_entry)
        db.session.commit()