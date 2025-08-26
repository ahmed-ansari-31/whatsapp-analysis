"""
Simple verification test to check parser works with sample data
"""

from parser import WhatsAppParser
from analyzer import ChatAnalyzer

def test_sample_chat():
    """Test parser with the known working sample_chat.txt"""
    print("🧪 Testing parser with sample_chat.txt...")
    
    try:
        parser = WhatsAppParser()
        df = parser.parse_chat('sample_chat.txt')
        
        if df is not None and not df.empty:
            print(f"✅ Sample parsing successful! {len(df)} messages")
            
            # Test a few key things
            print(f"📊 Participants: {df['sender'].nunique()}")
            print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"👥 Users: {list(df['sender'].unique())}")
            
            # Test analyzer
            analyzer = ChatAnalyzer(df)
            basic_stats = analyzer.get_basic_stats()
            print(f"📈 Analysis successful! {basic_stats['total_messages']} messages analyzed")
            
            return True
        else:
            print("❌ Sample parsing failed - empty result")
            return False
            
    except Exception as e:
        print(f"❌ Sample parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_generated_format():
    """Test the format generation"""
    print("\n🔧 Testing generated message format...")
    
    from datetime import datetime, timedelta
    import random
    
    # Generate a few test messages like the performance_test does
    users = ['John Doe', 'Jane Smith']
    messages = ['Hello everyone!', 'Good morning! ☀️']
    start_date = datetime(2025, 8, 1)
    
    for i in range(5):
        days_offset = random.randint(0, 30)
        hours_offset = random.randint(8, 22)
        minutes_offset = random.randint(0, 59)
        
        timestamp = start_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        
        # Format to match exact sample_chat.txt format
        month = timestamp.month
        day = timestamp.day
        year = timestamp.strftime('%y')
        hour = timestamp.hour
        minute = timestamp.minute
        
        # Convert to 12-hour format
        if hour == 0:
            hour_12 = 12
            ampm = 'AM'
        elif hour < 12:
            hour_12 = hour
            ampm = 'AM'
        elif hour == 12:
            hour_12 = 12
            ampm = 'PM'
        else:
            hour_12 = hour - 12
            ampm = 'PM'
        
        timestamp_str = f"{month}/{day}/{year}, {hour_12}:{minute:02d} {ampm}"
        user = random.choice(users)
        message = random.choice(messages)
        
        test_line = f"{timestamp_str} - {user}: {message}"
        print(f"Generated: {test_line}")
    
    print("✅ Format generation test complete")

if __name__ == "__main__":
    print("🚀 PARSER VERIFICATION TEST")
    print("=" * 50)
    
    # Test with known working sample
    sample_works = test_sample_chat()
    
    # Test format generation
    test_generated_format()
    
    if sample_works:
        print("\n✅ Parser works with sample data!")
        print("🔄 You can now run performance_test.py")
    else:
        print("\n❌ Parser has issues with sample data")
        print("🔧 Need to fix parser first")
