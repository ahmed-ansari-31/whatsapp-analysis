"""
Minimal parser test to isolate the issue
"""

from parser import WhatsAppParser
import traceback

def minimal_test():
    print("🧪 MINIMAL PARSER TEST")
    print("=" * 40)
    
    try:
        parser = WhatsAppParser()
        
        # Test with sample_chat.txt
        print("📁 Testing with sample_chat.txt...")
        
        # Read file manually first
        with open('sample_chat.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 File content length: {len(content)} characters")
        print(f"📄 First line: {repr(content.split('\\n')[0])}")
        
        # Test format detection
        print("\\n🔍 Testing format detection...")
        detected_format = parser.detect_format_fast(content)
        print(f"Detected format: {detected_format}")
        
        if detected_format == 'unknown':
            print("❌ Format detection failed!")
            return False
        
        # Test message parsing
        print("\\n📝 Testing message parsing...")
        messages = parser.parse_messages_batch(content, detected_format)
        print(f"Messages found: {len(messages)}")
        
        if not messages:
            print("❌ No messages parsed!")
            
            # Debug: manually test first line
            print("\\n🔧 Manual debugging:")
            first_line = content.split('\\n')[0].strip()
            print(f"Testing line: {repr(first_line)}")
            
            pattern = parser.compiled_patterns[detected_format]
            match = pattern.match(first_line)
            
            if match:
                timestamp_str, sender, message = match.groups()
                print(f"✅ Regex matches!")
                print(f"  Timestamp: {repr(timestamp_str)}")
                print(f"  Sender: {repr(sender)}")
                print(f"  Message: {repr(message)}")
                
                # Test system message detection
                is_system = parser.is_system_message_fast(sender, message)
                print(f"  Is system message: {is_system}")
                
                if is_system:
                    print("❌ Message filtered out as system message!")
                else:
                    # Test timestamp parsing
                    try:
                        parsed_timestamp = parser.parse_timestamp_cached(timestamp_str, detected_format)
                        print(f"✅ Timestamp parsed: {parsed_timestamp}")
                    except Exception as e:
                        print(f"❌ Timestamp parsing failed: {e}")
                        
            else:
                print("❌ Regex doesn't match!")
            
            return False
        
        print(f"✅ Found {len(messages)} messages")
        
        # Show first few messages
        for i, msg in enumerate(messages[:3]):
            print(f"  Message {i+1}: {msg['sender']} - {msg['message'][:30]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = minimal_test()
    if success:
        print("\\n🎉 Parser test successful!")
    else:
        print("\\n💔 Parser test failed!")
