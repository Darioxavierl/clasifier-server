#!/usr/bin/env python3
"""
Test API endpoints with HTTP requests
Verifies the full API stack is working
"""
import requests
import time
import subprocess
import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Get the parent directory
PROJECT_DIR = str(Path(__file__).parent.parent)
    """Test API endpoints"""
    
    print("=" * 60)
    print("API ENDPOINT TEST")
    print("=" * 60)
    
    # Start server
    print("\n📡 Starting API server...")
    env = os.environ.copy()
    server_process = subprocess.Popen(
        [".venv\\Scripts\\python.exe", "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=PROJECT_DIR
    )
    
    time.sleep(5)  # Wait for server
    
    try:
        # Test connection
        print("\n🧪 Testing connection...")
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            print(f"   ✅ Server responding (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)}")
            return False
        
        # Create test image
        print("\n📸 Creating test image...")
        img_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        test_image = Image.fromarray(img_array, mode='RGB')
        test_image.save('test_image.jpg')
        
        # Test prediction
        print("\n🚀 Testing /predict endpoint...")
        with open('test_image.jpg', 'rb') as f:
            files = {'file': f}
            try:
                response = requests.post(
                    "http://localhost:8000/predict",
                    files=files,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Prediction successful (HTTP 200)")
                    print(f"      Class: {data.get('class_name')}")
                    print(f"      Confidence: {data.get('confidence'):.1%}")
                    print(f"      Code: {data.get('code')}")
                    return True
                else:
                    print(f"   ❌ Error: HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                return False
        
    finally:
        # Stop server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        
        # Clean up
        Path('test_image.jpg').unlink(missing_ok=True)

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n✅ API TEST PASSED\n")
    else:
        print("\n❌ API TEST FAILED\n")
    sys.exit(0 if success else 1)
