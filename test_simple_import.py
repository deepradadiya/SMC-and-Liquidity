#!/usr/bin/env python3
"""
Simple import test for reorganized system
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing basic imports...")
    
    # Test main app import
    from main import app
    print("✅ Main app imported successfully")
    
    # Test core imports
    from app.core.config import settings
    print("✅ Core config imported")
    
    # Test module 1
    from app.module1_mtf_confluence.mtf_confluence import ConfluenceEngine
    print("✅ Module 1 MTF imported")
    
    print("\n🎉 Basic reorganization is working!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()