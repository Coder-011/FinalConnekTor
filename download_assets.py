import os
import urllib.request
from PIL import Image

def main():
    assets_dir = 'assets'
    fonts_dir = os.path.join(assets_dir, 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Download Fonts
    fonts = {
        'Poppins-Bold.ttf': 'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf',
        'Poppins-Regular.ttf': 'https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf',
        'MaterialIcons.ttf': 'https://github.com/google/material-design-icons/raw/master/font/MaterialIcons-Regular.ttf'
    }
    
    for filename, url in fonts.items():
        filepath = os.path.join(fonts_dir, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
    
    # Create icon.png
    icon_path = os.path.join(assets_dir, 'icon.png')
    if not os.path.exists(icon_path):
        print("Creating icon.png...")
        img = Image.new('RGB', (512, 512), color=(13, 14, 26)) # #0D0E1A
        img.save(icon_path)
        
    print("Assets created successfully.")

if __name__ == '__main__':
    main()
