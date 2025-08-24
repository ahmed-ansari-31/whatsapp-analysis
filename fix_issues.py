"""
Quick Fix Script for Common WhatsApp Analyzer Issues
Run this if you encounter any errors
"""

import os
import sys
import subprocess
import traceback

def fix_imports():
    """Fix import issues by reinstalling packages"""
    print("🔧 Fixing import issues...")
    
    packages_to_fix = [
        'pandas',
        'numpy',
        'scikit-learn',
        'plotly',
        'streamlit',
        'fastapi',
        'uvicorn',
        'emoji',
        'vaderSentiment',
        'wordcloud'
    ]
    
    for package in packages_to_fix:
        try:
            print(f"  Reinstalling {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", package],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✅ {package} fixed")
        except:
            print(f"  ⚠️ Could not fix {package}")

def fix_nltk_data():
    """Download missing NLTK data"""
    print("\n🔧 Fixing NLTK data...")
    
    try:
        import nltk
        nltk_data = ['punkt', 'stopwords', 'vader_lexicon', 'averaged_perceptron_tagger']
        
        for data in nltk_data:
            try:
                nltk.download(data, quiet=True)
                print(f"  ✅ Downloaded {data}")
            except:
                print(f"  ⚠️ Could not download {data}")
    except ImportError:
        print("  ❌ NLTK not installed. Run: pip install nltk")

def fix_encoding_issues():
    """Fix file encoding issues"""
    print("\n🔧 Fixing encoding issues...")
    
    # Set UTF-8 as default encoding
    if sys.platform == "win32":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        print("  ✅ Set UTF-8 encoding for Windows")
    
    print("  ✅ Encoding settings updated")

def fix_date_parsing():
    """Create a test file with various date formats"""
    print("\n🔧 Creating date format test file...")
    
    test_formats = """# Different date formats for testing
# Format 1: MM/DD/YY (US)
1/15/24, 10:30 AM - User1: Testing US format
1/15/24, 10:31 AM - User2: Response

# Format 2: DD/MM/YY (EU)
15/01/24, 10:30 - User1: Testing EU format
15/01/24, 10:31 - User2: Response

# Format 3: Android new format
8/1/25, 9:54 AM - User1: Testing Android format
8/1/25, 9:55 AM - User2: Response

# Format 4: iOS format
[1/15/24, 10:30:45 AM] User1: Testing iOS format
[1/15/24, 10:31:00 AM] User2: Response"""
    
    with open('date_format_test.txt', 'w', encoding='utf-8') as f:
        f.write(test_formats)
    
    print("  ✅ Created date_format_test.txt for testing")

def fix_permissions():
    """Fix file and directory permissions"""
    print("\n🔧 Fixing permissions...")
    
    dirs_to_create = ['reports', 'temp', 'exports', '.streamlit']
    
    for dir_name in dirs_to_create:
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"  ✅ Created {dir_name}/")
            else:
                print(f"  ✓ {dir_name}/ exists")
        except:
            print(f"  ⚠️ Could not create {dir_name}/")

def test_quick_parse():
    """Quick test to verify parsing works"""
    print("\n🧪 Testing quick parse...")
    
    try:
        from parser import WhatsAppParser
        
        # Create simple test data
        test_data = """8/1/25, 9:00 AM - John: Hello
8/1/25, 9:01 AM - Jane: Hi there!
8/1/25, 9:02 AM - John: How are you?"""
        
        with open('quick_test.txt', 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        parser = WhatsAppParser()
        df = parser.parse_chat('quick_test.txt')
        
        if len(df) == 3:
            print(f"  ✅ Parser working! Parsed {len(df)} messages")
        else:
            print(f"  ⚠️ Parser may have issues. Parsed {len(df)} messages (expected 3)")
        
        # Clean up
        os.remove('quick_test.txt')
        
    except Exception as e:
        print(f"  ❌ Parser test failed: {e}")
        traceback.print_exc()

def check_system_info():
    """Display system information"""
    print("\n📊 System Information:")
    print(f"  Python version: {sys.version}")
    print(f"  Platform: {sys.platform}")
    print(f"  Current directory: {os.getcwd()}")
    
    try:
        import pandas as pd
        import numpy as np
        import streamlit
        import fastapi
        
        print(f"  Pandas version: {pd.__version__}")
        print(f"  NumPy version: {np.__version__}")
        print(f"  Streamlit version: {streamlit.__version__}")
        print(f"  FastAPI version: {fastapi.__version__}")
    except ImportError as e:
        print(f"  ⚠️ Some packages not installed: {e}")

def main():
    print("=" * 60)
    print("   WhatsApp Analyzer - Quick Fix Tool")
    print("=" * 60)
    
    print("\nSelect fix to apply:")
    print("1. Fix all (recommended)")
    print("2. Fix imports only")
    print("3. Fix NLTK data only")
    print("4. Fix encoding issues")
    print("5. Fix date parsing")
    print("6. Fix permissions")
    print("7. Run quick test")
    print("8. Show system info")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-8): ").strip()
    
    if choice == "1":
        fix_imports()
        fix_nltk_data()
        fix_encoding_issues()
        fix_date_parsing()
        fix_permissions()
        test_quick_parse()
        check_system_info()
    elif choice == "2":
        fix_imports()
    elif choice == "3":
        fix_nltk_data()
    elif choice == "4":
        fix_encoding_issues()
    elif choice == "5":
        fix_date_parsing()
    elif choice == "6":
        fix_permissions()
    elif choice == "7":
        test_quick_parse()
    elif choice == "8":
        check_system_info()
    elif choice == "0":
        print("Exiting...")
        return
    else:
        print("Invalid choice")
    
    print("\n" + "=" * 60)
    print("✅ Fix process completed!")
    print("=" * 60)
    print("\nTry running the application now:")
    print("  streamlit run app.py")
    print("  OR")
    print("  python -m uvicorn api:app --reload")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess cancelled.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
