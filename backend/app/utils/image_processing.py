from PIL import Image, ImageEnhance, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def preprocess_image(image_path: str) -> str:
    """
    Preprocesses the image for better OCR results.
    - Increases contrast
    - Sharpening
    - Auto-orient
    
    Returns the path to the processed image.
    """
    try:
        with Image.open(image_path) as img:
            # Fix orientation (EXIF)
            img = ImageOps.exif_transpose(img)
            
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Upscale if image is too small (critical for NID/small docs)
            # Target at least 1000px on the longest side for better OCR
            width, height = img.size
            max_dim = max(width, height)
            if max_dim < 1000:
                scale_factor = 1000 / max_dim
                new_size = (int(width * scale_factor), int(height * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Upscaled image from {width}x{height} to {new_size[0]}x{new_size[1]}")

            # Enhancement factors
            # 1. Increase Contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5) # Increase contrast by 50%
            
            # 2. Sharpen
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0) # Sharpen significantly
            
            # Save processed image
            directory, filename = os.path.split(image_path)
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_processed{ext}"
            new_path = os.path.join(directory, new_filename)
            
            img.save(new_path, quality=95)
            logger.info(f"Processed image saved to {new_path}")
            return new_path
            
    except Exception as e:
        logger.error(f"Failed to preprocess image: {e}")
        return image_path # Return original if failure
