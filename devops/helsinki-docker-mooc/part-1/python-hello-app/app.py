from flask import Flask, jsonify
import datetime
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to Python Hello App!',
        'timestamp': datetime.datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/info')
def info():
    return jsonify({
        'app_name': 'Python Hello App',
        'version': '1.0.0',
        'description': 'A simple Flask application for Docker demonstration',
        'endpoints': {
            '/': 'Home endpoint with basic info',
            '/health': 'Health check endpoint',
            '/info': 'Application information'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
