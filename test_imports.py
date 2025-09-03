#!/usr/bin/env python3
"""
Test script to verify all required imports work correctly.
"""

try:
    print("Testing imports...")
    
    import flask
    print(f"✅ Flask {flask.__version__}")
    
    import moviepy
    print(f"✅ MoviePy {moviepy.__version__}")
    
    from moviepy.editor import VideoFileClip
    print("✅ MoviePy VideoFileClip import successful")
    
    import numpy
    print(f"✅ NumPy {numpy.__version__}")
    
    import PIL
    print(f"✅ Pillow {PIL.__version__}")
    
    import imageio
    print(f"✅ ImageIO {imageio.__version__}")
    
    import gunicorn
    print(f"✅ Gunicorn {gunicorn.__version__}")
    
    print("\n🎉 All imports successful! The application should work.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)
