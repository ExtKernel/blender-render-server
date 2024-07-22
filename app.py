import os
from datetime import datetime
import shutil
import subprocess
import re
from flask import Flask, request, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration constants
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
STATIC_FOLDER = os.path.join(RESULT_FOLDER, 'static')
ANIMATED_FOLDER = os.path.join(RESULT_FOLDER, 'animated')
ALLOWED_EXTENSIONS = {'blend'}  # Add other allowed file extensions if needed

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(ANIMATED_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Check if the file extension is allowed.

    :param filename: Name of the file to check
    :return: Boolean indicating if the file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def render():
    """Render the upload page."""
    return render_template("upload.html")


@app.route('/static/result', methods=['POST'])
def static_result():
    """
    Handle static render requests.

    Process uploaded .blend file and render a single frame.
    """
    cleanup_folders(UPLOAD_FOLDER, STATIC_FOLDER)
    check_request(request)

    file = request.files['file']
    check_file(file)

    filename = secure_filename(f'{file.filename}_{datetime.now()}')
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
    except Exception as e:
        return render_template('error.html', message=f"Error saving file: {str(e)}"), 500

    try:
        rendered_filename = render_static(filename, filepath)
        return render_template('success.html', filename=rendered_filename, animated=False)
    except subprocess.CalledProcessError as e:
        return render_template('error.html', message=f"Render process failed: {e.stderr}"), 500
    except Exception as e:
        return render_template('error.html', message=f"Error during rendering: {str(e)}"), 500


@app.route('/animated/result', methods=['POST'])
def animated_result():
    """
    Handle animated render requests.

    Process uploaded .blend file and render multiple frames for animation.
    """
    cleanup_folders(UPLOAD_FOLDER, ANIMATED_FOLDER)
    check_request(request)

    file = request.files['file']
    check_file(file)

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    start_frame = request.form.get('start_frame', '1')  # Default to '1' if not provided
    end_frame = request.form.get('end_frame', '250')  # Default to '250' if not provided

    try:
        file.save(filepath)
    except Exception as e:
        return render_template('error.html', message=f"Error saving file: {str(e)}"), 500

    try:
        rendered_filename = render_animated(filename, filepath, int(start_frame), int(end_frame))
        return render_template('success.html', filename=rendered_filename, animated=True)
    except subprocess.CalledProcessError as e:
        return render_template('error.html', message=f"Render process failed: {e.stderr}"), 500
    except Exception as e:
        return render_template('error.html', message=f"Error during rendering: {str(e)}"), 500


@app.route('/download/<filename>')
def download(filename):
    """
    Handle file download requests.

    :param filename: Name of the file to download
    """
    animated = request.args.get('animated', 'false').lower() == 'true'
    folder = ANIMATED_FOLDER if animated else STATIC_FOLDER

    try:
        return_value = send_from_directory(folder, filename, as_attachment=True)
        return return_value
    except FileNotFoundError:
        abort(404)


def render_static(filename, filepath):
    """
    Render a single frame from a .blend file.

    :param filename: Name of the .blend file
    :param filepath: Path to the .blend file
    :return: Name of the rendered file
    """
    cmd = [
        'blender',
        '-b', filepath,
        '-o', f'./{STATIC_FOLDER}/{filename}',
        '-f', '1',
        '--',
        '--cycles-device', 'CUDA'
    ]
    render_result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    saved_pattern = re.search(r"Saved: '.*\/([^\/]+)'", render_result.stdout)
    if not saved_pattern:
        raise ValueError("Couldn't find saved file information in output")

    return saved_pattern.group(1)


def render_animated(filename, filepath, start_frame, end_frame):
    """
    Render multiple frames from a .blend file for animation.

    :param filename: Name of the .blend file
    :param filepath: Path to the .blend file
    :param start_frame: Starting frame number
    :param end_frame: Ending frame number
    :return: Name of the zip file containing rendered frames
    """
    animated_file_result_folder = os.path.join(ANIMATED_FOLDER, filename)
    os.makedirs(animated_file_result_folder, exist_ok=True)

    cmd = [
        'blender',
        '-b', filepath,
        '-o', f'./{animated_file_result_folder}/{filename}',
        '-s', str(start_frame),
        '-e', str(end_frame),
        '-a',
        '--',
        '--cycles-device', 'CUDA'
    ]
    render_result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    saved_pattern = re.search(r"Saved: '.*\/([^\/]+)'", render_result.stdout)
    if not saved_pattern:
        raise ValueError("Couldn't find saved file information in output")

    zip_filename = os.path.join(ANIMATED_FOLDER, filename)
    shutil.make_archive(zip_filename, 'zip', animated_file_result_folder)

    # Clean up individual frame files
    shutil.rmtree(animated_file_result_folder)

    return filename + '.zip'


def check_request(render_request):
    """
    Validate the incoming request.

    :param render_request: The Flask request object
    """
    if render_request.method != 'POST':
        abort(405)  # Method Not Allowed

    if 'file' not in render_request.files:
        return render_template('error.html', message="No file part"), 400


def check_file(file):
    """
    Validate the uploaded file.

    :param file: The uploaded file object
    """
    if file.filename == '':
        return render_template('error.html', message="No selected file"), 400

    if not allowed_file(file.filename):
        return render_template('error.html', message="File type not allowed"), 400


def cleanup_folders(*folders):
    """
    Remove all files and subdirectories in the specified folders.

    :param folders: Variable number of folder paths to clean up
    """
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {str(e)}")


if __name__ == '__main__':
    app.run(debug=False)  # Set debug=False in production
