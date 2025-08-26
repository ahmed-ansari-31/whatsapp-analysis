"""
Quick Test Script to Verify the Fixes
Tests if the optimized parser and analyzer work without errors
"""

try:
    print("🧪 Testing imports...")
    from parser import WhatsAppParser
    from analyzer import ChatAnalyzer
    print("✅ Imports successful!")
    
    print("\n🔧 Testing parser initialization...")
    parser = WhatsAppParser()
    print("✅ Parser initialized!")
    
    print("\n📊 Testing with sample data...")
    df = parser.parse_chat('sample_chat.txt')
    
    if df is not None and not df.empty:
        print(f"✅ Parser test successful! {len(df)} messages parsed")
        
        print("\n🔍 Testing analyzer...")
        analyzer = ChatAnalyzer(df)
        basic_stats = analyzer.get_basic_stats()
        
        print(f"✅ Analyzer test successful! {basic_stats['total_messages']} messages analyzed")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Your optimized system is ready to use!")
        
    else:
        print("❌ Parser returned empty data")
        
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()
