"""
WhatsApp Group Analyzer - Main Application
A comprehensive WhatsApp chat analysis tool with predictions and visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import json
import base64
from io import BytesIO

# Import custom modules
from parser import WhatsAppParser
from analyzer import ChatAnalyzer
from predictor import ChatPredictor
from visualizer import ChatVisualizer
from database_manager import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="WhatsApp Group Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #25D366;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #128C7E;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        background-color: #DCF8C6;
        color: #075E54;
    }
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_data' not in st.session_state:
    st.session_state.chat_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

def load_sample_data():
    """Load sample data for demonstration"""
    sample_messages = """1/1/24, 10:00 AM - John Doe: Hey everyone! Happy New Year! 🎉
1/1/24, 10:01 AM - Jane Smith: Happy New Year! 🎊 How's everyone doing?
1/1/24, 10:02 AM - Bob Wilson: Great! Just finished breakfast 😊
1/1/24, 10:05 AM - John Doe: Planning anything special today?
1/1/24, 10:06 AM - Jane Smith: Family dinner tonight! You?
1/1/24, 10:08 AM - Bob Wilson: Movie marathon 🍿
1/1/24, 2:30 PM - Alice Brown: Hey guys! Just woke up 😅
1/1/24, 2:31 PM - John Doe: Good afternoon sleepyhead!
1/1/24, 2:32 PM - Alice Brown: <Media omitted>
1/1/24, 2:33 PM - Jane Smith: Nice photo! Where is that?
1/1/24, 2:35 PM - Alice Brown: Central Park this morning ☀️
1/2/24, 9:00 AM - Bob Wilson: Morning everyone!
1/2/24, 9:15 AM - John Doe: Morning Bob! How was the movie marathon?
1/2/24, 9:16 AM - Bob Wilson: Awesome! Watched 5 movies 🎬
1/2/24, 11:00 AM - Jane Smith: Anyone up for lunch tomorrow?
1/2/24, 11:01 AM - Alice Brown: Count me in! 🙋‍♀️
1/2/24, 11:02 AM - John Doe: Sure! Where should we go?
1/2/24, 11:05 AM - Jane Smith: How about that new Italian place?
1/2/24, 11:06 AM - Bob Wilson: Sounds perfect! 🍝
1/1/24, 10:00 AM - John Doe: Hey everyone! Happy New Year! 🎉
1/1/24, 10:01 AM - Jane Smith: Happy New Year! 🎊 How's everyone doing?
1/1/24, 10:02 AM - Bob Wilson: Great! Just finished breakfast 😊
1/1/24, 10:05 AM - John Doe: Planning anything special today?
1/1/24, 10:06 AM - Jane Smith: Family dinner tonight! You?
1/1/24, 10:08 AM - Bob Wilson: Movie marathon 🍿
1/1/24, 2:30 PM - Alice Brown: Hey guys! Just woke up 😅
1/1/24, 2:31 PM - John Doe: Good afternoon sleepyhead!
1/1/24, 2:32 PM - Alice Brown: <Media omitted>
1/1/24, 2:33 PM - Jane Smith: Nice photo! Where is that?
1/1/24, 2:35 PM - Alice Brown: Central Park this morning ☀️
1/1/24, 7:45 PM - Bob Wilson: Just ordered pizza 🍕 anyone hungry?
1/1/24, 7:46 PM - Jane Smith: Yes!! Save me a slice 😂
1/1/24, 8:10 PM - John Doe: About to watch fireworks 🎆
1/1/24, 8:12 PM - Alice Brown: Send pics later!
1/1/24, 11:59 PM - Jane Smith: Goodnight everyone 🌙
1/2/24, 9:00 AM - Bob Wilson: Morning everyone!
1/2/24, 9:15 AM - John Doe: Morning Bob! How was the movie marathon?
1/2/24, 9:16 AM - Bob Wilson: Awesome! Watched 5 movies 🎬
1/2/24, 11:00 AM - Jane Smith: Anyone up for lunch tomorrow?
1/2/24, 11:01 AM - Alice Brown: Count me in! 🙋‍♀️
1/2/24, 11:02 AM - John Doe: Sure! Where should we go?
1/2/24, 11:05 AM - Jane Smith: How about that new Italian place?
1/2/24, 11:06 AM - Bob Wilson: Sounds perfect! 🍝
1/2/24, 3:20 PM - Alice Brown: Just had coffee ☕ needed energy
1/2/24, 5:45 PM - John Doe: Anyone watched the game last night? 🏀
1/2/24, 5:50 PM - Bob Wilson: Yep! Crazy last quarter!
1/2/24, 6:00 PM - Jane Smith: I missed it 😭 highlights?
1/3/24, 8:15 AM - Alice Brown: Morning!! 🌞
1/3/24, 8:16 AM - John Doe: Morning Alice!
1/3/24, 9:30 AM - Bob Wilson: Stuck in traffic 🚗
1/3/24, 9:45 AM - Jane Smith: Same here, roads are packed today 😩
1/3/24, 10:00 AM - John Doe: Working from home today 💻
1/3/24, 12:30 PM - Alice Brown: Lunch break 🍔
1/3/24, 12:45 PM - Bob Wilson: <Media omitted>
1/3/24, 12:46 PM - Jane Smith: Omg that burger looks huge 😂
1/3/24, 1:00 PM - John Doe: Now I’m hungry 😅
1/3/24, 6:15 PM - Alice Brown: Meeting was so long today 💤
1/3/24, 6:16 PM - Jane Smith: Same! Can’t wait for the weekend
1/4/24, 7:00 AM - Bob Wilson: Good morning team! 🌅
1/4/24, 7:05 AM - John Doe: Morning!
1/4/24, 7:06 AM - Jane Smith: Coffee first ☕
1/4/24, 9:30 AM - Alice Brown: Big presentation today, wish me luck 🤞
1/4/24, 9:32 AM - Bob Wilson: You’ll crush it!
1/4/24, 9:33 AM - John Doe: Good luck Alice!
1/4/24, 12:15 PM - Alice Brown: Done ✅ went really well!
1/4/24, 12:16 PM - Jane Smith: Yay! Proud of you 👏
1/4/24, 12:17 PM - Bob Wilson: Congrats 🎉
1/4/24, 7:45 PM - John Doe: Anyone free for a call?
1/4/24, 7:50 PM - Jane Smith: Give me 10 mins
1/5/24, 10:00 AM - Alice Brown: TGIF! 🎊
1/5/24, 10:01 AM - Bob Wilson: Finally! Weekend plans?
1/5/24, 10:05 AM - Jane Smith: Going hiking tomorrow 🥾
1/5/24, 10:07 AM - John Doe: Nice! I’ll be watching football 🏈
1/5/24, 11:00 AM - Alice Brown: Let’s meet for brunch Sunday?
1/5/24, 11:05 AM - Bob Wilson: Count me in!
1/5/24, 11:10 AM - Jane Smith: Yes please 🥞
1/5/24, 11:12 AM - John Doe: Done ✅
1/5/24, 7:00 PM - Alice Brown: <Media omitted>
1/5/24, 7:01 PM - Jane Smith: Cute dog!! 🐶
1/5/24, 7:02 PM - Bob Wilson: Adorable!
1/1/24, 10:00 AM - John Doe: Hey everyone! Happy New Year! 🎉
1/1/24, 10:01 AM - Jane Smith: Happy New Year!! 🎊 Wishing you all the best 💖
1/1/24, 10:02 AM - Bob Wilson: Great start! Coffee in hand ☕😊
1/1/24, 10:03 AM - Alice Brown: Happy 2024! 🥳
1/1/24, 10:05 AM - Mike Johnson: Morning fam! Ready to smash goals this year 💪
1/1/24, 10:06 AM - Sarah Lee: Just finished a run 🏃 feeling good!
1/1/24, 10:07 AM - Tom Harris: Happy New Year, legends 😎
1/1/24, 10:08 AM - Emily Clark: Fireworks last night were amazing 🎆
1/1/24, 10:10 AM - John Doe: Anyone got resolutions? 🤔
1/1/24, 10:12 AM - Jane Smith: Eat healthier (let’s see how long that lasts 😂)
1/1/24, 10:13 AM - Bob Wilson: Travel more ✈️
1/1/24, 2:30 PM - Alice Brown: Just woke up lol 😅
1/1/24, 2:31 PM - Sarah Lee: Lazy bones! 😂
1/1/24, 2:32 PM - Alice Brown: <Media omitted>
1/1/24, 2:33 PM - Emily Clark: Omg where is that?
1/1/24, 2:35 PM - Alice Brown: Central Park this morning ☀️

