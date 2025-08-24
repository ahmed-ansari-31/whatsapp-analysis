"""
Test script to verify all modules are working correctly
"""

import sys
import traceback
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    modules_to_test = [
        'pandas',
        'numpy', 
        'matplotlib',
        'plotly',
        'streamlit',
        'fastapi',
        'emoji',
        'nltk',
        'sklearn',
        'wordcloud',
        'vaderSentiment'
    ]
    
    failed = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - Not installed")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️ Missing modules: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required modules installed!")
    return True

def test_custom_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")
    
    try:
        from parser import WhatsAppParser
        print("✅ parser.py")
        
        from analyzer import ChatAnalyzer
        print("✅ analyzer.py")
        
        from predictor import ChatPredictor
        print("✅ predictor.py")
        
        from visualizer import ChatVisualizer
        print("✅ visualizer.py")
        
        from api import app
        print("✅ api.py")
        
        from report_generator import ReportGenerator
        print("✅ report_generator.py")
        
        print("\n✅ All custom modules loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading custom modules: {e}")
        traceback.print_exc()
        return False

def test_sample_parsing():
    """Test parsing sample data"""
    print("\nTesting sample data parsing...")
    
    try:
        from parser import WhatsAppParser
        
        # Create sample data
        sample_data = """8/1/25, 9:54 AM - John Doe: Hello everyone! 👋
8/1/25, 10:00 AM - Jane Smith: Hi John! How are you?
8/1/25, 10:05 AM - John Doe: Great! Just testing the analyzer 😊
8/1/25, 10:10 AM - Bob Wilson: <Media omitted>
8/1/25, 10:15 AM - Jane Smith: Nice photo Bob!
8/2/25, 2:30 PM - Alice Brown: Hey guys, what's up?
8/2/25, 2:35 PM - John Doe: Working on the WhatsApp analyzer project
8/2/25, 2:40 PM - Alice Brown: Sounds interesting! 🎉"""
        
        # Save to temp file
        with open('test_chat.txt', 'w', encoding='utf-8') as f:
            f.write(sample_data)
        
        # Parse
        parser = WhatsAppParser()
        df = parser.parse_chat('test_chat.txt')
        
        print(f"✅ Parsed {len(df)} messages")
        print(f"✅ Found {df['sender'].nunique()} participants")
        print(f"✅ Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Test analysis
        from analyzer import ChatAnalyzer
        analyzer = ChatAnalyzer(df)
        stats = analyzer.get_basic_stats()
        
        print(f"✅ Basic stats computed")
        print(f"   - Total words: {stats['total_words']}")
        print(f"   - Total emojis: {stats['total_emojis']}")
        
        # Test predictions
        from predictor import ChatPredictor
        predictor = ChatPredictor(df)
        
        print("✅ Predictor initialized")
        
        # Clean up
        import os
        os.remove('test_chat.txt')
        
        print("\n✅ Sample data test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Sample data test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("WhatsApp Analyzer Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test custom modules
    if not test_custom_modules():
        all_passed = False
    
    # Test sample parsing
    if not test_sample_parsing():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYou can now run:")
        print("  - Streamlit: streamlit run app.py")
        print("  - FastAPI: python -m uvicorn api:app --reload")
        print("  - Or use: run.bat")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the application.")
    print("=" * 50)

if __name__ == "__main__":
    main()
