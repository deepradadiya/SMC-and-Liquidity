#!/usr/bin/env python3
"""
Test the reorganized backend system
"""

import sys
import os
import subprocess
import time

def test_import_structure():
    """Test if all modules can be imported correctly"""
    print("🔍 Testing import structure...")
    
    try:
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Test core imports
        from app.core.config import settings
        from app.core.logger import get_logger
        from app.core.database import db_manager
        print("✅ Core modules imported successfully")
        
        # Test module imports
        from app.module1_mtf_confluence.mtf_confluence import ConfluenceEngine
        from app.module2_risk_manager.risk_manager import RiskManager
        from app.module3_smc_engine.smc_engine import PreciseSMCEngine
        print("✅ Module engines imported successfully")
        
        # Test route imports
        from app.module1_mtf_confluence.routes import router as mtf_router
        from app.module2_risk_manager.routes import router as risk_router
        from app.module3_smc_engine.routes import router as smc_router
        print("✅ Module routes imported successfully")
        
        print("🎉 All imports working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_server_start():
    """Test if the server can start"""
    print("\n🚀 Testing server startup...")
    
    try:
        # Try to start the server for a few seconds
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully!")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Server start error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Reorganized Backend System")
    print("=" * 50)
    
    # Test imports
    import_success = test_import_structure()
    
    # Test server startup
    server_success = test_server_start()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Server:  {'✅ PASS' if server_success else '❌ FAIL'}")
    
    if import_success and server_success:
        print("\n🎉 REORGANIZATION SUCCESSFUL!")
        print("   All modules are properly organized and working")
    else:
        print("\n⚠️  ISSUES FOUND - Check errors above")
    
    return import_success and server_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)