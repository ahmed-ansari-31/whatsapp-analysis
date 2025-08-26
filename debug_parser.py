"""
Debug script to find why parser is not finding messages
"""

import re
from datetime import datetime

# Read sample chat
with open('sample_chat.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print("📁 Sample file content (first 300 chars):")
print(repr(content[:300]))
print()

# Test each line with regex patterns
lines = content.split('\n')
print(f"📊 Total lines: {len(lines)}")

# Define the patterns from the parser
patterns = {
    'ios_12h': re.compile(r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\]\s([^:]+):\s(.+)'),
    'ios_24h': re.compile(r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)'),
    'android_12h': re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)'),
    'android_24h': re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)'),
    'android_alt': re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)'),
    'european': re.compile(r'(\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)')
}

print("🔍 Testing first few lines with regex patterns:")
for i, line in enumerate(lines[:5]):
    if line.strip():
        print(f"\nLine {i+1}: {repr(line)}")
        
        for fmt, pattern in patterns.items():
            match = pattern.match(line)
            if match:
                print(f"  ✅ Matches {fmt}: {match.groups()}")
            else:
                print(f"  ❌ No match for {fmt}")

# Test system message detection
system_patterns = re.compile(r'(?:Messages and calls are end-to-end encrypted|'
                            r'changed the subject|changed the group description|'
                            r'added|left|removed|created group|created this group|'
                            r'joined using.*invite link|You joined using|'
                            r'Missed voice call|Missed video call|This message was deleted|'
                            r'security code|disappearing messages)', re.IGNORECASE)

print(f"\n🔍 Testing system message detection on first line:")
first_line = lines[0].strip() if lines else ""
if first_line:
    is_system = system_patterns.search(first_line) is not None
    print(f"Line: {repr(first_line)}")
    print(f"Is system message: {is_system}")

# Test timestamp parsing
print(f"\n🕐 Testing timestamp parsing:")
sample_timestamps = [
    "8/1/25, 9:00 AM",
    "8/1/25, 10:30 AM", 
    "8/2/25, 12:00 PM"
]

for ts_str in sample_timestamps:
    formats = [
        '%m/%d/%Y, %I:%M %p',
        '%d/%m/%Y, %I:%M %p', 
        '%m/%d/%y, %I:%M %p',
        '%d/%m/%y, %I:%M %p'
    ]
    
    print(f"Parsing: {ts_str}")
    for fmt in formats:
        try:
            result = datetime.strptime(ts_str, fmt)
            print(f"  ✅ Success with {fmt}: {result}")
            break
        except ValueError:
            print(f"  ❌ Failed with {fmt}")
