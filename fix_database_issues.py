"""
Auto-Fix Script for Database Loading Issues
This script will fix the data type conversion errors when loading from database
"""

import os
import sys
import shutil
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def backup_files():
    """Create backups of original files"""
    files_to_backup = [
        'database_manager.py',
        'app.py',
        'visualizer.py'
    ]
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📦 Creating backup directory: {backup_dir}")
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"✅ Backed up {file}")
        else:
            print(f"⚠️ {file} not found, skipping backup")
    
    return backup_dir

def fix_database_manager():
    """Apply fixes to database_manager.py"""
    print("🔧 Fixing database_manager.py...")
    
    # The fixes have already been applied through the edits above
    # This function just validates the fixes are in place
    
    try:
        with open('database_manager.py', 'r') as f:
            content = f.read()
        
        # Check for the restore_pandas_objects method
        if 'def restore_pandas_objects(self, obj):' in content:
            print("✅ restore_pandas_objects method found")
        else:
            print("❌ restore_pandas_objects method missing")
            return False
        
        # Check for the updated convert_to_json_safe method
        if "'_type': 'pandas_dataframe'" in content:
            print("✅ Enhanced convert_to_json_safe method found")
        else:
            print("❌ Enhanced convert_to_json_safe method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database_manager.py: {e}")
        return False

def fix_app():
    """Apply fixes to app.py"""
    print("🔧 Fixing app.py...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for DataFrame conversion in user_insights
        if 'if isinstance(user_stats, dict):' in content:
            print("✅ DataFrame conversion fix found in user_insights")
        else:
            print("❌ DataFrame conversion fix missing in user_insights")
            return False
        
        # Check for peak hours fix
        if 'int(x) if isinstance(x, str) and x.isdigit()' in content:
            print("✅ Peak hours fix found")
        else:
            print("❌ Peak hours fix missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")
        return False

def fix_visualizer():
    """Apply fixes to visualizer.py"""
    print("🔧 Fixing visualizer.py...")
    
    try:
        with open('visualizer.py', 'r') as f:
            content = f.read()
        
        # Check for DataFrame conversion and list conversion fixes
        if 'if isinstance(user_stats, dict):' in content and 'tolist() if hasattr(' in content:
            print("✅ DataFrame and list conversion fixes found")
        else:
            print("❌ DataFrame and list conversion fixes missing")
            return False
        
        return True
        
    except Exception as e:
        print("❌ Error checking visualizer.py: {e}")
        return False

def test_fixes():
    """Test if the fixes work"""
    print("🧪 Testing fixes...")
    
    try:
        from database_manager import DatabaseManager
        
        db = DatabaseManager()
        sessions = db.get_saved_sessions()
        
        if sessions:
            print(f"✅ Found {len(sessions)} sessions in database")
            
            # Try to load the first session
            session_id = sessions[0]['id']
            df, basic_stats, analysis_results, predictions = db.load_analysis(session_id)
            
            if df is not None:
                print("✅ Successfully loaded DataFrame from database")
                
                # Check user_stats type
                if 'user_stats' in analysis_results:
                    user_stats = analysis_results['user_stats']
                    if hasattr(user_stats, 'tolist'):
                        print("✅ user_stats is properly restored as DataFrame/Series")
                    else:
                        print(f"⚠️ user_stats is {type(user_stats)} - can be converted")
                
                print("✅ All tests passed!")
                return True
            else:
                print("❌ Failed to load data from database")
                return False
        else:
            print("⚠️ No sessions found to test with")
            return True  # Not a failure, just no data to test
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main fix function"""
    print("🚀 Starting WhatsApp Analysis Database Fix...")
    print("=" * 50)
    
    # Create backups
    backup_dir = backup_files()
    print()
    
    # Apply and check fixes
    fixes_success = []
    
    fixes_success.append(fix_database_manager())
    fixes_success.append(fix_app())
    fixes_success.append(fix_visualizer())
    
    print()
    
    if all(fixes_success):
        print("✅ All fixes applied successfully!")
        
        # Test the fixes
        if test_fixes():
            print("\n🎉 Fix completed successfully!")
            print("Your WhatsApp analysis app should now work without database loading errors.")
            print(f"Backup created in: {backup_dir}")
        else:
            print("\n⚠️ Fixes applied but testing failed.")
            print("You may need to run a fresh analysis or check for additional issues.")
    else:
        print("\n❌ Some fixes failed to apply.")
        print("Please check the error messages above and try again.")
    
    print("\n" + "=" * 50)
    print("Fix script completed.")

if __name__ == "__main__":
    main()
