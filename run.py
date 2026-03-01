"""Simple script to run the Gram-Vani Streamlit application."""

import subprocess
import sys
import os


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import audio_recorder_streamlit
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def main():
    """Run the Streamlit application."""
    print("=" * 60)
    print("🎙️  Gram-Vani - Voice-First Government Document Assistant")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check for environment variables
    if not os.getenv("BHASHINI_API_KEY"):
        print("⚠️  Warning: BHASHINI_API_KEY not set")
        print("   Set it in .env file or environment variables")
    
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        print("⚠️  Warning: AWS credentials not set")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    
    print()
    print("Starting Streamlit application...")
    print("The app will open in your browser at http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    print()
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Gram-Vani...")
        print("Thank you for using Gram-Vani!")


if __name__ == "__main__":
    main()
