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
            # Convert to GIF with aggressive size optimization to keep under 1MB
            duration = clip.duration
            original_fps = clip.fps
            
            # Aggressive size reduction strategy
            # Target: Keep final GIF under 1MB
            
            # Step 1: Resize video if too large
            width, height = clip.size
            if width > 480 or height > 480:
                # Resize to max 480px on longest side
                if width > height:
                    new_width = 480
                    new_height = int(height * (480 / width))
                else:
                    new_height = 480
                    new_width = int(width * (480 / height))
                clip = clip.resize((new_width, new_height))
            
            conversion_progress[task_id]['progress'] = 35
            
            # Step 2: Reduce FPS aggressively based on duration
            if duration <= 3:
                gif_fps = 15  # Short clips can have higher fps
            elif duration <= 10:
                gif_fps = 10  # Medium clips
            elif duration <= 20:
                gif_fps = 8   # Longer clips
            else:
                gif_fps = 6   # Very long clips
            
            # Step 3: Limit duration for very long videos
            if duration > 30:
                # Trim to first 30 seconds to keep size manageable
                clip = clip.subclip(0, 30)
                duration = 30
            
            conversion_progress[task_id]['progress'] = 50
            
            # Step 4: Use aggressive compression settings
            clip.write_gif(
                output_path,
                fps=gif_fps,
                program='ffmpeg',
                opt='optimizeplus',
                fuzz=3,  # Higher fuzz for smaller file size
                verbose=False,
                logger=None
            )
            
            conversion_progress[task_id]['progress'] = 85
            
            # Step 5: Check file size and apply additional optimization if needed
            import os
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            if file_size_mb > 1.0:  # If still over 1MB, apply more aggressive optimization
                print(f"GIF size {file_size_mb:.1f}MB, applying additional optimization...")
                
                # Further reduce resolution and fps
                if width > 320 or height > 320:
                    if width > height:
                        new_width = 320
                        new_height = int(height * (320 / width))
                    else:
                        new_height = 320
                        new_width = int(width * (320 / height))
                    clip = clip.resize((new_width, new_height))
                
                # Reduce fps even more
                gif_fps = max(gif_fps - 2, 4)  # Minimum 4fps
                
                # Re-convert with more aggressive settings
                clip.write_gif(
                    output_path,
                    fps=gif_fps,
                    program='ffmpeg',
                    opt='optimizeplus',
                    fuzz=5,  # Even higher fuzz
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
