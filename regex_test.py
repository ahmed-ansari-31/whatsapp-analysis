"""
Quick regex test to debug the parser issue
"""
import re

# Test sample line
test_line = "8/1/25, 9:00 AM - John Doe: Good morning everyone! 🌞"

# Our android_12h pattern
pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)')

print("🧪 REGEX DEBUG TEST")
print("=" * 40)
print(f"Test line: {repr(test_line)}")
print(f"Pattern: {pattern.pattern}")

match = pattern.match(test_line)
if match:
    print("✅ REGEX MATCHES!")
    print(f"Groups: {match.groups()}")
    timestamp, sender, message = match.groups()
    print(f"  Timestamp: {repr(timestamp)}")
    print(f"  Sender: {repr(sender)}")
    print(f"  Message: {repr(message)}")
else:
    print("❌ REGEX DOES NOT MATCH")
    
    # Let's try to debug step by step
    print("\nDebugging each part:")
    
    # Test timestamp part
    timestamp_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])'
    timestamp_match = re.search(timestamp_pattern, test_line)
    print(f"Timestamp part: {'✅' if timestamp_match else '❌'} - {timestamp_match.group() if timestamp_match else 'No match'}")
    
    # Test full pattern parts
    parts = [
        (r'\d{1,2}/\d{1,2}/\d{2,4}', "Date part"),
        (r',\s', "Comma space"),
        (r'\d{1,2}:\d{2}', "Time digits"),
        (r'\s[APap][Mm]', "AM/PM part"),
        (r'\s-\s', "Dash part"),
        (r'[^:]+', "Sender part"),
        (r':\s', "Colon space"),
        (r'.+', "Message part")
    ]
    
    for part_pattern, name in parts:
        if re.search(part_pattern, test_line):
            print(f"  {name}: ✅")
        else:
            print(f"  {name}: ❌")

# Test with the actual sample_chat.txt
print(f"\n📄 Testing with sample_chat.txt:")

try:
    with open('sample_chat.txt', 'r', encoding='utf-8') as f:
        lines = f.read().strip().split('\n')
    
    matches = 0
    for i, line in enumerate(lines[:5]):
        match = pattern.match(line)
        if match:
            matches += 1
            print(f"  Line {i+1}: ✅ {match.groups()[0]} | {match.groups()[1]}")
        else:
            print(f"  Line {i+1}: ❌ {repr(line[:50])}")
    
    print(f"📊 Total matches: {matches}/{len(lines[:5])}")
    
except Exception as e:
    print(f"Error reading file: {e}")

# Test system message detection
print(f"\n🔍 System message test:")
system_pattern = re.compile(r'(?:Messages and calls are end-to-end encrypted|'
                           r'changed the subject|changed the group description|'
                           r'added|left|removed|created group|created this group|'
                           r'joined using.*invite link|You joined using|'
                           r'Missed voice call|Missed video call|This message was deleted|'
                           r'security code|disappearing messages)', re.IGNORECASE)

test_messages = [
    "Good morning everyone! 🌞",
    "Messages and calls are end-to-end encrypted",
    "John added Jane to the group"
]

for msg in test_messages:
    is_system = system_pattern.search(msg) is not None
    print(f"  '{msg}': {'System' if is_system else 'Normal'}")
