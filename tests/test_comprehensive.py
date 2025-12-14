#!/usr/bin/env python3
"""
Comprehensive API test suite
Tests all endpoints and validates responses
"""
import json
import requests
import time
import subprocess
import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Get project directory
PROJECT_DIR = str(Path(__file__).parent.parent)

class APITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
    
    def start_server(self):
        """Start FastAPI server"""
        print("\n📡 Starting FastAPI server...")
        env = os.environ.copy()
        self.server_process = subprocess.Popen(
            [".venv\\Scripts\\python.exe", "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=PROJECT_DIR
        )
        time.sleep(5)
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            print("\n🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    def test_connection(self):
        """Test API is responding"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            print(f"✅ API responding (HTTP {response.status_code})")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def test_prediction(self):
        """Test prediction endpoint"""
        img_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        test_image = Image.fromarray(img_array, mode='RGB')
        test_image.save('test_img.jpg')
        
        try:
            with open('test_img.jpg', 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.base_url}/predict",
                    files=files,
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ /predict endpoint working")
                print(f"   Class: {data.get('class_name')}")
                print(f"   Confidence: {data.get('confidence'):.1%}")
                return True
            else:
                print(f"❌ /predict error: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ /predict error: {str(e)}")
            return False
        finally:
            Path('test_img.jpg').unlink(missing_ok=True)
    
    def test_health(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ /health endpoint working")
                print(f"   Status: {health.get('status')}")
                return True
            else:
                print(f"❌ /health error: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ /health error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE API TEST")
        print("=" * 60)
        
        self.start_server()
        results = []
        
        try:
            print("\n[1/3] Testing connection...")
            results.append(("Connection", self.test_connection()))
            
            print("\n[2/3] Testing /predict endpoint...")
            results.append(("Prediction", self.test_prediction()))
            
            print("\n[3/3] Testing /health endpoint...")
            results.append(("Health", self.test_health()))
            
            print("\n" + "=" * 60)
            passed = sum(1 for _, r in results if r)
            total = len(results)
            print(f"RESULTS: {passed}/{total} tests passed")
            print("=" * 60)
            
            for test_name, result in results:
                icon = "✅" if result else "❌"
                print(f"{icon} {test_name}")
            
            return passed == total
        
        finally:
            self.stop_server()

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