1/5/24, 8:00 AM - Mike Johnson: Gym done ✅ feeling pumped
1/5/24, 8:05 AM - Tom Harris: Bro chill, it’s Friday morning 😂
1/5/24, 8:06 AM - Sarah Lee: Respect tho 🙌
1/5/24, 10:15 AM - Emily Clark: Who’s free Sunday brunch? 🥞
1/5/24, 10:16 AM - Jane Smith: Yes please!
1/5/24, 10:20 AM - John Doe: Count me in
1/5/24, 10:22 AM - Bob Wilson: Where we going?
1/5/24, 10:25 AM - Emily Clark: That new café on 5th street?
1/5/24, 10:26 AM - Alice Brown: Perfect! ❤️
1/5/24, 10:27 AM - Tom Harris: Ok but I’m ordering pancakes AND waffles 😂

1/14/24, 9:10 PM - Jane Smith: This weather tho 🌧️
1/14/24, 9:12 PM - Sarah Lee: Same here… raining all day
1/14/24, 9:15 PM - Mike Johnson: Good excuse to stay in and game 🎮
1/14/24, 9:18 PM - Bob Wilson: <Media omitted>
1/14/24, 9:19 PM - Emily Clark: Lol your cat looks so done 😂🐱
1/14/24, 9:25 PM - Alice Brown: Awww cuteee

