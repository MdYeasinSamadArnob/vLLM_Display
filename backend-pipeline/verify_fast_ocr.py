
import requests
import json
import os

# Configuration
API_URL = "http://localhost:8001/api/v1/ocr/direct"
TEST_IMAGE_PATH = "./test_image.jpg" # Need to ensure this exists or use a dummy

def create_dummy_image():
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (800, 500), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10,10), "Name: John Doe", fill=(0,0,0))
    d.text((10,50), "Date of Birth: 01 Jan 1990", fill=(0,0,0))
    d.text((10,90), "NID No: 1234567890", fill=(0,0,0))
    img.save("test_image.jpg")
    print("Created dummy test image: test_image.jpg")

def test_fast_ocr():
    if not os.path.exists("test_image.jpg"):
        create_dummy_image()
        
    print(f"Testing Fast OCR API at {API_URL}...")
    
    files = {
        'file': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')
    }
    data = {
        'type': 'nid_front'
    }
    
    try:
        response = requests.post(API_URL, files=files, data=data)
        
        if response.status_code == 200:
            print("✅ Success! API responded with 200 OK")
            result = response.json()
            print(json.dumps(result, indent=2))
            
            # Basic validation
            if result.get("status") == "success" and "data" in result:
                print("✅ Response structure valid")
            else:
                print("❌ Invalid response structure")
        else:
            print(f"❌ API Failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_fast_ocr()
