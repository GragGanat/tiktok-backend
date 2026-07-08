from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
from pathlib import Path
import uuid

app = Flask(__name__)
CORS(app)

# Create a temp folder for downloads
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Generate a unique filename for the downloaded video
        unique_filename = f"video_{uuid.uuid4()}.mp4"
        filepath = Path(DOWNLOAD_FOLDER) / unique_filename

        # Run yt-dlp to download the video
        subprocess.run(
            ["yt-dlp", "-f", "best", "-o", str(filepath), url],
            check=True,
            capture_output=True,
            timeout=300 # Set a timeout for the download process
        )

        # Send the file to the client
        return send_file(
            str(filepath),
            mimetype="video/mp4",
            as_attachment=True,
            download_name=unique_filename
        )

    except subprocess.CalledProcessError as e:
        # Log the error output for debugging
        print(f"yt-dlp error: {e.stderr.decode()}")
        return jsonify({"error": "Failed to download video. Check URL or try again.", "details": e.stderr.decode()}), 400
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Download took too long. Please try again.", "details": "Timeout after 300 seconds"}), 400
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the downloaded file after sending (if it exists)
        if filepath.exists():
            os.remove(filepath)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Backend is running!"})

if __name__ == "__main__":
    app.run(debug=False)
