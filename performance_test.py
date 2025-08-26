"""
Performance Test Script for Optimized WhatsApp Parser
Tests the performance improvements on different file sizes
"""

import time
import os
import random
from datetime import datetime, timedelta
from parser import WhatsAppParser
from analyzer import ChatAnalyzer

def generate_large_test_file(filename, num_messages=50000):
    """Generate a large test file for performance testing"""
    users = ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Charlie Davis', 
             'Eva Martinez', 'David Kim', 'Sarah Johnson', 'Mike Chen', 'Lisa Wang']
    
    messages = [
        "Hey everyone! How's it going?",
        "Good morning! ☀️",
        "Anyone up for lunch today?",
        "Just finished work 😊",
        "Thanks for the help yesterday",
        "Looking forward to the weekend!",
        "Great meeting today 👍",
        "Can't wait for vacation",
        "Happy birthday! 🎉",
        "See you tomorrow",
        "Perfect weather today",
        "Traffic is crazy right now",
        "Just watched a great movie",
        "Time for coffee ☕",
        "Working from home today"
    ]
    
    start_date = datetime(2025, 8, 1)  # Match sample_chat.txt format
    
    print(f"🔧 Generating {num_messages:,} messages test file...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(num_messages):
            # Random timestamp
            days_offset = random.randint(0, 30)  # Keep within a month for consistency
            hours_offset = random.randint(8, 22)  # Reasonable hours
            minutes_offset = random.randint(0, 59)
            
            timestamp = start_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
            
            # Format to match exact sample_chat.txt format: "8/1/25, 9:00 AM"
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
            
            # Random user and message
            user = random.choice(users)
            message = random.choice(messages)
            
            # Add some variety
            if random.random() < 0.1:  # 10% media messages
                message = "<Media omitted>"
            elif random.random() < 0.05:  # 5% questions
                message += " What do you think?"
            
            f.write(f"{timestamp_str} - {user}: {message}\n")
    
    file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
    print(f"✅ Generated test file: {file_size:.1f} MB")
    
    return filename

def test_performance():
    """Test parser performance on different file sizes"""
    print("🚀 PERFORMANCE TESTING - OPTIMIZED PARSER")
    print("=" * 60)
    
    # Test sizes
    test_configs = [
        ('small', 1000, "Small chat (1K messages)"),
        ('medium', 10000, "Medium chat (10K messages)"),
        ('large', 50000, "Large chat (50K messages)"),
    ]
    
    results = []
    
    for size_name, num_messages, description in test_configs:
        print(f"\n📊 Testing {description}")
        print("-" * 40)
        
        # Generate test file
        test_file = f"test_{size_name}_chat.txt"
        generate_large_test_file(test_file, num_messages)
        
        try:
            # Parse with new optimized parser
            parser = WhatsAppParser()
            
            print("🔄 Starting parsing...")
            start_time = time.time()
            
            df = parser.parse_chat(test_file)
            
            parse_time = time.time() - start_time
            
            if df is not None and not df.empty:
                print(f"✅ Parsing completed successfully!")
                print(f"📈 Messages parsed: {len(df):,}")
                print(f"⏱️  Total parse time: {parse_time:.2f}s")
                print(f"🚄 Parse rate: {len(df)/parse_time:.1f} messages/second")
                
                # Test analyzer performance
                print("\n🔍 Testing analyzer...")
                analyzer_start = time.time()
                
                analyzer = ChatAnalyzer(df)
                basic_stats = analyzer.get_basic_stats()
                user_stats = analyzer.get_user_stats()
                
                analyzer_time = time.time() - analyzer_start
                print(f"⏱️  Analysis time: {analyzer_time:.2f}s")
                print(f"📊 Analysis rate: {len(df)/analyzer_time:.1f} messages/second")
                
                # Get performance stats
                parser_stats = parser.get_performance_stats()
                analyzer_stats = analyzer.get_performance_stats()
                
                results.append({
                    'size': size_name,
                    'messages': len(df),
                    'parse_time': parse_time,
                    'analyze_time': analyzer_time,
                    'total_time': parse_time + analyzer_time,
                    'parse_rate': len(df)/parse_time,
                    'description': description
                })
                
                # Show breakdown
                print(f"📋 Performance breakdown:")
                for operation, time_taken in parser_stats['timing'].items():
                    print(f"   • {operation}: {time_taken:.2f}s")
                
            else:
                print("❌ Parsing failed!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Cleanup
        try:
            os.remove(test_file)
        except:
            pass
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if results:
        print(f"{'Size':<10} {'Messages':<10} {'Parse':<8} {'Analyze':<8} {'Total':<8} {'Rate':<10}")
        print("-" * 60)
        
        for result in results:
            print(f"{result['size']:<10} "
                  f"{result['messages']:,<10} "
                  f"{result['parse_time']:<8.1f} "
                  f"{result['analyze_time']:<8.1f} "
                  f"{result['total_time']:<8.1f} "
                  f"{result['parse_rate']:<10.0f}")
        
        # Estimate for 1.7MB file
        print(f"\n💡 ESTIMATE FOR YOUR 1.7MB FILE:")
        
        # Assume ~35K messages for 1.7MB (rough estimate)
        estimated_messages = 35000
        
        # Use large test performance for estimation
        large_result = next((r for r in results if r['size'] == 'large'), None)
        if large_result:
            scale_factor = estimated_messages / large_result['messages']
            estimated_time = large_result['total_time'] * scale_factor
            print(f"🔮 Estimated messages: ~{estimated_messages:,}")
            print(f"⏱️  Estimated total time: ~{estimated_time:.1f} seconds")
            print(f"🚄 Expected improvement: ~{1200/estimated_time:.0f}x faster!")
        
        print(f"\n🎉 OPTIMIZATION SUCCESS!")
        print(f"   • Pre-compiled regex patterns")
        print(f"   • Cached timestamp parsing") 
        print(f"   • Batch processing")
        print(f"   • Vectorized pandas operations")
        print(f"   • Parallel emoji extraction")
        print(f"   • Optimized feature extraction")

def benchmark_comparison():
    """Quick benchmark to show the improvements"""
    print("\n🏁 QUICK BENCHMARK")
    print("-" * 30)
    
    # Create a medium-sized test
    test_file = "benchmark_test.txt"
    generate_large_test_file(test_file, 5000)
    
    try:
        parser = WhatsAppParser()
        
        # Time the parsing
        start = time.time()
        df = parser.parse_chat(test_file)
        total_time = time.time() - start
        
        if df is not None and not df.empty:
            rate = len(df) / total_time
            print(f"✅ Processed {len(df):,} messages in {total_time:.2f}s")
            print(f"🚄 Rate: {rate:.0f} messages/second")
            
            # Expected time for 1.7MB file (rough estimate)
            estimated_messages_17mb = int(len(df) * (1.7 * 1024 * 1024) / os.path.getsize(test_file))
            estimated_time_17mb = estimated_messages_17mb / rate
            
            print(f"\n📈 For 1.7MB file (~{estimated_messages_17mb:,} messages):")
            print(f"⏱️  Expected time: ~{estimated_time_17mb:.1f} seconds")
            print(f"🎯 Improvement: From 20+ minutes to ~{estimated_time_17mb/60:.1f} minutes!")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
    
    finally:
        # Cleanup
        try:
            os.remove(test_file)
        except:
            pass

if __name__ == "__main__":
    test_performance()
    benchmark_comparison()
