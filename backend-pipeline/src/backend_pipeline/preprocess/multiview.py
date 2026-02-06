
import numpy as np
from typing import List, Tuple

def generate_views(img: np.ndarray) -> List[Tuple[np.ndarray, int, int]]:
    """
    Generate multiple views of the image to improve OCR robustness.
    Returns list of tuples: (image_crop, offset_x, offset_y)
    """
    h, w = img.shape[:2]
    
    views = []
    
    # 1. Original
    views.append((img, 0, 0))
    
    # 2. Top Half (with some overlap)
    mid_h = h // 2
    overlap = 50 
    # crop: [0 : mid_h+overlap, 0:w]
    views.append((img[:mid_h + overlap, :], 0, 0))
    
    # 3. Bottom Half (with some overlap)
    # crop: [mid_h-overlap : h, 0:w]
    start_y = max(0, mid_h - overlap)
    views.append((img[start_y:, :], 0, start_y))
    
    # 4. Dense Crop (Center) - focus on content
    margin_h = h // 6
    margin_w = w // 6
    # crop: [margin_h : h-margin_h, margin_w : w-margin_w]
    views.append((img[margin_h:h-margin_h, margin_w:w-margin_w], margin_w, margin_h))
    
    return views
