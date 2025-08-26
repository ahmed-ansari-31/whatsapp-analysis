"""
Test script for the updated WhatsApp parser
Tests iOS and Android formats including Arabic text
"""

from parser import WhatsAppParser
from analyzer import ChatAnalyzer
import pandas as pd

def test_parser():
    parser = WhatsAppParser()
    
    print("="*60)
    print("TESTING WHATSAPP PARSER FIXES")
    print("="*60)
    
    # Test iOS format
    print("\n1. Testing iOS Format:")
    print("-" * 30)
    try:
        df_ios = parser.parse_chat('test_ios_chat.txt')
        print(f"✅ iOS format parsed successfully!")
        print(f"   Messages found: {len(df_ios)}")
        print(f"   Participants: {df_ios['sender'].nunique()}")
        print(f"   Date range: {df_ios['date'].min()} to {df_ios['date'].max()}")
        print(f"   Sample senders: {list(df_ios['sender'].unique())}")
        
        # Test response time calculation
        analyzer = ChatAnalyzer(df_ios)
        user_stats = analyzer.get_user_stats()
        print(f"   User stats generated: {len(user_stats)} users")
        
        # Check for negative response times
        for _, user in user_stats.iterrows():
            if pd.notna(user['avg_response_time_minutes']):
                if user['avg_response_time_minutes'] < 0:
                    print(f"   ❌ Negative response time found for {user['user']}: {user['avg_response_time_minutes']}")
                else:
                    print(f"   ✅ Positive response time for {user['user']}: {user['avg_response_time_minutes']:.2f} minutes")
        
    except Exception as e:
        print(f"❌ iOS format failed: {e}")
    
    # Test Android format with Arabic
    print("\n2. Testing Android Format with Arabic:")
    print("-" * 40)
    try:
        df_android = parser.parse_chat('test_android_arabic_chat.txt')
        print(f"✅ Android with Arabic parsed successfully!")
        print(f"   Messages found: {len(df_android)}")
        print(f"   Participants: {df_android['sender'].nunique()}")
        print(f"   Date range: {df_android['date'].min()} to {df_android['date'].max()}")
        print(f"   Sample senders: {list(df_android['sender'].unique())}")
        
        # Check Arabic text handling
        arabic_messages = df_android[df_android['message'].str.contains('Arabic|مرحبا|أهلاً|الحمد', na=False, regex=True)]
        print(f"   Arabic messages detected: {len(arabic_messages)}")
        
        # Test response time calculation
        analyzer = ChatAnalyzer(df_android)
        user_stats = analyzer.get_user_stats()
        print(f"   User stats generated: {len(user_stats)} users")
        
        # Check for negative response times
        negative_times = 0
        positive_times = 0
        for _, user in user_stats.iterrows():
            if pd.notna(user['avg_response_time_minutes']):
                if user['avg_response_time_minutes'] < 0:
                    negative_times += 1
                    print(f"   ❌ Negative response time for {user['user']}: {user['avg_response_time_minutes']}")
                else:
                    positive_times += 1
                    print(f"   ✅ Positive response time for {user['user']}: {user['avg_response_time_minutes']:.2f} minutes")
        
        print(f"   Response time summary: {positive_times} positive, {negative_times} negative")
        
    except Exception as e:
        print(f"❌ Android with Arabic failed: {e}")
    
    # Test sample data
    print("\n3. Testing Sample Data:")
    print("-" * 25)
    try:
        df_sample = parser.parse_chat('sample_chat.txt')
        print(f"✅ Sample data parsed successfully!")
        print(f"   Messages found: {len(df_sample)}")
        print(f"   Participants: {df_sample['sender'].nunique()}")
        
        # Test analyzer
        analyzer = ChatAnalyzer(df_sample)
        basic_stats = analyzer.get_basic_stats()
        print(f"   Basic stats: {basic_stats['total_messages']} messages, {basic_stats['total_participants']} users")
        
    except Exception as e:
        print(f"❌ Sample data failed: {e}")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_parser()
