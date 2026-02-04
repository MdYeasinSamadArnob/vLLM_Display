from PIL import Image
import os

image_path = os.path.join(os.path.dirname(__file__), "sample-images", "nid-test.png")
try:
    img = Image.open(image_path)
    print(f"Image loaded. Size: {img.size}, Mode: {img.mode}")
except Exception as e:
    print(f"Error loading image: {e}")
