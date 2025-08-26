"""
WhatsApp Chat Visualizer Module
Creates interactive visualizations using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import colorsys

class ChatVisualizer:
    def __init__(self, df, analysis_results):
        self.df = df
        self.analysis = analysis_results
        self.color_palette = px.colors.qualitative.Plotly
        
    def create_monthly_timeline(self):
        """Create interactive timeline of messages aggregated by month"""

        # Ensure 'date' is datetime
        df_copy = self.df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])

        # Aggregate messages by month
        monthly_counts = (
            df_copy
            .groupby(df_copy['date'].dt.to_period("M"))
            .size()
            .reset_index(name='count')
        )
        monthly_counts['date'] = monthly_counts['date'].dt.to_timestamp()

        # Rolling average (3 months for smoother trends)
        monthly_counts['rolling_avg'] = (
            monthly_counts['count']
            .rolling(window=3, min_periods=1)
            .mean()
        )

        # Create figure
        fig = go.Figure()

        # Bar for total messages each month
        fig.add_trace(go.Bar(
            x=monthly_counts['date'],
            y=monthly_counts['count'],
            name='Messages',
            marker=dict(color='rgba(31, 119, 180, 0.6)'),
            hovertemplate='<b>Month:</b> %{x|%b %Y}<br><b>Messages:</b> %{y}<extra></extra>'
        ))

        # Rolling average line
        fig.add_trace(go.Scatter(
            x=monthly_counts['date'],
            y=monthly_counts['rolling_avg'],
            mode='lines+markers',
            name='3-Month Average',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6),
            hovertemplate='<b>Month:</b> %{x|%b %Y}<br><b>Avg:</b> %{y:.1f}<extra></extra>'
        ))

        # Fancy layout
        fig.update_layout(
            title='📅 Monthly Message Timeline',
            xaxis_title='Month',
            yaxis_title='Number of Messages',
            hovermode='x unified',
            showlegend=True,
            height=500,
            template='plotly_white',
            bargap=0.2
        )

        return fig

    def create_message_timeline(self):
        """Create interactive timeline of messages"""
        
        daily_counts = self.df.groupby('date').size().reset_index(name='count')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_counts['date'],
            y=daily_counts['count'],
            mode='lines+markers',
            name='Daily Messages',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6),
            hovertemplate='<b>Date:</b> %{x}<br><b>Messages:</b> %{y}<extra></extra>'
        ))
        
        # Add rolling average
        daily_counts['rolling_avg'] = daily_counts['count'].rolling(window=7, min_periods=1).mean()
        
        fig.add_trace(go.Scatter(
            x=daily_counts['date'],
            y=daily_counts['rolling_avg'],
            mode='lines',
            name='7-day Average',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='<b>Date:</b> %{x}<br><b>7-day Avg:</b> %{y:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Message Timeline',
            xaxis_title='Date',
            yaxis_title='Number of Messages',
            hovermode='x unified',
            showlegend=True,
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def create_user_activity_chart(self):
        """Create interactive user activity chart"""
        
        user_stats = self.analysis['user_stats']
        
        # Ensure user_stats is a DataFrame
        if isinstance(user_stats, dict):
            user_stats = pd.DataFrame(user_stats)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Messages by User', 'Words by User', 
                          'Emojis by User', 'Media Shared'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Messages
        fig.add_trace(
            go.Bar(
                x=user_stats['user'].tolist() if hasattr(user_stats['user'], 'tolist') else list(user_stats['user']),
                y=user_stats['message_count'].tolist() if hasattr(user_stats['message_count'], 'tolist') else list(user_stats['message_count']),
                name='Messages',
                marker_color='#1f77b4',
                hovertemplate='<b>%{x}</b><br>Messages: %{y}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Words
        fig.add_trace(
            go.Bar(
                x=user_stats['user'].tolist() if hasattr(user_stats['user'], 'tolist') else list(user_stats['user']),
                y=user_stats['word_count'].tolist() if hasattr(user_stats['word_count'], 'tolist') else list(user_stats['word_count']),
                name='Words',
                marker_color='#ff7f0e',
                hovertemplate='<b>%{x}</b><br>Words: %{y}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Emojis
        fig.add_trace(
            go.Bar(
                x=user_stats['user'].tolist() if hasattr(user_stats['user'], 'tolist') else list(user_stats['user']),
                y=user_stats['emoji_count'].tolist() if hasattr(user_stats['emoji_count'], 'tolist') else list(user_stats['emoji_count']),
                name='Emojis',
                marker_color='#2ca02c',
                hovertemplate='<b>%{x}</b><br>Emojis: %{y}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Media
        fig.add_trace(
            go.Bar(
                x=user_stats['user'].tolist() if hasattr(user_stats['user'], 'tolist') else list(user_stats['user']),
                y=user_stats['media_count'].tolist() if hasattr(user_stats['media_count'], 'tolist') else list(user_stats['media_count']),
                name='Media',
                marker_color='#d62728',
                hovertemplate='<b>%{x}</b><br>Media: %{y}<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_layout(
            height=700,
            showlegend=False,
            title_text="User Activity Analysis",
            template='plotly_white'
        )
        
        return fig
    
    def create_hourly_heatmap(self):
        """Create activity heatmap"""
        
        heatmap_data = self.analysis['temporal_analysis']['heatmap_data']
        
        # Prepare data for heatmap
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        z_values = []
        for day in days:
            day_values = []
            for hour in hours:
                value = next((item['count'] for item in heatmap_data 
                            if item['day'] == day and item['hour'] == hour), 0)
                day_values.append(value)
            z_values.append(day_values)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=[f"{h:02d}:00" for h in hours],
            y=days,
            colorscale='Viridis',
            hovertemplate='<b>%{y}</b><br>Time: %{x}<br>Messages: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Activity Heatmap - Messages by Day and Hour',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    def create_emoji_chart(self):
        """Create emoji usage chart"""
        import ast
        emoji_data = self.analysis['emoji_analysis']
        top_emojis_raw = emoji_data['top_emojis'][:15]
        top_emojis = []
        if top_emojis_raw:
        # Safely convert each string "(emoji, count)" into a tuple
            for item in top_emojis_raw:
                try:
                    tup = ast.literal_eval(item)  # ('🙏', 9)
                    if isinstance(tup, tuple) and len(tup) == 2:
                        top_emojis.append(tup)
                except Exception:
                    continue

            # Now split into lists
            emojis = [t[0] for t in top_emojis]
            counts = [t[1] for t in top_emojis]

            print("emojis", emojis)
            print("counts", counts)
            fig = go.Figure(data=[
                go.Bar(
                    x=counts,
                    y=emojis,
                    orientation='h',
                    # marker=dict(
                    #     color=counts,
                    #     colorscale='Viridis',
                    #     showscale=False
                    # ),
                    marker=dict(color="#1f77b4"),
                    hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title='Top 15 Most Used Emojis',
                xaxis_title='Usage Count',
                yaxis_title='Emoji',
                height=500,
                template='plotly_white',
                yaxis=dict(tickfont=dict(size=20))
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="No emojis found in chat",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=400)
        
        return fig
    
    def create_word_cloud(self):
        """Create word cloud visualization"""
        
        word_freq = self.analysis['word_analysis']['word_frequency']
        
        if word_freq:
            # Generate word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis',
                max_words=100
            ).generate_from_frequencies(word_freq)
            
            # Convert to base64 for display
            img = BytesIO()
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            img.seek(0)
            encoded = base64.b64encode(img.read()).decode()
            
            return f"data:image/png;base64,{encoded}"
        
        return None
    
    def create_sentiment_timeline(self):
        """Create sentiment analysis timeline"""
        
        sentiment_data = self.analysis['sentiment_analysis']['sentiment_over_time']
        print("sentiment_data", sentiment_data)
        if sentiment_data:
            df_sentiment = pd.DataFrame(sentiment_data)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_sentiment['date'],
                y=df_sentiment['compound'],
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6),
                hovertemplate='<b>Date:</b> %{x}<br><b>Sentiment:</b> %{y:.3f}<extra></extra>'
            ))
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            # Add colored regions
            fig.add_hrect(y0=0, y1=1, fillcolor="green", opacity=0.1)
            fig.add_hrect(y0=-1, y1=0, fillcolor="red", opacity=0.1)
            
            fig.update_layout(
                title='Sentiment Analysis Over Time',
                xaxis_title='Date',
                yaxis_title='Sentiment Score',
                yaxis=dict(range=[-1, 1]),
                height=400,
                template='plotly_white'
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for sentiment analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=400)
        
        return fig
    
    def create_response_time_chart(self):
        """Create response time analysis chart"""
        
        user_stats = self.analysis['user_stats']
        
        # Ensure user_stats is a DataFrame
        if isinstance(user_stats, dict):
            user_stats = pd.DataFrame(user_stats)
        
        # Filter users with response time data
        users_with_response = user_stats[user_stats['avg_response_time_minutes'].notna()]
        
        if not users_with_response.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=users_with_response['user'],
                y=users_with_response['avg_response_time_minutes'],
                name='Avg Response Time',
                marker_color='#1f77b4',
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=users_with_response['max_response_time_minutes'] - users_with_response['avg_response_time_minutes'],
                    arrayminus=users_with_response['avg_response_time_minutes'] - users_with_response['min_response_time_minutes']
                ),
                hovertemplate='<b>%{x}</b><br>Avg: %{y:.1f} min<extra></extra>'
            ))
            
            fig.update_layout(
                title='Average Response Time by User',
                xaxis_title='User',
                yaxis_title='Response Time (minutes)',
                height=400,
                template='plotly_white'
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for response time analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=400)
        
        return fig
    
    def create_prediction_chart(self, predictions):
        """Create chart for activity predictions"""
        
        daily_pred = pd.DataFrame(predictions['future_activity']['daily_predictions'])
        
        if not daily_pred.empty:
            fig = go.Figure()
            
            # Historical data
            historical = self.df.groupby('date').size().reset_index(name='count')
            recent_historical = historical.tail(30)
            
            fig.add_trace(go.Scatter(
                x=recent_historical['date'],
                y=recent_historical['count'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))
            
            # Predictions
            fig.add_trace(go.Scatter(
                x=daily_pred['date'],
                y=daily_pred['predicted_messages'],
                mode='lines+markers',
                name='Predicted',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title='Activity Prediction for Next 7 Days',
                xaxis_title='Date',
                yaxis_title='Number of Messages',
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for predictions",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=400)
        
        return fig
    
    def create_optimal_time_chart(self, predictions):
        """Create visualization for optimal messaging times"""
        
        engagement_data = predictions['optimal_messaging_times']['engagement_heatmap']
        
        if engagement_data:
            df_engagement = pd.DataFrame(engagement_data)
            
            # Prepare data for heatmap
            days = list(range(7))
            hours = list(range(24))
            
            z_values = []
            for day in days:
                day_values = []
                for hour in hours:
                    value = df_engagement[
                        (df_engagement['day_of_week'] == day) & 
                        (df_engagement['hour'] == hour)
                    ]['engagement_score'].values
                    day_values.append(value[0] if len(value) > 0 else 0)
                z_values.append(day_values)
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            fig = go.Figure(data=go.Heatmap(
                z=z_values,
                x=[f"{h:02d}:00" for h in hours],
                y=day_names,
                colorscale='RdYlGn',
                hovertemplate='<b>%{y}</b><br>Time: %{x}<br>Engagement: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Optimal Messaging Times - Engagement Heatmap',
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week',
                height=400,
                template='plotly_white'
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for engagement analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=400)
        
        return fig
    
    def create_conversation_flow_chart(self):
        """Create conversation flow visualization"""
        
        flow_data = self.analysis['conversation_flow']
        
        if 'chain_by_user' in flow_data and flow_data['chain_by_user']:
            users = list(flow_data['chain_by_user'].keys())
            chain_lengths = list(flow_data['chain_by_user'].values())
            
            fig = go.Figure(data=[
                go.Bar(
                    x=users,
                    y=chain_lengths,
                    marker_color='#1f77b4',
                    hovertemplate='<b>%{x}</b><br>Avg Chain Length: %{y:.1f}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title='Average Message Chain Length by User',
                xaxis_title='User',
                yaxis_title='Average Chain Length',
                height=400,
                template='plotly_white'
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for conversation flow analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=400)
        
        return fig
    
    def create_comprehensive_dashboard(self, predictions):
        """Create a comprehensive dashboard with all visualizations"""
        
        dashboard = {
            'timeline': self.create_message_timeline(),
            'user_activity': self.create_user_activity_chart(),
            'hourly_heatmap': self.create_hourly_heatmap(),
            'emoji_chart': self.create_emoji_chart(),
            'word_cloud': self.create_word_cloud(),
            'sentiment_timeline': self.create_sentiment_timeline(),
            'response_time': self.create_response_time_chart(),
            'prediction_chart': self.create_prediction_chart(predictions),
            'optimal_time_chart': self.create_optimal_time_chart(predictions),
            'conversation_flow': self.create_conversation_flow_chart()
        }
        
        return dashboard
