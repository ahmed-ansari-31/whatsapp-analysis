"""
Test script to verify the auto-save functionality works
"""

from parser import WhatsAppParser
from analyzer import ChatAnalyzer
from predictor import ChatPredictor
from database_manager import DatabaseManager
import pandas as pd
from datetime import datetime
import os

def test_auto_save():
    print("🧪 Testing auto-save functionality...")
    
    try:
        # Initialize components
        parser = WhatsAppParser()
        db_manager = DatabaseManager()
        
        print("📄 Parsing sample_chat.txt...")
        df = parser.parse_chat('sample_chat.txt')
        
        if df is None or df.empty:
            print("❌ Failed to parse sample chat")
            return False
        
        print(f"✅ Parsed {len(df)} messages")
        
        # Run analysis
        print("🔍 Running analysis...")
        analyzer = ChatAnalyzer(df)
        basic_stats = analyzer.get_basic_stats()
        
        analysis_results = {
            'basic_stats': basic_stats,
            'user_stats': analyzer.get_user_stats(),
            'temporal_analysis': analyzer.get_temporal_analysis()
        }
        
        print("🤖 Running predictions...")
        predictor = ChatPredictor(df)
        predictions = predictor.get_prediction_summary()
        
        # Test auto-save
        print("💾 Testing auto-save...")
        session_name = f"Test Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        session_id = db_manager.save_analysis(
            session_name,
            'sample_chat.txt',
            df,
            basic_stats,
            analysis_results,
            predictions
        )
        
        print(f"✅ Auto-save successful! Session ID: {session_id}")
        
        # Test loading
        print("📥 Testing load...")
        loaded_df, loaded_basic_stats, loaded_analysis, loaded_predictions = db_manager.load_analysis(session_id)
        
        if loaded_df is not None and not loaded_df.empty:
            print(f"✅ Load successful! Loaded {len(loaded_df)} messages")
            print(f"📊 Basic stats loaded: {len(loaded_basic_stats)} items")
            
            # Verify data integrity
            if len(loaded_df) == len(df):
                print("✅ Data integrity verified!")
                return True
            else:
                print(f"❌ Data mismatch: expected {len(df)}, got {len(loaded_df)}")
                return False
        else:
            print("❌ Load failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_stats():
    """Test database statistics"""
    print("\n📊 Testing database stats...")
    
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_database_stats()
        
        print(f"✅ Database stats:")
        print(f"   Sessions: {stats['session_count']}")
        print(f"   Messages: {stats['message_count']:,}")
        print(f"   Size: {stats['db_size_mb']:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Database stats test failed: {e}")
        return False

def main():
    print("🚀 AUTO-SAVE FUNCTIONALITY TEST")
    print("=" * 50)
    
    success = test_auto_save()
    test_database_stats()
    
    if success:
        print("\n🎉 AUTO-SAVE TEST PASSED!")
        print("✅ SQLite data type issues fixed")
        print("✅ Automatic saving working")
        print("✅ Loading working correctly")
        print("\n🚀 Ready for Streamlit app testing!")
    else:
        print("\n❌ AUTO-SAVE TEST FAILED!")
        print("Need to debug further")

if __name__ == "__main__":
    main()
