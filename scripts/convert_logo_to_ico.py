#!/usr/bin/env python3
import sys
import os
from PIL import Image

def convert_to_ico(input_path, output_path):
    """
    Convert an image to .ico format with multiple sizes.
    """
    try:
        img = Image.open(input_path)
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # Icon sizes
        icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        
        # Save as ICO
        img.save(output_path, format='ICO', sizes=icon_sizes)
        print(f"Successfully converted '{input_path}' to '{output_path}'")
        return True
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_logo_to_ico.py <input_image_path> [output_ico_path]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Default output in assets folder if not specified
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'app_icon.ico')
        
    convert_to_ico(input_file, output_file)
