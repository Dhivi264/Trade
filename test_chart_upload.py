#!/usr/bin/env python3
"""
Test script to debug chart upload functionality
"""

import requests
import os
from PIL import Image
import numpy as np

def create_test_chart_image():
    """Create a simple test chart image"""
    # Create a simple chart-like image
    img = Image.new('RGB', (800, 600), color='white')
    pixels = img.load()
    
    # Draw a simple trend line
    for x in range(100, 700):
        y = 300 + int(50 * np.sin(x / 100))  # Simple sine wave
        if 0 <= y < 600:
            pixels[x, y] = (0, 0, 255)  # Blue line
    
    # Save test image
    img.save('test_chart.png')
    return 'test_chart.png'

def test_chart_upload():
    """Test the chart upload endpoint"""
    print("🧪 Testing Chart Upload Functionality")
    
    # Create test image
    test_image = create_test_chart_image()
    print(f"✅ Created test chart image: {test_image}")
    
    # Test data
    url = 'http://localhost:8000/api/upload-chart-analysis/'
    
    try:
        with open(test_image, 'rb') as f:
            files = {'chart_image': f}
            data = {
                'symbol': 'EURUSD',
                'timeframe': '1h'
            }
            
            print("📤 Sending request to upload endpoint...")
            response = requests.post(url, files=files, data=data)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS! Chart upload worked!")
                print(f"📈 Analysis Result: {result}")
            else:
                print(f"❌ ERROR! Status: {response.status_code}")
                print(f"🔍 Response Text: {response.text}")
                
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test image
        if os.path.exists(test_image):
            os.remove(test_image)
            print(f"🧹 Cleaned up test image: {test_image}")

if __name__ == "__main__":
    test_chart_upload()