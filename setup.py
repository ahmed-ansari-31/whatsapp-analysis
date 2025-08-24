"""
Enhanced Setup Script for WhatsApp Analyzer v2.0
Installs dependencies, downloads required data, and verifies installation
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print setup header"""
    print("\n" + "=" * 60)
    print("   WhatsApp Analyzer v2.0 - Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is 3.8+"""
    print("📌 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    print("This may take a few minutes...\n")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        print("\nTry running manually:")
        print("  pip install -r requirements.txt")
        return False

def download_nltk_data():
    """Download required NLTK data"""
    print("\n📥 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("✅ NLTK data downloaded successfully!")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not download NLTK data: {e}")
        print("The app will download it on first run.")
        return True

def create_sample_data():
    """Create sample WhatsApp export files for testing"""
    print("\n📝 Creating sample data files...")
    
    # Sample chat with reactions and media
    sample_chat = """8/1/25, 9:00 AM - John Doe: Good morning everyone! 🌞
8/1/25, 9:05 AM - Jane Smith: Morning John! How's everyone doing today?
8/1/25, 9:10 AM - Bob Wilson: Great! Just finished breakfast 😊
8/1/25, 9:15 AM - Alice Brown: Hey guys! Anyone up for coffee later? ☕
8/1/25, 9:20 AM - John Doe: Count me in! 
8/1/25, 9:25 AM - Jane Smith: <Media omitted>
8/1/25, 9:26 AM - Bob Wilson: Nice photo Jane! Where is that?
8/1/25, 9:27 AM - Jane Smith: Central Park this morning! Beautiful weather
8/1/25, 10:00 AM - Alice Brown: Wow, gorgeous! 😍
8/1/25, 10:30 AM - John Doe: So coffee at 3 PM? ☕
8/1/25, 10:31 AM - Bob Wilson: Works for me 👍
8/1/25, 10:32 AM - Jane Smith: Same here!
8/1/25, 10:33 AM - Alice Brown: Perfect! See you all at the usual place
8/1/25, 2:00 PM - John Doe: Running a bit late, be there by 3:15
8/1/25, 2:01 PM - Jane Smith: No worries! We'll wait
8/1/25, 3:00 PM - Bob Wilson: I'm here! Got us a table
8/1/25, 3:05 PM - Alice Brown: On my way! 5 minutes
8/1/25, 3:10 PM - Jane Smith: Just arrived! 
8/1/25, 3:15 PM - John Doe: Here! Sorry for the delay
8/1/25, 5:00 PM - Bob Wilson: That was fun! We should do this more often
8/1/25, 5:01 PM - Alice Brown: Absolutely! Same time next week?
8/1/25, 5:02 PM - Jane Smith: I'm in! 🎉
8/1/25, 5:03 PM - John Doe: Me too! Thanks for today everyone
8/2/25, 8:00 AM - Jane Smith: Good morning! Ready for another day? 💪
8/2/25, 8:15 AM - Bob Wilson: Morning! Already at work
8/2/25, 8:30 AM - John Doe: Morning all! Busy day ahead
8/2/25, 8:45 AM - Alice Brown: Same here! Let's crush it today! 💯
8/2/25, 12:00 PM - Jane Smith: Lunch break! What's everyone having?
8/2/25, 12:05 PM - Bob Wilson: Sandwich and salad 🥗
8/2/25, 12:10 PM - John Doe: Pizza day for me! 🍕
8/2/25, 12:15 PM - Alice Brown: Sushi! 🍱
8/2/25, 12:20 PM - Jane Smith: You all are making me hungry! 😂
8/2/25, 6:00 PM - Bob Wilson: Heading home! Have a great evening everyone
8/2/25, 6:05 PM - John Doe: You too Bob! See you tomorrow
8/2/25, 6:10 PM - Alice Brown: Bye everyone! 👋
8/2/25, 6:15 PM - Jane Smith: Have a good night all! 🌙"""
    
    # Save sample files
    files_created = []
    
    try:
        # Main sample file
        with open('sample_chat.txt', 'w', encoding='utf-8') as f:
            f.write(sample_chat)
        files_created.append('sample_chat.txt')
        
        # Create a larger sample for testing
        large_sample = sample_chat
        for i in range(5):  # Repeat to create more data
            large_sample += f"\n8/{i+3}/25, 10:00 AM - User{i}: Test message {i}\n"
            large_sample += sample_chat.replace("8/1/25", f"8/{i+3}/25").replace("8/2/25", f"8/{i+4}/25")
        
        with open('large_sample_chat.txt', 'w', encoding='utf-8') as f:
            f.write(large_sample)
        files_created.append('large_sample_chat.txt')
        
        print(f"✅ Created {len(files_created)} sample files:")
        for file in files_created:
            print(f"   - {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    dirs_to_create = ['reports', 'temp', 'exports']
    
    for dir_name in dirs_to_create:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}/")
        else:
            print(f"   Directory exists: {dir_name}/")
    
    return True

def test_installation():
    """Test if everything is installed correctly"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import pandas
        import numpy
        import plotly
        import streamlit
        import fastapi
        import emoji
        
        print("✅ Core packages imported successfully")
        
        # Test custom modules
        from parser import WhatsAppParser
        from analyzer import ChatAnalyzer
        from predictor import ChatPredictor
        
        print("✅ Custom modules loaded successfully")
        
        # Quick parsing test
        parser = WhatsAppParser()
        print("✅ Parser initialized successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def print_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("📌 Setup Complete! Here's how to use the analyzer:")
    print("=" * 60)
    
    print("\n🚀 Quick Start:")
    print("-" * 40)
    
    if platform.system() == "Windows":
        print("1. Double-click 'run.bat' for interactive menu")
        print("   OR")
    
    print("2. Run Streamlit Dashboard:")
    print("   streamlit run app.py")
    print()
    print("3. Run FastAPI Server:")
    print("   python -m uvicorn api:app --reload")
    print()
    print("4. Run both simultaneously:")
    print("   Terminal 1: streamlit run app.py")
    print("   Terminal 2: python -m uvicorn api:app --reload")
    
    print("\n📱 Export WhatsApp Chat:")
    print("-" * 40)
    print("Android: Menu (⋮) → More → Export chat")
    print("iOS: Contact name → Export Chat")
    print("Choose 'Without media' for faster processing")
    
    print("\n📊 Sample Files Created:")
    print("-" * 40)
    print("• sample_chat.txt - Small sample for testing")
    print("• large_sample_chat.txt - Larger dataset")
    
    print("\n🔗 Access Points:")
    print("-" * 40)
    print("• Streamlit: http://localhost:8501")
    print("• API: http://localhost:8000")
    print("• API Docs: http://localhost:8000/docs")
    
    print("\n💡 Tips:")
    print("-" * 40)
    print("• Use sample data to test features first")
    print("• Export chats without media for faster processing")
    print("• Check API docs for integration examples")
    print("• Reports are saved in the 'reports' folder")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.8+ required")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️ Some packages may not be installed")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(1)
    
    # Download NLTK data
    download_nltk_data()
    
    # Create sample data
    create_sample_data()
    
    # Test installation
    if test_installation():
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️ Some tests failed, but you can still try running the app")
    
    # Print instructions
    print_instructions()
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    
    input("\nPress Enter to exit...")
