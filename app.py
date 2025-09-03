import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file, flash
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Store conversion progress
conversion_progress = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_video(input_path, output_path, output_format, task_id):
    """Convert video file to specified format"""
    try:
        conversion_progress[task_id] = {'status': 'processing', 'progress': 0}
        
        # Load video clip
        clip = VideoFileClip(input_path)
        conversion_progress[task_id]['progress'] = 25
        
        if output_format == 'gif':
            # Convert to GIF preserving original timing and quality
            # Use original fps but cap at 24fps for reasonable file size
            original_fps = clip.fps
            gif_fps = min(original_fps, 24) if original_fps else 15
            
            # For very long videos, reduce fps to keep file size manageable
            duration = clip.duration
            if duration > 10:  # If video is longer than 10 seconds
                gif_fps = min(gif_fps, 15)
            elif duration > 30:  # If video is longer than 30 seconds
                gif_fps = min(gif_fps, 12)
            
            conversion_progress[task_id]['progress'] = 40
            
            clip.write_gif(
                output_path,
                fps=gif_fps,
                program='ffmpeg',
                opt='optimizeplus',
                fuzz=1,  # Lower fuzz for better quality
                verbose=False,
                logger=None
            )
        elif output_format == 'mp4':
            # Convert to MP4
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac'
            )
        elif output_format == 'avi':
            # Convert to AVI
            clip.write_videofile(
                output_path,
                codec='libxvid'
            )
        elif output_format == 'webm':
            # Convert to WebM
            clip.write_videofile(
                output_path,
                codec='libvpx'
            )
        
        conversion_progress[task_id] = {'status': 'completed', 'progress': 100}
        clip.close()
        
    except Exception as e:
        conversion_progress[task_id] = {'status': 'error', 'progress': 0, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    output_format = request.form.get('format', 'gif')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        task_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Save uploaded file
        input_filename = f"{task_id}_input.{file_extension}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)
        
        # Prepare output file
        output_filename = f"{task_id}_output.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Start conversion in background thread
        thread = threading.Thread(
            target=convert_video,
            args=(input_path, output_path, output_format, task_id)
        )
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'File uploaded successfully. Conversion started.',
            'output_filename': output_filename
        })

@app.route('/progress/<task_id>')
def get_progress(task_id):
    progress = conversion_progress.get(task_id, {'status': 'not_found', 'progress': 0})
    return jsonify(progress)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup/<task_id>')
def cleanup_files(task_id):
    """Clean up uploaded and converted files"""
    try:
        # Find and remove files associated with task_id
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            for filename in os.listdir(folder):
                if filename.startswith(task_id):
                    os.remove(os.path.join(folder, filename))
        
        # Remove from progress tracking
        if task_id in conversion_progress:
            del conversion_progress[task_id]
        
        return jsonify({'message': 'Files cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
