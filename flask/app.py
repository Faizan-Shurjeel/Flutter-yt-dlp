from flask import Flask, request, jsonify, render_template, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/series.json')
def series():
    return send_from_directory(os.path.dirname(__file__), 'series.json')

@app.route('/get_media', methods=['POST'])
def get_media():
    data = request.get_json()
    url = data.get('url')
    cookies_file_path = 'cookies.txt'  # Path to your cookies file
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'cookies': cookies_file_path
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [info])
            media_urls = []

            for format in formats:
                format_note = format.get('format_note') or format.get('height') or format.get('quality') or 'Unknown Format'
                if format.get('vcodec') != 'none' and format.get('acodec') != 'none':
                    media_urls.append({
                        'format': format_note,
                        'url': format.get('url'),
                        'ext': format.get('ext')
                    })

        if not media_urls:
            return jsonify({'error': 'No suitable formats found with both audio and video'}), 404

        return jsonify({'media_urls': media_urls}), 200

    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'Error downloading media: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
