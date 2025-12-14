#!/usr/bin/env python3
"""
Quick verification script to check everything is working
"""
import sys
from pathlib import Path

def check_structure():
    """Verify project structure"""
    print(" Checking project structure...")
    
    required_dirs = [
        "app",
        "models",
        "training",
        "tests",
        "logs"
    ]
    
    required_files = [
        "run.py",
        ".env",
        "requirements.txt",
        "README.md"
    ]
    
    missing = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(f"   Directory: {dir_name}/")
    
    for file_name in required_files:
        if not Path(file_name).exists():
            missing.append(f"   File: {file_name}")
    
    if missing:
        print("\nMissing items:")
        for item in missing:
            print(item)
        return False
    
    print("   Structure OK")
    return True

def check_models():
    """Verify model files exist"""
    print("\n Checking model files...")
    
    models_dir = Path("models")
    pytorch_model = models_dir / "mobilenetv2_waste_pytorch_best.pth"
    tensorflow_model = models_dir / "mobilenetv2_waste.h5"
    
    pytorch_ok = pytorch_model.exists()
    tensorflow_ok = tensorflow_model.exists()
    
    print(f"  {'ok' if pytorch_ok else 'err'} PyTorch model: {pytorch_model.name}")
    print(f"  {'ok' if tensorflow_ok else 'err'} TensorFlow model: {tensorflow_model.name}")
    
    return pytorch_ok or tensorflow_ok

def check_env():
    """Verify .env configuration"""
    print("\n  Checking configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print(" .env file not found")
        return False
    
    content = env_file.read_text()
    
    checks = [
        ("MODEL_PATH", "MODEL_PATH" in content),
        ("LOG_LEVEL", "LOG_LEVEL" in content),
        ("CONFIDENCE_THRESHOLD", "CONFIDENCE_THRESHOLD" in content),
    ]
    
    all_ok = True
    for key, ok in checks:
        print(f"  {'ok' if ok else 'err'} {key}")
        if not ok:
            all_ok = False
    
    return all_ok

def check_dependencies():
    """Check Python dependencies"""
    print("\n Checking dependencies...")
    
    deps = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "PIL": "Pillow",
        "cv2": "OpenCV",
        "numpy": "NumPy",
    }
    
    all_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"  ok {name}")
        except ImportError:
            print(f"  err {name}")
            all_ok = False
    
    # Check for torch or tensorflow
    print("\n  Frameworks:")
    torch_ok = False
    try:
        import torch
        print(f"  ok PyTorch {torch.__version__}")
        torch_ok = True
    except ImportError:
        print(f" warn  PyTorch not installed")
    
    tf_ok = False
    try:
        import tensorflow as tf
        print(f"  ok TensorFlow {tf.__version__}")
        tf_ok = True
    except ImportError:
        print(f"  warn TensorFlow not installed")

    if not (torch_ok or tf_ok):
        print("\n  warn  At least one framework (PyTorch or TensorFlow) is required!")
        all_ok = False
    
    return all_ok

def check_gpu():
    """Check GPU availability"""
    print("\n Checking GPU...")
    
    # Check PyTorch GPU
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            device_count = torch.cuda.device_count()
            print(f"   PyTorch GPU: {device_name}")
            print(f"     CUDA Available: {torch.cuda.is_available()}")
            print(f"     Device Count: {device_count}")
        else:
            print(f"    PyTorch GPU: Not available (CPU mode)")
    except ImportError:
        pass
    
    # Check TensorFlow GPU
    try:
        import tensorflow as tf
        devices = tf.config.list_physical_devices('GPU')
        if devices:
            print(f"  ok TensorFlow GPU: {len(devices)} device(s)")
            for device in devices:
                print(f"     - {device}")
        else:
            print(f"    TensorFlow GPU: Not available (CPU mode)")
    except ImportError:
        pass

def main():
    """Run all checks"""
    print("=" * 60)
    print("WASTE CLASSIFICATION API - VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Project Structure", check_structure),
        ("Model Files", check_models),
        ("Configuration", check_env),
        ("Dependencies", check_dependencies),
        ("GPU", lambda: (check_gpu(), True)[1]),  # GPU check doesn't return bool
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            result = check_func()
            results[name] = result if result is not None else True
        except Exception as e:
            print(f"\n Error checking {name}: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results.items():
        if name != "GPU":
            icon = "ok" if result else "err"
            print(f"{icon} {name}")
    
    # Final status
    critical_ok = all(v for k, v in results.items() if k != "GPU")
    
    print("\n" + "=" * 60)
    if critical_ok:
        print(" All checks passed!")
        print("\nNext steps:")
        print("  1. Run tests:  python tests/test_comprehensive.py")
        print("  2. Start API:  python run.py")
        print("  3. Open:       http://localhost:8000/docs")
        return 0
    else:
        print(" Some checks failed. Please fix issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
