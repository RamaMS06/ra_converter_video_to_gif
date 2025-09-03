#!/usr/bin/env python3
"""
Simple runner script for the MP4 Video Converter application.
This script provides a convenient way to start the Flask application.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import moviepy
        print("✅ Python dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg found")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg not found")
    print("Please install FFmpeg:")
    print("  macOS: brew install ffmpeg")
    print("  Ubuntu: sudo apt install ffmpeg")
    print("  Windows: Download from https://ffmpeg.org/download.html")
    return False

def main():
    """Main function to run the application."""
    print("🎬 MP4 Video Converter")
    print("=" * 30)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if not check_ffmpeg():
        print("\n⚠️  Warning: FFmpeg not found. Video conversion may fail.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    print("\n🚀 Starting the application...")
    print("📍 Server will be available at: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
