import os
import time
import sys
import json
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
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

@app.route('/upload')
def upload_page():
    """Serves the S3 photo upload demo page."""
    return render_template('upload.html')

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


# ─────────────────────────────────────────────────────────────────────────────
# S3 Presigned Upload URL
# ─────────────────────────────────────────────────────────────────────────────
# Security note: NO access keys or secret keys are used here.
# boto3 automatically resolves credentials via the AWS credential chain:
#   1. ~/.aws/credentials (local development)
#   2. EC2 Instance Profile / IAM Role (production on EC2)
# ─────────────────────────────────────────────────────────────────────────────

S3_BUCKET  = "my-ai-bucket-jackydev"
S3_REGION  = "ap-east-2"          # 台北區域
S3_PREFIX  = "feature3/"           # 強制鎖定上傳路徑前綴
URL_EXPIRY = 600                   # 預簽名網址有效期：10 分鐘（600 秒）

# 允許上傳的 MIME 類型白名單
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


@app.route('/api/s3/presigned-upload', methods=['POST'])
def api_s3_presigned_upload():
    """
    生成 S3 預簽名 PUT 網址（Presigned URL）。

    前端以 POST 帶入 JSON body:
        { "filename": "photo.jpg", "content_type": "image/jpeg" }

    後端回傳:
        { "upload_url": "https://...", "s3_key": "feature3/photo.jpg" }

    安全保障：
    - S3 路徑強制鎖定在 feature3/ 前綴，前端無法繞過。
    - Content-Type 僅允許白名單內的圖片格式。
    - 網址 10 分鐘後自動失效。
    - 後端不持有任何 Access Key / Secret Key。
    """
    req_data = request.get_json(silent=True) or {}

    filename     = req_data.get("filename", "").strip()
    content_type = req_data.get("content_type", "image/jpeg").strip()

    # ── 輸入驗證 ──────────────────────────────────────────────────────────────
    if not filename:
        return jsonify({"error": "缺少必要欄位: filename"}), 400

    # 防止路徑穿越攻擊（Path Traversal）
    safe_filename = os.path.basename(filename)
    if not safe_filename or safe_filename in (".", ".."):
        return jsonify({"error": "無效的檔名"}), 400

    if content_type not in ALLOWED_CONTENT_TYPES:
        return jsonify({
            "error": f"不允許的 Content-Type: {content_type}。"
                     f"允許的類型: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
        }), 400

    # ── 強制鎖定 S3 存放路徑前綴 ──────────────────────────────────────────────
    s3_key = f"{S3_PREFIX}{safe_filename}"

    # ── 生成預簽名網址（boto3 自動使用本地憑證或 IAM Role）────────────────────
    # 注意：ContentType 已被納入 SigV4 簽名計算，前端 PUT 時必須傳送完全相同的值。
    try:
        s3_client = boto3.client(
            "s3",
            region_name=S3_REGION,          # ap-east-2 台北區域
            config=Config(signature_version="s3v4")   # ap-east-2 強制要求 SigV4
        )

        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket":      S3_BUCKET,
                "Key":         s3_key,
                "ContentType": content_type,  # 已納入簽名，前端必須一致
            },
            ExpiresIn=URL_EXPIRY,
            HttpMethod="PUT",
        )

        # Debug log：服務啟動後可在終端機確認網址已成功生成
        logging.info("[S3] presigned URL generated: key=%s expires_in=%ds", s3_key, URL_EXPIRY)
    except NoCredentialsError:
        logging.exception("[S3] 找不到 AWS 憑證。請確認 ~/.aws/credentials 或 EC2 IAM Role 已正確設定。")
        return jsonify({"error": "伺服器 AWS 憑證未設定，請聯絡管理員。"}), 500
    except ClientError as exc:
        logging.exception("[S3] 生成預簽名網址失敗")
        return jsonify({"error": f"S3 錯誤: {exc.response['Error']['Message']}"}), 500

    return jsonify({
        "upload_url": presigned_url,
        "s3_key":     s3_key,
        "expires_in": URL_EXPIRY,
    }), 200


if __name__ == '__main__':
    # Start the server on port 19191
    app.run(host='0.0.0.0', port=19191, debug=True)
