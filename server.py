from flask import Flask, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        result = subprocess.run(['python', 'create_ki_video.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"status": "success", "video_path": "/tmp/final_tiktok.mp4"})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
