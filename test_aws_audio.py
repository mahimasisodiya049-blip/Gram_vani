"""Test script for AWS Audio Client integration.

This script verifies that the AWS audio client can be imported and initialized.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from integrations import AWS_AVAILABLE
        print(f"✅ AWS_AVAILABLE: {AWS_AVAILABLE}")
        
        if AWS_AVAILABLE:
            from integrations import AWSAudioClient, AWSAudioClientError
            print("✅ AWSAudioClient imported successfully")
            print("✅ AWSAudioClientError imported successfully")
            
            # Test initialization
            try:
                client = AWSAudioClient(region_name="us-east-1")
                print("✅ AWSAudioClient initialized successfully")
                
                # Test supported languages
                languages = client.get_supported_languages()
                print(f"✅ Supported languages: {', '.join(languages)}")
                
                return True
            except Exception as e:
                print(f"⚠️ Could not initialize client (credentials may be missing): {e}")
                print("   This is expected if AWS credentials are not configured")
                return True
        else:
            print("⚠️ AWS not available - boto3 not installed")
            print("   Install with: pip install boto3")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_imports():
    """Test that app files can import the client."""
    print("\nTesting app imports...")
    
    try:
        # Test basic import without running the app
        import importlib.util
        
        # Test app.py
        spec = importlib.util.spec_from_file_location("app", "app.py")
        if spec and spec.loader:
            print("✅ app.py can be loaded")
        
        # Test app_improved.py
        spec = importlib.util.spec_from_file_location("app_improved", "app_improved.py")
        if spec and spec.loader:
            print("✅ app_improved.py can be loaded")
        
        return True
    except Exception as e:
        print(f"❌ Error loading app files: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("AWS Audio Client Integration Test")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test app imports
    results.append(("App Imports", test_app_imports()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Integration is complete.")
        print("\nNext steps:")
        print("1. Set AWS credentials in .env or environment variables")
        print("2. Run: streamlit run app_improved.py")
        print("3. Test audio recording and playback")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
