from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Create downloads folder
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        filename = f"{DOWNLOAD_FOLDER}/video_%(id)s.mp4"
        
        # Run yt-dlp
        subprocess.run(
            ['yt-dlp', '-f', 'best', '-o', filename, url],
            check=True,
            capture_output=True,
            timeout=300
        )
        
        return jsonify({
            'success': True,
            'message': 'Video downloaded successfully!'
        })
    
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to download video. Check URL.'}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Download took too long'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Backend is running!'})

if __name__ == '__main__':
    app.run(debug=False)