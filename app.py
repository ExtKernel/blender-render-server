import os
import subprocess
import re
from flask import Flask, request, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'result'
ALLOWED_EXTENSIONS = {'blend'}  # Add other allowed file extensions if needed

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def render():
    return render_template("upload.html")


@app.route('/result', methods=['POST'])
def result():
    if request.method != 'POST':
        abort(405)  # Method Not Allowed

    if 'file' not in request.files:
        return render_template('error.html', message="No file part"), 400

    file = request.files['file']

    if file.filename == '':
        return render_template('error.html', message="No selected file"), 400

    if not allowed_file(file.filename):
        return render_template('error.html', message="File type not allowed"), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
    except Exception as e:
        return render_template('error.html', message=f"Error saving file: {str(e)}"), 500

    try:
        cmd = ['blender', '-b', filepath, '-o', f'./{RESULT_FOLDER}/{filename}', '-f', '1', '--', '--cycles-device',
               'CUDA']
        render_result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        saved_pattern = re.search(r"Saved: '.*\/([^\/]+)'", render_result.stdout)
        if not saved_pattern:
            raise ValueError("Couldn't find saved file information in output")

        rendered_filename = saved_pattern.group(1)
        return render_template('success.html', filename=rendered_filename)

    except subprocess.CalledProcessError as e:
        return render_template('error.html', message=f"Render process failed: {e.stderr}"), 500
    except Exception as e:
        return render_template('error.html', message=f"Error during rendering: {str(e)}"), 500


@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(debug=False)  # Set debug=False in production
