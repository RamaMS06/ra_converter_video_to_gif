"""
Compatibility fix for MoviePy with newer Pillow versions.
This patches the PIL.Image.ANTIALIAS issue.
"""

try:
    from PIL import Image
    # Fix for Pillow 10.0.0+ compatibility with MoviePy
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
        print("Applied Pillow compatibility fix: ANTIALIAS -> LANCZOS")
except ImportError:
    pass
