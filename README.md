# 🎬 MP4 Video Converter

A modern, user-friendly web application for converting MP4 videos to various formats including GIF, AVI, WebM, and more. Built with Flask and MoviePy, featuring a beautiful drag-and-drop interface.

## ✨ Features

- **Multiple Format Support**: Convert to GIF, MP4, AVI, WebM
- **Drag & Drop Interface**: Modern, intuitive file upload
- **Real-time Progress**: Live conversion progress tracking
- **File Management**: Automatic cleanup of temporary files
- **Responsive Design**: Works on desktop and mobile devices
- **Background Processing**: Non-blocking video conversion
- **File Size Limit**: Configurable upload limits (default: 100MB)

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- FFmpeg (for video processing)

### Installation

1. **Clone or download this project**
   ```bash
   cd mp4_converter
   ```

2. **Install FFmpeg** (required for video processing)
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **Windows:**
   - Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Add to system PATH

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate (macOS/Linux)
   source venv/bin/activate
   
   # Activate (Windows)
   venv\Scripts\activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 Usage

1. **Upload a Video**: 
   - Drag and drop a video file onto the upload area, or
   - Click the upload area to browse and select a file

2. **Choose Output Format**:
   - GIF: Optimized animated GIFs
   - MP4: Standard video format
   - AVI: Legacy video format
   - WebM: Modern web video format

3. **Convert**: Click the "Convert Video" button

4. **Download**: Once conversion is complete, download your converted file

5. **Clean Up**: Use the cleanup button to remove temporary files

## 📁 Supported Input Formats

- MP4
- AVI
- MOV
- MKV
- WMV
- FLV
- WebM

## 🔧 Configuration

You can modify the following settings in `app.py`:

```python
# File upload settings
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Supported file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
```

## 🏗️ Project Structure

```
mp4_converter/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/
│   └── index.html     # Web interface
├── uploads/           # Temporary upload storage
└── outputs/           # Converted file storage
```

## 🔒 Security Notes

- Files are automatically cleaned up after conversion
- Unique task IDs prevent file conflicts
- File type validation prevents malicious uploads
- Configurable file size limits

## 🛠️ Development

### Adding New Output Formats

To add support for additional output formats, modify the `convert_video` function in `app.py`:

```python
elif output_format == 'your_format':
    clip.write_videofile(
        output_path,
        codec='your_codec'
    )
```

### Customizing the UI

The interface styling is contained within `templates/index.html`. You can modify the CSS to match your preferred design.

## 📝 API Endpoints

- `GET /` - Main interface
- `POST /upload` - Upload and start conversion
- `GET /progress/<task_id>` - Get conversion progress
- `GET /download/<filename>` - Download converted file
- `GET /cleanup/<task_id>` - Clean up temporary files

## 🐛 Troubleshooting

**FFmpeg not found:**
- Ensure FFmpeg is installed and in your system PATH
- Try running `ffmpeg -version` in terminal

**Large file conversion fails:**
- Check available disk space
- Increase `MAX_FILE_SIZE` if needed
- Consider using cloud storage for large files

**Slow conversion:**
- GIF conversion can be slow for long videos
- Consider reducing video length or frame rate

## 📄 License

This project is open source. Feel free to use, modify, and distribute as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Enjoy converting your videos! 🎉**
