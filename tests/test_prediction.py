#!/usr/bin/env python3
"""
Test local predictions with the model
Verifies the classifier loads and makes predictions correctly
"""
import sys
import os
import numpy as np
from pathlib import Path
from PIL import Image
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_local_prediction():
    """Test classifier locally without API server"""
    
    print("=" * 60)
    print("LOCAL PREDICTION TEST")
    print("=" * 60)
    
    try:
        from app.models.mobilenet_classifier import MobileNetClassifier
        from app.config import settings
        
        # Initialize classifier
        logger.info(f"Loading classifier: {settings.MODEL_PATH}")
        classifier = MobileNetClassifier()
        classifier.load_model(settings.MODEL_PATH)
        
        print(f"\n✅ Classifier initialized")
        print(f"   Framework: {classifier.framework}")
        print(f"   Classes: {len(settings.CLASSES)}")
        print(f"   Classes: {settings.CLASSES}")
        
        # Create dummy image
        print(f"\n📸 Creating test image...")
        dummy_image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        
        # Make prediction
        print(f"\n🧠 Making prediction...")
        prediction = classifier.predict(dummy_image)
        
        print(f"✅ Prediction successful")
        print(f"\n   Results:")
        for key, value in prediction.items():
            if isinstance(value, list) and len(str(value)) > 60:
                print(f"      {key}: [probabilities - {len(value)} values]")
            else:
                print(f"      {key}: {value}")
        
        # Validate output
        required_keys = ["class_id", "class_name", "confidence", "all_probabilities"]
        missing_keys = [k for k in required_keys if k not in prediction]
        
        if missing_keys:
            print(f"\n❌ Missing keys: {missing_keys}")
            return False
        
        if not (0 <= prediction["class_id"] < len(settings.CLASSES)):
            print(f"\n❌ Invalid class_id: {prediction['class_id']}")
            return False
        
        if prediction["class_name"] not in settings.CLASSES:
            print(f"\n❌ Invalid class_name: {prediction['class_name']}")
            return False
        
        if not (0 <= prediction["confidence"] <= 1):
            print(f"\n❌ Invalid confidence: {prediction['confidence']}")
            return False
        
        if len(prediction["all_probabilities"]) != len(settings.CLASSES):
            print(f"\n❌ Invalid probability count")
            return False
        
        print(f"\n✅ VALIDATION SUCCESSFUL")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_local_prediction()
    sys.exit(0 if success else 1)
