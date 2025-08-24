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
1/2/24, 11:06 AM - Bob Wilson: Sounds perfect! 🍝"""
    
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
            options=["Upload Chat", "Analysis Dashboard", "User Insights", 
                    "Predictions", "Visualizations", "Export Report"],
            icons=["cloud-upload", "dashboard", "people", 
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
                
                st.success("✅ Sample data loaded successfully!")
                st.rerun()
    
    # Main content based on selection
    if selected == "Upload Chat":
        upload_section()
    elif selected == "Analysis Dashboard":
        if st.session_state.chat_data is not None:
            analysis_dashboard()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first!")
    elif selected == "User Insights":
        if st.session_state.chat_data is not None:
            user_insights()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first!")
    elif selected == "Predictions":
        if st.session_state.predictions is not None:
            predictions_section()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first!")
    elif selected == "Visualizations":
        if st.session_state.chat_data is not None:
            visualizations_section()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first!")
    elif selected == "Export Report":
        if st.session_state.analysis_results is not None:
            export_report()
        else:
            st.warning("⚠️ Please upload a WhatsApp chat file first!")

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
        peak_df['Hour'] = peak_df['Hour'].apply(lambda x: f"{x:02d}:00")
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

if __name__ == "__main__":
    main()