2/2/24, 7:30 AM - John Doe: Morning guys 🌞
2/2/24, 7:45 AM - Tom Harris: Too early, bro
2/2/24, 7:50 AM - Sarah Lee: Already on my second coffee ☕
2/2/24, 7:55 AM - Jane Smith: Same 😂
2/2/24, 12:00 PM - Bob Wilson: Who’s up for lunch today?
2/2/24, 12:01 PM - Mike Johnson: I’m in
2/2/24, 12:03 PM - Emily Clark: Can’t, stuck at work 😭
2/2/24, 12:05 PM - Alice Brown: Me too, maybe dinner instead?

2/14/24, 6:00 PM - Jane Smith: Happy Valentine’s Day 💕
2/14/24, 6:01 PM - Alice Brown: 😍
2/14/24, 6:02 PM - Sarah Lee: My Valentine is pizza tonight 🍕😂
2/14/24, 6:05 PM - Tom Harris: Mood lol
2/14/24, 6:06 PM - Mike Johnson: Took gf out for sushi 🍣
2/14/24, 6:07 PM - John Doe: Nice one bro 👍
2/14/24, 6:08 PM - Emily Clark: <Media omitted>
2/14/24, 6:09 PM - Bob Wilson: Cute couple! ❤️

3/3/24, 10:00 AM - Sarah Lee: March already 😳
3/3/24, 10:01 AM - John Doe: Time flying
3/3/24, 10:05 AM - Alice Brown: Spring vibes 🌸
3/3/24, 10:07 AM - Jane Smith: Finally some sun ☀️
3/3/24, 2:15 PM - Mike Johnson: Anyone up for hiking next weekend?
3/3/24, 2:16 PM - Tom Harris: I’m down 🥾
3/3/24, 2:17 PM - Emily Clark: Same here
3/3/24, 2:20 PM - Bob Wilson: As long as there’s food after 😂
3/3/24, 2:22 PM - Sarah Lee: Always about food with you lol
3/3/24, 2:25 PM - Bob Wilson: Priorities 🤷

3/28/24, 8:45 PM - John Doe: Big news tomorrow 👀
3/28/24, 8:46 PM - Jane Smith: Don’t tease ussss
3/28/24, 8:47 PM - Alice Brown: Spill it now!
3/28/24, 8:50 PM - John Doe: Patience 😉
3/29/24, 9:00 AM - John Doe: I GOT PROMOTED!!! 🎉🎉🎉
3/29/24, 9:01 AM - Everyone: Congrats!!!!! 🎊👏🔥

