"""
Test script to verify database loading fixes
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def test_database_loading():
    """Test that database loading properly restores pandas objects"""
    print("Testing database manager fixes...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Get saved sessions
    sessions = db_manager.get_saved_sessions()
    
    if not sessions:
        print("❌ No saved sessions found. Please save an analysis first.")
        return False
    
    print(f"✅ Found {len(sessions)} saved sessions")
    
    # Load the first session
    session_id = sessions[0]['id']
    session_name = sessions[0]['session_name']
    
    print(f"🔄 Loading session: {session_name}")
    
    try:
        df, basic_stats, analysis_results, predictions = db_manager.load_analysis(session_id)
        
        if df is None:
            print("❌ Failed to load DataFrame")
            return False
        
        print(f"✅ DataFrame loaded with {len(df)} rows")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"DataFrame dtypes: {df.dtypes}")
        
        # Check user_stats type
        if 'user_stats' in analysis_results:
            user_stats = analysis_results['user_stats']
            print(f"✅ user_stats type: {type(user_stats)}")
            
            if isinstance(user_stats, pd.DataFrame):
                print(f"✅ user_stats is DataFrame with {len(user_stats)} rows")
                print(f"user_stats columns: {list(user_stats.columns)}")
            elif isinstance(user_stats, dict):
                print(f"⚠️ user_stats is still dict, but can be converted")
                # Test conversion
                user_stats_df = pd.DataFrame(user_stats)
                print(f"✅ Converted to DataFrame with {len(user_stats_df)} rows")
            else:
                print(f"❌ user_stats is unexpected type: {type(user_stats)}")
        
        # Check predictions
        if predictions and 'future_activity' in predictions:
            future_activity = predictions['future_activity']
            if 'peak_predicted_hours' in future_activity:
                peak_hours = future_activity['peak_predicted_hours']
                print(f"✅ peak_hours type: {type(peak_hours)}")
                if peak_hours:
                    print(f"Sample peak hour entry: {list(peak_hours.items())[0] if peak_hours else 'None'}")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during loading: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_loading()
    if success:
        print("\n🎉 Database fixes are working correctly!")
    else:
        print("\n💥 Some issues still remain. Check the errors above.")
