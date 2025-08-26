"""
Quick test to verify the parser fixes
"""

from parser import WhatsAppParser

def quick_test():
    print("🧪 Testing parser fixes...")
    
    try:
        parser = WhatsAppParser()
        df = parser.parse_chat('sample_chat.txt')
        
        if df is not None and not df.empty:
            print(f"✅ SUCCESS! Parsed {len(df)} messages")
            print(f"📊 Users: {df['sender'].unique()}")
            print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
            return True
        else:
            print("❌ Failed - no messages found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("🎉 Parser is working! You can now run performance_test.py")
    else:
        print("💔 Parser still has issues")
