import os
import sys
import cv2
import numpy as np

# Add src to path to allow imports
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from backend_pipeline.preprocess.normalize import normalize
    from backend_pipeline.preprocess.multiview import generate_views
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def main():
    # Input image path
    input_path = r"g:\_era\vllm-ocr\backend\sample-images\nid-test.png"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        # Try to find any png in uploads if sample not found
        import glob
        files = glob.glob(r"g:\_era\vllm-ocr\backend\uploads\*.png")
        if files:
            input_path = files[0]
            print(f"Using alternative image: {input_path}")
        else:
            return

    print(f"Processing {input_path}...")
    
    with open(input_path, "rb") as f:
        img_bytes = f.read()

    # 1. Run Normalize (The 'Perfect' Preprocessing)
    print("Running normalization...")
    normalized_img = normalize(img_bytes)
    
    output_dir = "debug_preprocessing_output"
    os.makedirs(output_dir, exist_ok=True)
    
    norm_path = os.path.join(output_dir, "01_normalized_main.jpg")
    cv2.imwrite(norm_path, normalized_img)
    print(f"Saved Normalized Image: {norm_path} ({normalized_img.shape[1]}x{normalized_img.shape[0]})")

    # 2. Run Multiview (What the OCR actually sees)
    print("Generating views...")
    views = generate_views(normalized_img)
    
    for i, (view_img, off_x, off_y) in enumerate(views):
        view_path = os.path.join(output_dir, f"02_view_{i}.jpg")
        cv2.imwrite(view_path, view_img)
        print(f"Saved View {i}: {view_path} ({view_img.shape[1]}x{view_img.shape[0]}) at offset ({off_x}, {off_y})")

    print("\nDone! Check the 'debug_preprocessing_output' folder.")

if __name__ == "__main__":
    main()
