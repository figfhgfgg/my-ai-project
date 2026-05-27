import os
import time
import sys
import json
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder='templates', static_folder='static')

# Record application start time for uptime calculation
START_TIME = time.time()

# Data file persistence path
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            "cinnamon_roll_code": "CR-ROLL-99",
            "cinnamon_roll_name": "焦糖核桃肉桂捲",
            "afternoon_company": "未來創意科技有限公司",
            "afternoon_company_location": "台北市信義區"
        }

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

@app.route('/')
def index():
    """Serves the dashboard user interface."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Liveness check endpoint."""
    return jsonify({
        "status": "UP",
        "timestamp": time.time(),
        "details": {
            "app": "Flask Service",
            "port": 19191
        }
    }), 200

@app.route('/api/status')
def api_status():
    """Returns application run stats."""
    uptime = time.time() - START_TIME
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    return jsonify({
        "status": "online",
        "port": 19191,
        "uptime": uptime_str,
        "framework": "Flask",
        "python_version": sys.version.split()[0],
        "environment": os.environ.get("FLASK_ENV", "production")
    })

@app.route('/api/cinnamon', methods=['GET', 'POST'])
def api_cinnamon():
    """Gets or updates the favorite cinnamon roll code."""
    data = load_data()
    if request.method == 'POST':
        req_data = request.get_json() or {}
        if 'cinnamon_roll_code' in req_data:
            data['cinnamon_roll_code'] = req_data['cinnamon_roll_code']
        if 'cinnamon_roll_name' in req_data:
            data['cinnamon_roll_name'] = req_data['cinnamon_roll_name']
        if save_data(data):
            return jsonify({"status": "success", "data": data}), 200
        return jsonify({"status": "error", "message": "Failed to save data"}), 500
    
    return jsonify({
        "cinnamon_roll_code": data.get("cinnamon_roll_code", ""),
        "cinnamon_roll_name": data.get("cinnamon_roll_name", "")
    }), 200

@app.route('/api/company', methods=['GET', 'POST'])
def api_company():
    """Gets or updates the afternoon company."""
    data = load_data()
    if request.method == 'POST':
        req_data = request.get_json() or {}
        if 'afternoon_company' in req_data:
            data['afternoon_company'] = req_data['afternoon_company']
        if 'afternoon_company_location' in req_data:
            data['afternoon_company_location'] = req_data['afternoon_company_location']
        if save_data(data):
            return jsonify({"status": "success", "data": data}), 200
        return jsonify({"status": "error", "message": "Failed to save data"}), 500
        
    return jsonify({
        "afternoon_company": data.get("afternoon_company", ""),
        "afternoon_company_location": data.get("afternoon_company_location", "")
    }), 200


if __name__ == '__main__':
    # Start the server on port 19191
    app.run(host='0.0.0.0', port=19191, debug=True)
