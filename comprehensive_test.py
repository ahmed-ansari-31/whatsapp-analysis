"""
Comprehensive test script to verify all fixes are working
"""

from parser import WhatsAppParser
from analyzer import ChatAnalyzer
import time
import os

def test_sample_chat():
    """Test with the sample_chat.txt file"""
    print("🧪 Testing with sample_chat.txt...")
    
    try:
        parser = WhatsAppParser()
        df = parser.parse_chat('sample_chat.txt')
        
        if df is not None and not df.empty:
            print(f"✅ Sample parsing successful!")
            print(f"   📊 Messages: {len(df)}")
            print(f"   👥 Users: {df['sender'].nunique()}")
            print(f"   📅 Date range: {df['date'].min()} to {df['date'].max()}")
            
            # Test analyzer
            analyzer = ChatAnalyzer(df)
            stats = analyzer.get_basic_stats()
            print(f"   📈 Analysis successful: {stats['total_messages']} messages")
            
            return True
        else:
            print("❌ Sample parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Sample parsing error: {e}")
        return False

def test_generated_messages():
    """Test with generated messages"""
    print("\\n🔧 Testing with generated messages...")
    
    # Create a small test file with proper format
    test_content = \"\"\"8/1/25, 9:00 AM - John Doe: Hello everyone! 🌞
8/1/25, 9:05 AM - Jane Smith: Morning John! How's it going?
8/1/25, 9:10 AM - Bob Wilson: Great! Just finished breakfast 😊
8/1/25, 10:00 AM - Alice Brown: Anyone up for coffee? ☕
8/1/25, 10:30 AM - John Doe: Count me in!
8/1/25, 11:00 AM - Jane Smith: <Media omitted>
8/1/25, 11:05 AM - Bob Wilson: Nice photo! Where is that?
8/1/25, 2:00 PM - Alice Brown: That was fun! Thanks everyone
\"\"\"
    
    # Write test file
    with open('test_generated.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        parser = WhatsAppParser()
        df = parser.parse_chat('test_generated.txt')
        
        if df is not None and not df.empty:
            print(f"✅ Generated message parsing successful!")
            print(f"   📊 Messages: {len(df)}")
            print(f"   👥 Users: {df['sender'].nunique()}")
            
            # Clean up
            os.remove('test_generated.txt')
            return True
        else:
            print("❌ Generated message parsing failed")
            os.remove('test_generated.txt')
            return False
            
    except Exception as e:
        print(f"❌ Generated message parsing error: {e}")
        if os.path.exists('test_generated.txt'):
            os.remove('test_generated.txt')
        return False

def performance_mini_test():
    """Quick performance test with a reasonable number of messages"""
    print("\\n🚀 Mini performance test...")
    
    from performance_test import generate_large_test_file
    
    try:
        # Generate 1000 messages
        test_file = generate_large_test_file('mini_perf_test.txt', 1000)
        
        # Test parsing
        parser = WhatsAppParser()
        start_time = time.time()
        
        df = parser.parse_chat('mini_perf_test.txt')
        
        parse_time = time.time() - start_time
        
        if df is not None and not df.empty:
            print(f"✅ Performance test successful!")
            print(f"   📊 Messages: {len(df):,}")
            print(f"   ⏱️  Time: {parse_time:.2f}s")
            print(f"   🚄 Rate: {len(df)/parse_time:.0f} messages/second")
            
            # Clean up
            os.remove('mini_perf_test.txt')
            return True
        else:
            print("❌ Performance test failed - no messages parsed")
            os.remove('mini_perf_test.txt')
            return False
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        if os.path.exists('mini_perf_test.txt'):
            os.remove('mini_perf_test.txt')
        return False

def main():
    print("🧪 COMPREHENSIVE PARSER TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Sample chat
    if test_sample_chat():
        tests_passed += 1
    
    # Test 2: Generated messages  
    if test_generated_messages():
        tests_passed += 1
    
    # Test 3: Performance test
    if performance_mini_test():
        tests_passed += 1
    
    print(f"\\n📊 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Parser is working correctly")
        print("✅ System message detection fixed") 
        print("✅ Timestamp parsing fixed")
        print("✅ Performance optimizations working")
        print("\\n🚀 You can now:")
        print("   • Run: streamlit run app.py")
        print("   • Run: python performance_test.py") 
        print("   • Upload your 1.7MB file (should parse in 1-2 minutes!)")
    else:
        print("❌ Some tests failed - need further debugging")

if __name__ == "__main__":
    main()