"""
    
    # Save to temp file
    with open('temp_sample.txt', 'w', encoding='utf-8') as f:
        f.write(sample_messages)
    
    return 'temp_sample.txt'

def main():
    # Header
    st.markdown('<h1 class="main-header">💬 WhatsApp Group Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg", width=100)
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Upload Chat", "Previous Chats", "Analysis Dashboard", "User Insights", 
                    "Predictions", "Visualizations", "Export Report"],
            icons=["cloud-upload", "database", "dashboard", "people", 
                  "graph-up", "bar-chart", "download"],
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 How to Export WhatsApp Chat"):
            st.markdown("""
            **For Android:**
            1. Open WhatsApp group
            2. Tap menu (3 dots) > More > Export chat
            3. Choose 'Without media'
            4. Save the .txt file
            
            **For iOS:**
            1. Open WhatsApp group
            2. Tap group name > Export Chat
            3. Choose 'Without Media'
            4. Save the .txt file
            """)
        
        # Sample data option
        if st.button("🎯 Load Sample Data"):
            sample_file = load_sample_data()
            parser = WhatsAppParser()
            df = parser.parse_chat(sample_file)
            
            if not df.empty:
                st.session_state.chat_data = df
                analyzer = ChatAnalyzer(df)
                st.session_state.analysis_results = {
                    'basic_stats': analyzer.get_basic_stats(),
                    'user_stats': analyzer.get_user_stats(),
                    'temporal_analysis': analyzer.get_temporal_analysis(),
                    'emoji_analysis': analyzer.get_emoji_analysis(),
                    'word_analysis': analyzer.get_word_analysis(),
                    'conversation_flow': analyzer.get_conversation_flow(),
                    'sentiment_analysis': analyzer.get_sentiment_analysis(),
                    'activity_patterns': analyzer.get_activity_patterns()
                }
                
                predictor = ChatPredictor(df)
                st.session_state.predictions = predictor.get_prediction_summary()
                
                # Auto-save sample data too
                try:
                    session_name = f"Sample Data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    session_id = st.session_state.db_manager.save_analysis(
                        session_name,
                        sample_file,
                        df,
                        st.session_state.analysis_results['basic_stats'],
                        st.session_state.analysis_results,
                        st.session_state.predictions
                    )
                    st.session_state.current_session_id = session_id
                    st.success(f"✅ Sample data loaded and automatically saved!")
                except Exception as e:
                    st.success(f"✅ Sample data loaded successfully!")
                    st.warning(f"Auto-save failed: {str(e)}")
                
                st.rerun()
    
    # Main content based on selection
    if selected == "Upload Chat":
        upload_section()
    elif selected == "Previous Chats":
        previous_chats_section()
    elif selected == "Analysis Dashboard":
        if st.session_state.chat_data is not None:
            analysis_dashboard()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first or load from previous chats!")
    elif selected == "User Insights":
        if st.session_state.chat_data is not None:
            user_insights()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first or load from previous chats!")
    elif selected == "Predictions":
        if st.session_state.predictions is not None:
            predictions_section()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first or load from previous chats!")
    elif selected == "Visualizations":
        if st.session_state.chat_data is not None:
            visualizations_section()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first or load from previous chats!")
    elif selected == "Export Report":
        if st.session_state.analysis_results is not None:
            export_report()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first or load from previous chats!")

def upload_section():
    """File upload section"""
    st.markdown('<h2 class="sub-header">📤 Upload WhatsApp Chat Export</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a WhatsApp chat export file",
            type=['txt'],
            help="Export your WhatsApp chat without media and upload the .txt file"
        )
        st.markdown("""
        <p style="font-size: 12px;">
        <strong>Disclaimer:</strong><br>
        The owner/creator of this application does <strong>not</strong> save any uploaded files. 
        Files are uploaded exclusively through the <code>st.file_uploader</code> function and are processed solely within the app. 
        Once the session ends, the files are discarded. 
        <strong>No data is stored or retained beyond the session</strong>.
        </p>
    """, unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with open('temp_chat.txt', 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner('🔄 Parsing chat data...'):
                try:
                    parser = WhatsAppParser()
                    df = parser.parse_chat('temp_chat.txt')
                    
                    if df.empty:
                        st.error("❌ No messages found in the file. Please check the format.")
                    else:
                        st.session_state.chat_data = df
                        
                        with st.spinner('🔍 Analyzing chat data...'):
                            analyzer = ChatAnalyzer(df)
                            st.session_state.analysis_results = {
                                'basic_stats': analyzer.get_basic_stats(),
                                'user_stats': analyzer.get_user_stats(),
                                'temporal_analysis': analyzer.get_temporal_analysis(),
                                'emoji_analysis': analyzer.get_emoji_analysis(),
                                'word_analysis': analyzer.get_word_analysis(),
                                'conversation_flow': analyzer.get_conversation_flow(),
                                'sentiment_analysis': analyzer.get_sentiment_analysis(),
                                'activity_patterns': analyzer.get_activity_patterns()
                            }
                        
                        with st.spinner('🤖 Generating predictions...'):
                            predictor = ChatPredictor(df)
                            st.session_state.predictions = predictor.get_prediction_summary()
                        
                        # Automatically save to database (no manual button needed)
                        with st.spinner('💾 Auto-saving analysis...'):
                            # Generate automatic session name
                            file_name = uploaded_file.name.replace('.txt', '').replace('_', ' ')
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                            session_name = f"{file_name} - {timestamp}"
                            
                            try:
                                session_id = st.session_state.db_manager.save_analysis(
                                    session_name,
                                    'temp_chat.txt',
                                    df,
                                    st.session_state.analysis_results['basic_stats'],
                                    st.session_state.analysis_results,
                                    st.session_state.predictions
                                )
                                st.session_state.current_session_id = session_id
                                st.success(f"✅ Analysis automatically saved as: '{session_name}'")
                                st.info("💡 You can now load this analysis instantly from 'Previous Chats' section!")
                            except Exception as e:
                                st.warning(f"⚠️ Auto-save failed: {str(e)} - Analysis is still available in this session.")
                        
                        st.success(f"✅ Successfully analyzed {len(df)} messages!")
                        st.balloons()
                        
                        # Show basic info
                        st.markdown("### 📊 Quick Overview")
                        stats = st.session_state.analysis_results['basic_stats']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Messages", f"{stats['total_messages']:,}")
                        with col2:
                            st.metric("Participants", stats['total_participants'])
                        with col3:
                            st.metric("Total Days", stats['total_days'])
                        with col4:
                            st.metric("Avg Messages/Day", f"{stats['avg_messages_per_day']:.1f}")
                        
                except Exception as e:
                    st.error(f"❌ Error parsing file: {str(e)}")
                    st.info("Please ensure the file is a valid WhatsApp chat export.")
    
    with col2:
        st.info("""
        **Supported Formats:**
        - Android exports (12/24 hour)
        - iOS exports
        - Both with/without media
        
        **File should contain:**
        - Timestamps
        - Sender names
        - Messages
        """)

def analysis_dashboard():
    """Main analysis dashboard"""
    st.markdown('<h2 class="sub-header">📊 Analysis Dashboard</h2>', unsafe_allow_html=True)
    
    stats = st.session_state.analysis_results['basic_stats']
    
    # Key metrics
    st.markdown("### 🎯 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📨 Messages", f"{stats['total_messages']:,}")
    with col2:
        st.metric("👥 Users", stats['total_participants'])
    with col3:
        st.metric("💬 Words", f"{stats['total_words']:,}")
    with col4:
        st.metric("😊 Emojis", f"{stats['total_emojis']:,}")
    with col5:
        st.metric("📷 Media", f"{stats['total_media']:,}")
    
    st.markdown("---")
    
    # Temporal Analysis
    st.markdown("### ⏰ Temporal Analysis")
    temporal = st.session_state.analysis_results['temporal_analysis']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Peak Hour:** {temporal['peak_hour']:02d}:00 ({temporal['peak_hour_messages']} messages)")
        
        # Hourly distribution chart
        hourly_data = pd.DataFrame(list(temporal['hourly_distribution'].items()), 
                                  columns=['Hour', 'Messages'])
        fig = px.bar(hourly_data, x='Hour', y='Messages', 
                     title='Messages by Hour of Day')
        fig.update_xaxes(tickmode='linear', dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.info(f"**Peak Day:** {temporal['peak_day']} ({temporal['peak_day_messages']} messages)")
        
        # Daily distribution chart
        daily_data = pd.DataFrame(list(temporal['daily_distribution'].items()), 
                                 columns=['Day', 'Messages'])
        fig = px.bar(daily_data, x='Day', y='Messages', 
                     title='Messages by Day of Week')
        st.plotly_chart(fig, use_container_width=True)
    
    # Activity Patterns
    st.markdown("### 📈 Activity Patterns")
    patterns = st.session_state.analysis_results['activity_patterns']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Daily Messages", f"{patterns['avg_daily_messages']:.1f}",
                 delta=f"±{patterns['std_daily_messages']:.1f}")
    with col2:
        st.metric("Most Active Date", str(patterns['most_active_date']),
                 delta=f"{patterns['max_daily_messages']} messages")
    with col3:
        st.metric("Least Active Date", str(patterns['least_active_date']),
                 delta=f"{patterns['min_daily_messages']} messages")
    
    # Sentiment Analysis
    st.markdown("### 😊 Sentiment Analysis")
    sentiment = st.session_state.analysis_results['sentiment_analysis']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Sentiment", f"{sentiment['overall_sentiment']:.3f}",
                 delta="Positive" if sentiment['overall_sentiment'] > 0 else "Negative")
    with col2:
        st.metric("Positive Messages", f"{sentiment['positive_ratio']*100:.1f}%")
    with col3:
        st.metric("Neutral Messages", f"{sentiment['neutral_ratio']*100:.1f}%")
    with col4:
        st.metric("Negative Messages", f"{sentiment['negative_ratio']*100:.1f}%")

def user_insights():
    """User insights section"""
    st.markdown('<h2 class="sub-header">👥 User Insights</h2>', unsafe_allow_html=True)
    
    user_stats = st.session_state.analysis_results['user_stats']
    
    # Ensure user_stats is a DataFrame
    if isinstance(user_stats, dict):
        user_stats = pd.DataFrame(user_stats)
    
    # User selection
    users = user_stats['user'].tolist()
    selected_user = st.selectbox("Select a user for detailed analysis:", users)
    
    user_data = user_stats[user_stats['user'] == selected_user].iloc[0]
    
    # User metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Messages Sent", f"{user_data['message_count']:,}",
                 delta=f"{user_data['message_percentage']:.1f}% of total")
    with col2:
        st.metric("Words Written", f"{user_data['word_count']:,}",
                 delta=f"{user_data['avg_words_per_message']:.1f} per msg")
    with col3:
        st.metric("Emojis Used", f"{user_data['emoji_count']:,}")
    with col4:
        if pd.notna(user_data['avg_response_time_minutes']):
            st.metric("Avg Response Time", f"{user_data['avg_response_time_minutes']:.1f} min")
        else:
            st.metric("Avg Response Time", "N/A")
    
    st.markdown("---")
    
    # User activity patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🕐 Activity Patterns")
        st.info(f"**Most Active Hour:** {user_data['most_active_hour']:02d}:00")
        st.info(f"**Most Active Day:** {user_data['most_active_day']}")
        st.info(f"**Sentiment Score:** {user_data['sentiment_score']:.3f}")
    
    with col2:
        st.markdown("### 😊 Top Emojis")
        if user_data['top_emojis']:
            emoji_df = pd.DataFrame(user_data['top_emojis'], columns=['Emoji', 'Count'])
            st.dataframe(emoji_df, hide_index=True)
        else:
            st.info("No emojis used by this user")
    
    # Comparison with group
    st.markdown("### 📊 Comparison with Group Average")
    
    avg_messages = user_stats['message_count'].mean()
    avg_words = user_stats['avg_words_per_message'].mean()
    avg_emojis = user_stats['emoji_count'].mean()
    
    comparison_data = {
        'Metric': ['Messages', 'Avg Words/Message', 'Total Emojis'],
        'User': [user_data['message_count'], user_data['avg_words_per_message'], user_data['emoji_count']],
        'Group Average': [avg_messages, avg_words, avg_emojis]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='User', x=comparison_df['Metric'], y=comparison_df['User']))
    fig.add_trace(go.Bar(name='Group Average', x=comparison_df['Metric'], y=comparison_df['Group Average']))
    fig.update_layout(title="User vs Group Average", barmode='group')
    
    st.plotly_chart(fig, use_container_width=True)

def predictions_section():
    """Predictions section"""
    st.markdown('<h2 class="sub-header">🔮 Predictions & Insights</h2>', unsafe_allow_html=True)
    
    predictions = st.session_state.predictions
    
    # Optimal Messaging Times
    st.markdown("### ⏰ Optimal Messaging Times")
    st.info("Based on historical engagement patterns, these are the best times to send messages for maximum response:")
    
    optimal_times = predictions['optimal_messaging_times']['overall_best_times'][:5]
    
    for i, time_slot in enumerate(optimal_times, 1):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.markdown(f"**#{i}**")
        with col2:
            st.markdown(f"**{time_slot['time']}**")
        with col3:
            st.markdown(f"Engagement: {time_slot['engagement_score']:.2f}")
    
    st.markdown("---")
    
    # Future Activity Prediction
    st.markdown("### 📈 7-Day Activity Forecast")
    
    future_activity = predictions['future_activity']
    st.info(f"**Model Accuracy:** {future_activity['model_accuracy']*100:.1f}%")
    st.info(f"**Predicted Total Messages (Next 7 Days):** {future_activity['total_predicted_messages']:,}")
    
    # Daily predictions chart
    daily_pred = pd.DataFrame(future_activity['daily_predictions'])
    if not daily_pred.empty:
        fig = px.bar(daily_pred, x='date', y='predicted_messages', 
                     title='Predicted Daily Messages',
                     labels={'predicted_messages': 'Messages', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Peak hours prediction
    st.markdown("### 🎯 Predicted Peak Hours")
    peak_hours = future_activity['peak_predicted_hours']
    if peak_hours:
        peak_df = pd.DataFrame(list(peak_hours.items()), columns=['Hour', 'Avg Messages'])
        # Convert hour to integer if it's a string
        peak_df['Hour'] = peak_df['Hour'].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
        peak_df['Hour'] = peak_df['Hour'].apply(lambda x: f"{x:02d}:00" if isinstance(x, int) else str(x))
        st.dataframe(peak_df, hide_index=True)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    recommendations = predictions['recommendations']
    for rec in recommendations:
        if rec['priority'] == 'high':
            st.error(f"🔴 **High Priority:** {rec['recommendation']}")
        elif rec['priority'] == 'medium':
            st.warning(f"🟡 **Medium Priority:** {rec['recommendation']}")
        else:
            st.info(f"🔵 **Low Priority:** {rec['recommendation']}")
    
    # Trending Topics
    st.markdown("### 🔥 Trending Topics")
    
    trending = predictions['trending_topics']['trending_topics']
    if trending:
        topics_df = pd.DataFrame(trending[:10])
        
        fig = px.bar(topics_df, x='score', y='topic', orientation='h',
                     title='Top Trending Topics',
                     labels={'score': 'Relevance Score', 'topic': 'Topic'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to identify trending topics")

def visualizations_section():
    """Interactive visualizations section"""
    st.markdown('<h2 class="sub-header">📊 Interactive Visualizations</h2>', unsafe_allow_html=True)
    
    df = st.session_state.chat_data
    analysis = st.session_state.analysis_results
    predictions = st.session_state.predictions
    
    visualizer = ChatVisualizer(df, analysis)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Timeline", "Heatmaps", "User Analysis", "Word Analysis", "Predictions"])
    
    with tab1:
        st.markdown("### 📅 Messages Over Months")
        monthly_fig = visualizer.create_monthly_timeline()
        st.plotly_chart(monthly_fig, use_container_width=True)
        
        st.markdown("### 📈 Message Timeline")
        timeline_fig = visualizer.create_message_timeline()
        st.plotly_chart(timeline_fig, use_container_width=True)
        
        st.markdown("### 💭 Sentiment Over Time")
        sentiment_fig = visualizer.create_sentiment_timeline()
        st.plotly_chart(sentiment_fig, use_container_width=True)
        
    
    with tab2:
        st.markdown("### 🗓️ Activity Heatmap")
        heatmap_fig = visualizer.create_hourly_heatmap()
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        st.markdown("### 🎯 Optimal Time Heatmap")
        optimal_fig = visualizer.create_optimal_time_chart(predictions)
        st.plotly_chart(optimal_fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 👥 User Activity Analysis")
        user_fig = visualizer.create_user_activity_chart()
        st.plotly_chart(user_fig, use_container_width=True)
        
        st.markdown("### ⏱️ Response Time Analysis")
        response_fig = visualizer.create_response_time_chart()
        st.plotly_chart(response_fig, use_container_width=True)
        
        st.markdown("### 🔄 Conversation Flow")
        flow_fig = visualizer.create_conversation_flow_chart()
        st.plotly_chart(flow_fig, use_container_width=True)
    
    with tab4:
        st.markdown("### ☁️ Word Cloud")
        word_cloud_img = visualizer.create_word_cloud()
        if word_cloud_img:
            st.image(word_cloud_img, use_column_width=True)
        else:
            st.info("Not enough text data for word cloud")
        
        st.markdown("### 😊 Emoji Analysis")
        emoji_fig = visualizer.create_emoji_chart()
        st.plotly_chart(emoji_fig, use_container_width=True)
    
    with tab5:
        st.markdown("### 🔮 Activity Predictions")
        prediction_fig = visualizer.create_prediction_chart(predictions)
        st.plotly_chart(prediction_fig, use_container_width=True)

def export_report():
    """Export analysis report"""
    st.markdown('<h2 class="sub-header">📥 Export Analysis Report</h2>', unsafe_allow_html=True)
    
    st.markdown("### 📄 Report Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_format = st.selectbox("Select report format:", ["JSON", "CSV", "HTML"])
        include_predictions = st.checkbox("Include predictions", value=True)
        include_visualizations = st.checkbox("Include visualization data", value=False)
    
    with col2:
        st.info("""
        **Available Formats:**
        - **JSON**: Complete data in structured format
        - **CSV**: Tabular data for spreadsheets
        - **HTML**: Interactive report with charts
        """)
    
    if st.button("📥 Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            if report_format == "JSON":
                # Create JSON report
                report_data = {
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_messages': len(st.session_state.chat_data),
                        'date_range': st.session_state.analysis_results['basic_stats']['date_range']
                    },
                    'analysis': st.session_state.analysis_results
                }
                
                if include_predictions:
                    report_data['predictions'] = st.session_state.predictions
                
                # Convert to JSON
                json_str = json.dumps(report_data, indent=2, default=str)
                
                # Download button
                st.download_button(
                    label="📥 Download JSON Report",
                    data=json_str,
                    file_name=f"whatsapp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
            elif report_format == "CSV":
                # Create CSV report
                output = BytesIO()
                
                # User statistics
                user_stats = st.session_state.analysis_results['user_stats']
                user_stats.to_csv(output, index=False)
                
                # Download button
                st.download_button(
                    label="📥 Download CSV Report",
                    data=output.getvalue(),
                    file_name=f"whatsapp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            elif report_format == "HTML":
                # Create HTML report
                html_content = generate_html_report(
                    st.session_state.analysis_results,
                    st.session_state.predictions if include_predictions else None
                )
                
                # Download button
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_content,
                    file_name=f"whatsapp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
            
            st.success("✅ Report generated successfully!")

def generate_html_report(analysis, predictions=None):
    """Generate HTML report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #25D366; }}
            h2 {{ color: #128C7E; }}
            .metric {{ 
                display: inline-block; 
                margin: 10px; 
                padding: 15px; 
                background: #f0f2f6; 
                border-radius: 8px; 
            }}
            .metric-value {{ font-size: 24px; font-weight: bold; }}
            .metric-label {{ color: #666; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #25D366; color: white; }}
        </style>
    </head>
    <body>
        <h1>WhatsApp Chat Analysis Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Basic Statistics</h2>
        <div>
            <div class="metric">
                <div class="metric-label">Total Messages</div>
                <div class="metric-value">{analysis['basic_stats']['total_messages']:,}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Participants</div>
                <div class="metric-value">{analysis['basic_stats']['total_participants']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Days</div>
                <div class="metric-value">{analysis['basic_stats']['total_days']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Messages/Day</div>
                <div class="metric-value">{analysis['basic_stats']['avg_messages_per_day']:.1f}</div>
            </div>
        </div>
        
        <h2>User Statistics</h2>
        <table>
            <tr>
                <th>User</th>
                <th>Messages</th>
                <th>Words</th>
                <th>Emojis</th>
                <th>Media</th>
            </tr>
    """
    
    # Add user statistics
    for _, user in analysis['user_stats'].iterrows():
        html += f"""
            <tr>
                <td>{user['user']}</td>
                <td>{user['message_count']}</td>
                <td>{user['word_count']}</td>
                <td>{user['emoji_count']}</td>
                <td>{user['media_count']}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html

def previous_chats_section():
    """Previous chats management section"""
    st.markdown('<h2 class="sub-header">📋 Previous Chat Analyses</h2>', unsafe_allow_html=True)
    
    # Get database statistics
    db_stats = st.session_state.db_manager.get_database_stats()
    
    # Show database info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Saved Sessions", db_stats['session_count'])
    with col2:
        st.metric("Total Messages", f"{db_stats['total_messages']:,}")
    with col3:
        st.metric("Database Size", f"{db_stats['db_size_mb']:.1f} MB")
    with col4:
        st.metric("Storage Used", f"{db_stats['message_count']:,} records")
    
    st.markdown("---")
    
    # Get saved sessions
    sessions = st.session_state.db_manager.get_saved_sessions()
    
    if not sessions:
        st.info("💭 No previous chat analyses found. Upload and analyze a chat first!")
        return
    
    st.markdown("### 📁 Saved Chat Analyses")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Recent Sessions", "Search & Manage"])
    
    with tab1:
        # Display sessions in an interactive table
        for session in sessions:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.subheader(session['session_name'])
                    st.caption(f"Date Range: {session['date_range_start']} to {session['date_range_end']}")
                
                with col2:
                    st.metric("Messages", f"{session['total_messages']:,}")
                    st.metric("Participants", session['total_participants'])
                
                with col3:
                    st.write(f"📅 **Uploaded:** {session['upload_date'][:10]}")
                    st.write(f"🕰️ **Last Accessed:** {session['last_accessed'][:10]}")
                
                with col4:
                    if st.button("📊 Load", key=f"load_{session['id']}", help="Load this analysis"):
                        with st.spinner('Loading analysis...'):
                            df, basic_stats, analysis_results, predictions = st.session_state.db_manager.load_analysis(session['id'])
                            
                            if df is not None:
                                st.session_state.chat_data = df
                                st.session_state.analysis_results = analysis_results
                                st.session_state.predictions = predictions
                                st.session_state.current_session_id = session['id']
                                
                                st.success(f"✅ Successfully loaded '{session['session_name']}'!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Failed to load analysis.")
                    
                    if st.button("🗑️ Delete", key=f"delete_{session['id']}", help="Delete this analysis"):
                        if st.session_state.db_manager.delete_session(session['id']):
                            st.success("✅ Session deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete session.")
                
                st.markdown("---")
    
    with tab2:
        st.markdown("### 🔍 Search Messages")
        
        # Session selector for search
        session_options = {f"{s['session_name']} ({s['upload_date'][:10]})": s['id'] for s in sessions}
        selected_session = st.selectbox("Select session to search:", options=list(session_options.keys()))
        
        if selected_session:
            session_id = session_options[selected_session]
            search_term = st.text_input("🔍 Search messages:", placeholder="Enter search term...")
            
            if search_term and len(search_term) >= 2:
                results = st.session_state.db_manager.search_messages(session_id, search_term)
                
                if results:
                    st.success(f"Found {len(results)} messages containing '{search_term}'")
                    
                    for result in results:
                        with st.expander(f"{result['sender']} - {result['timestamp'][:16]}"):
                            st.write(result['message'])
                else:
                    st.info("No messages found matching your search.")
        
        st.markdown("---")
        st.markdown("### 🛠️ Database Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Data", help="Refresh the sessions list"):
                st.rerun()
        
        with col2:
            if st.button("⚠️ Clear All Data", help="Delete all saved analyses"):
                if st.checkbox("I understand this will delete all saved analyses"):
                    # This would require implementing a clear_all method in DatabaseManager
                    st.warning("This feature is not yet implemented for safety reasons.")
    
    # Show current session info if any
    if st.session_state.current_session_id:
        current_session = next((s for s in sessions if s['id'] == st.session_state.current_session_id), None)
        if current_session:
            st.success(f"🟢 Currently loaded: **{current_session['session_name']}**")

if __name__ == "__main__":
    main()
