
import cv2
import numpy as np

def normalize(img_bytes: bytes) -> np.ndarray:
    """
    Normalize image for OCR.
    1. Decode
    2. Resize
    3. Auto-rotate (placeholder)
    4. Deskew (placeholder)
    5. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    """
    # Decode
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image bytes")

    # Denoise (FastNlMeans) - Gentle denoising
    try:
        img = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 7, 21)
    except Exception:
        pass

    # Add padding to help OCR with edge text
    img = cv2.copyMakeBorder(img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # Upscale if too small (e.g. thumbnails or low-res captures)
    # Helps OCR models resolve characters better
    h, w = img.shape[:2]
    min_side_target = 800
    if min(h, w) < min_side_target:
        scale = min_side_target / min(h, w)
        # Limit max scale to avoid excessive blurring/artifacts
        scale = min(scale, 4.0)
        # Only upscale if scale is significant
        if scale > 1.2:
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Resize (max side 2600)
    h, w = img.shape[:2]
    max_side = 2600
    if max(h, w) > max_side:
        scale = max_side / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # TODO: Auto-rotate logic (would require orientation detection model or heuristic)
    
    # TODO: Deskew logic
    
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # Enabled for NID cards to enhance text contrast against background
    try:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    except Exception as e:
        pass # Fallback to original if CLAHE fails
    
    # Sharpening (Unsharp Mask) to enhance edges for Bengali script
    gaussian = cv2.GaussianBlur(img, (0, 0), 3.0)
    img = cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)
    
    return img
