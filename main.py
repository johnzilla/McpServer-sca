from app import app, socketio

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True,
        use_reloader=True,
        log_output=True,
        websocket_ping_interval=25,  # Keep connections alive
        websocket_ping_timeout=120   # Longer timeout for analysis
    )