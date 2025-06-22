from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format_choice = data.get('format', 'mp4')
    print(f"[DEBUG] URL: {url}, Format: {format_choice}")

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ext = 'mp3' if format_choice == 'mp3' else 'mp4'
    ydl_opts = {
        'format': 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': ext,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }] if format_choice == 'mp3' else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base_filename = os.path.basename(filename)
            final_file_path = os.path.join(DOWNLOAD_DIR, base_filename)
            if not os.path.isfile(final_file_path):
                raise FileNotFoundError("File not created.")
            thumbnail = info.get('thumbnail', '')
        return jsonify({
            'success': True,
            'filename': base_filename,
            'thumbnail': thumbnail
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<path:filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
    else:
        abort(404)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
