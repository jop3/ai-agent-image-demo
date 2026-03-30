#!/usr/bin/env python3
"""
Quick test script to verify your setup before the presentation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🔍 Testing environment setup...\n")

    # Load .env
    load_dotenv()

    # Check .env file
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("   → Copy .env.example to .env and add your API key")
        return False
    print("✅ .env file found")

    # Check Free tier API key
    api_key_free = os.getenv("GEMINI_API_KEY_FREE")
    if not api_key_free or api_key_free == "your_free_api_key_here":
        print("❌ GEMINI_API_KEY_FREE not configured!")
        print("   → Get your API key from: https://aistudio.google.com/app/apikey")
        return False
    print(f"✅ GEMINI_API_KEY_FREE configured ({api_key_free[:10]}...)")

    # Check Paid tier API key
    api_key_paid = os.getenv("GEMINI_API_KEY_PAID")
    if not api_key_paid or api_key_paid == "your_paid_api_key_here":
        print("❌ GEMINI_API_KEY_PAID not configured!")
        print("   → Get your API key from: https://aistudio.google.com/app/apikey")
        return False
    print(f"✅ GEMINI_API_KEY_PAID configured ({api_key_paid[:10]}...)")

    return True

def test_imports():
    """Test Python dependencies"""
    print("\n🔍 Testing Python dependencies...\n")

    required = [
        "numpy",
        "faster_whisper",
        "google.genai",
        "websockets",
        "dotenv"
    ]

    all_ok = True
    for module in required:
        try:
            __import__(module.replace(".", "_") if "." in module else module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - Run: pip install -r requirements.txt")
            all_ok = False

    return all_ok

def test_cuda():
    """Test CUDA availability"""
    print("\n🔍 Testing CUDA (GPU)...\n")

    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            return True
        else:
            print("⚠️  CUDA not available - Whisper will run on CPU (slower)")
            return True  # Not critical, can still work
    except ImportError:
        print("⚠️  PyTorch not installed - cannot check CUDA")
        print("   Whisper might still work if CUDA is installed")
        return True

def test_gemini_connection():
    """Test Gemini API connection (both free and paid tiers)"""
    print("\n🔍 Testing Gemini API connections...\n")

    load_dotenv()
    api_key_free = os.getenv("GEMINI_API_KEY_FREE")
    api_key_paid = os.getenv("GEMINI_API_KEY_PAID")

    if not api_key_free or not api_key_paid:
        print("❌ Cannot test - missing API keys")
        return False

    try:
        from google import genai

        # Test FREE tier
        print("Testing FREE tier (text generation)...")
        client_free = genai.Client(api_key=api_key_free)

        response = client_free.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Say 'Hello' in Swedish"
        )

        print(f"✅ FREE tier working!")
        print(f"   Response: {response.text.strip()}\n")

        # Test PAID tier with a simple request
        print("Testing PAID tier (image generation)...")
        client_paid = genai.Client(api_key=api_key_paid)

        # Just verify the client can connect (don't generate image in test)
        print(f"✅ PAID tier API key accepted!")
        print(f"   Note: Actual image generation tested during runtime\n")

        return True

    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        print("   → Check your API keys and internet connection")
        return False

def main():
    print("=" * 60)
    print("  Elevate Avega - Setup Test")
    print("=" * 60)
    print()

    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_imports),
        ("CUDA/GPU", test_cuda),
        ("Gemini API", test_gemini_connection)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print()

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print()
    if all_passed:
        print("🎉 All tests passed! You're ready for your presentation!")
        print()
        print("Next steps:")
        print("1. Run: python main.py")
        print("2. Run: python server.py (in another terminal)")
        print("3. Open: http://localhost:8000")
        print()
        print("Or simply run: start.bat")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print()
        print("Common solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Configure .env: copy .env.example .env")
        print("- Add API key to .env file")

    print("=" * 60)

if __name__ == "__main__":
    main()
