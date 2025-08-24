"""
WhatsApp Chat Analyzer Module - Enhanced Version
Performs comprehensive analysis on parsed chat data including reactions
"""

import pandas as pd
import numpy as np
from collections import Counter
import emoji
import re
from datetime import datetime, timedelta
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except:
    stop_words = set()

class ChatAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
    def get_basic_stats(self):
        """Get basic statistics about the chat"""
        # Handle reaction columns if they exist
        total_reactions = 0
        if 'reaction_count' in self.df.columns:
            total_reactions = self.df['reaction_count'].sum()
        
        stats = {
            'total_messages': len(self.df),
            'total_participants': self.df['sender'].nunique(),
            'total_days': (self.df['date'].max() - self.df['date'].min()).days + 1,
            'avg_messages_per_day': len(self.df) / max(1, (self.df['date'].max() - self.df['date'].min()).days + 1),
            'total_words': self.df['word_count'].sum(),
            'total_media': self.df['is_media'].sum(),
            'total_urls': self.df['contains_url'].sum(),
            'total_emojis': self.df['emoji_count'].sum(),
            'total_reactions': total_reactions,
            'date_range': f"{self.df['date'].min()} to {self.df['date'].max()}"
        }
        return stats
    
    def get_user_stats(self):
        """Get statistics for each user"""
        user_stats = []
        
        for user in self.df['sender'].unique():
            user_df = self.df[self.df['sender'] == user]
            
            # Calculate response time
            response_times = self.calculate_response_time(user)
            
            # Calculate reactions given and received
            reactions_given = 0
            reactions_received = 0
            
            if 'reactions_received' in self.df.columns:
                # Count reactions received by this user's messages
                reactions_received = user_df['reaction_count'].sum() if 'reaction_count' in user_df.columns else 0
                
                # Count reactions given by this user (would need to parse reaction data)
                for _, row in self.df.iterrows():
                    if isinstance(row['reactions_received'], list):
                        for reaction in row['reactions_received']:
                            if reaction.get('reactor') == user:
                                reactions_given += 1
            
            stats = {
                'user': user,
                'message_count': len(user_df),
                'message_percentage': (len(user_df) / len(self.df)) * 100,
                'word_count': user_df['word_count'].sum(),
                'avg_words_per_message': user_df['word_count'].mean(),
                'emoji_count': user_df['emoji_count'].sum(),
                'media_count': user_df['is_media'].sum(),
                'url_count': user_df['contains_url'].sum(),
                'question_count': user_df['is_question'].sum(),
                'reactions_given': reactions_given,
                'reactions_received': reactions_received,
                'avg_response_time_minutes': response_times['avg'] if response_times else None,
                'min_response_time_minutes': response_times['min'] if response_times else None,
                'max_response_time_minutes': response_times['max'] if response_times else None,
                'most_active_hour': int(user_df.groupby('hour').size().idxmax()) if not user_df.empty else None,
                'most_active_day': user_df.groupby('day_of_week').size().idxmax() if not user_df.empty else None,
                'sentiment_score': self.calculate_user_sentiment(user)
            }
            
            # Get top emojis for user
            all_emojis = []
            for emoji_list in user_df['emojis']:
                all_emojis.extend(emoji_list)
            
            if all_emojis:
                emoji_counter = Counter(all_emojis)
                stats['top_emojis'] = emoji_counter.most_common(5)
            else:
                stats['top_emojis'] = []
            
            user_stats.append(stats)
        
        return pd.DataFrame(user_stats).sort_values('message_count', ascending=False)
    
    def get_reaction_analysis(self):
        """Analyze reaction patterns"""
        if 'reactions_received' not in self.df.columns:
            return {
                'total_reactions': 0,
                'reaction_types': {},
                'most_reacted_messages': [],
                'reaction_givers': {},
                'reaction_receivers': {},
                'reaction_timeline': []
            }
        
        # Collect all reactions
        all_reactions = []
        reaction_givers = Counter()
        reaction_receivers = Counter()
        reaction_types = Counter()
        
        for _, row in self.df.iterrows():
            if isinstance(row['reactions_received'], list):
                for reaction in row['reactions_received']:
                    all_reactions.append({
                        'timestamp': row['timestamp'],
                        'message_sender': row['sender'],
                        'reactor': reaction.get('reactor'),
                        'reaction': reaction.get('reaction'),
                        'message': row['message'][:100]
                    })
                    
                    reaction_givers[reaction.get('reactor')] += 1
                    reaction_receivers[row['sender']] += 1
                    reaction_types[reaction.get('reaction')] += 1
        
        # Most reacted messages
        most_reacted = self.df.nlargest(10, 'reaction_count')[['sender', 'message', 'reaction_count', 'timestamp']]
        most_reacted_list = []
        for _, row in most_reacted.iterrows():
            most_reacted_list.append({
                'sender': row['sender'],
                'message': row['message'][:100],
                'reaction_count': row['reaction_count'],
                'timestamp': row['timestamp']
            })
        
        # Reaction timeline (by hour)
        reaction_df = pd.DataFrame(all_reactions)
        reaction_timeline = []
        if not reaction_df.empty:
            reaction_df['hour'] = pd.to_datetime(reaction_df['timestamp']).dt.hour
            hourly_reactions = reaction_df.groupby('hour').size()
            reaction_timeline = [{'hour': h, 'count': c} for h, c in hourly_reactions.items()]
        
        return {
            'total_reactions': len(all_reactions),
            'reaction_types': dict(reaction_types.most_common()),
            'most_reacted_messages': most_reacted_list,
            'reaction_givers': dict(reaction_givers.most_common(10)),
            'reaction_receivers': dict(reaction_receivers.most_common(10)),
            'reaction_timeline': reaction_timeline
        }
    
    def calculate_response_time(self, user):
        """Calculate average response time for a user"""
        response_times = []
        
        for i in range(1, len(self.df)):
            if self.df.iloc[i]['sender'] == user and self.df.iloc[i-1]['sender'] != user:
                time_diff = (self.df.iloc[i]['timestamp'] - self.df.iloc[i-1]['timestamp']).total_seconds() / 60
                
                # Only consider responses within 24 hours
                if time_diff < 1440:
                    response_times.append(time_diff)
        
        if response_times:
            return {
                'avg': np.mean(response_times),
                'min': np.min(response_times),
                'max': np.max(response_times),
                'median': np.median(response_times)
            }
        return None
    
    def calculate_user_sentiment(self, user):
        """Calculate average sentiment score for a user"""
        user_messages = self.df[self.df['sender'] == user]['message']
        sentiments = []
        
        for message in user_messages:
            if not pd.isna(message) and '<Media omitted>' not in message:
                try:
                    scores = self.sentiment_analyzer.polarity_scores(str(message))
                    sentiments.append(scores['compound'])
                except:
                    continue
        
        return np.mean(sentiments) if sentiments else 0
    
    def get_temporal_analysis(self):
        """Analyze temporal patterns"""
        analysis = {
            'hourly_distribution': self.df.groupby('hour').size().to_dict(),
            'daily_distribution': self.df.groupby('day_of_week').size().to_dict(),
            'monthly_distribution': self.df.groupby('month_year').size().to_dict() if 'month_year' in self.df.columns else {},
            'time_period_distribution': self.df.groupby('time_period').size().to_dict()
        }
        
        # Find peak activity times
        hourly = self.df.groupby('hour').size()
        analysis['peak_hour'] = int(hourly.idxmax()) if not hourly.empty else 0
        analysis['peak_hour_messages'] = int(hourly.max()) if not hourly.empty else 0
        
        daily = self.df.groupby('day_of_week').size()
        analysis['peak_day'] = daily.idxmax() if not daily.empty else 'Monday'
        analysis['peak_day_messages'] = int(daily.max()) if not daily.empty else 0
        
        # Activity heatmap data
        analysis['heatmap_data'] = self.create_activity_heatmap_data()
        
        return analysis
    
    def create_activity_heatmap_data(self):
        """Create data for activity heatmap"""
        # Create a pivot table of day vs hour
        heatmap_df = self.df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
        
        # Ensure all combinations exist
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        full_data = []
        for day in days:
            for hour in hours:
                existing = heatmap_df[(heatmap_df['day_of_week'] == day) & (heatmap_df['hour'] == hour)]
                if not existing.empty:
                    full_data.append({'day': day, 'hour': hour, 'count': int(existing.iloc[0]['count'])})
                else:
                    full_data.append({'day': day, 'hour': hour, 'count': 0})
        
        return full_data
    
    def get_emoji_analysis(self):
        """Analyze emoji usage"""
        all_emojis = []
        emoji_by_user = {}
        
        for _, row in self.df.iterrows():
            all_emojis.extend(row['emojis'])
            
            if row['sender'] not in emoji_by_user:
                emoji_by_user[row['sender']] = []
            emoji_by_user[row['sender']].extend(row['emojis'])
        
        # Overall emoji statistics
        emoji_counter = Counter(all_emojis)
        
        analysis = {
            'total_emojis': len(all_emojis),
            'unique_emojis': len(emoji_counter),
            'top_emojis': emoji_counter.most_common(20),
            'emoji_by_user': {}
        }
        
        # User-specific emoji analysis
        for user, emojis in emoji_by_user.items():
            user_counter = Counter(emojis)
            analysis['emoji_by_user'][user] = {
                'total': len(emojis),
                'unique': len(user_counter),
                'top_5': user_counter.most_common(5)
            }
        
        return analysis
    
    def get_word_analysis(self):
        """Analyze word usage patterns"""
        # Combine all messages
        all_text = ' '.join(self.df[~self.df['is_media']]['message'].dropna().astype(str))
        
        # Clean text
        all_text = re.sub(r'http\S+', '', all_text)  # Remove URLs
        all_text = re.sub(r'[^\w\s]', ' ', all_text)  # Remove punctuation
        all_text = all_text.lower()
        
        # Tokenize and filter
        words = all_text.split()
        words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Word frequency
        word_freq = Counter(words)
        
        # User-specific word analysis
        user_words = {}
        for user in self.df['sender'].unique():
            user_text = ' '.join(self.df[(self.df['sender'] == user) & (~self.df['is_media'])]['message'].dropna().astype(str))
            user_text = re.sub(r'http\S+', '', user_text)
            user_text = re.sub(r'[^\w\s]', ' ', user_text)
            user_text = user_text.lower()
            
            user_word_list = user_text.split()
            user_word_list = [word for word in user_word_list if len(word) > 2 and word not in stop_words]
            
            if user_word_list:
                user_words[user] = Counter(user_word_list).most_common(10)
        
        analysis = {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'top_words': word_freq.most_common(30),
            'user_top_words': user_words,
            'avg_words_per_message': self.df['word_count'].mean(),
            'word_frequency': word_freq
        }
        
        return analysis
    
    def get_conversation_flow(self):
        """Analyze conversation flow and patterns"""
        flow_analysis = {}
        
        # Message chains (consecutive messages by same user)
        chains = []
        current_chain = {'sender': None, 'count': 0, 'start': None}
        
        for _, row in self.df.iterrows():
            if row['sender'] == current_chain['sender']:
                current_chain['count'] += 1
            else:
                if current_chain['count'] > 0:
                    chains.append(current_chain.copy())
                current_chain = {'sender': row['sender'], 'count': 1, 'start': row['timestamp']}
        
        if current_chain['count'] > 0:
            chains.append(current_chain)
        
        # Analyze chains
        chain_df = pd.DataFrame(chains)
        if not chain_df.empty:
            flow_analysis['avg_chain_length'] = chain_df['count'].mean()
            flow_analysis['max_chain_length'] = chain_df['count'].max()
            flow_analysis['chain_by_user'] = chain_df.groupby('sender')['count'].mean().to_dict()
        
        # Conversation initiators (messages after long gaps)
        gap_threshold = 3600  # 1 hour in seconds
        initiators = []
        
        for i in range(1, len(self.df)):
            time_gap = (self.df.iloc[i]['timestamp'] - self.df.iloc[i-1]['timestamp']).total_seconds()
            if time_gap > gap_threshold:
                initiators.append(self.df.iloc[i]['sender'])
        
        if initiators:
            initiator_counts = Counter(initiators)
            flow_analysis['conversation_initiators'] = dict(initiator_counts.most_common())
            flow_analysis['most_frequent_initiator'] = initiator_counts.most_common(1)[0] if initiator_counts else None
        
        return flow_analysis
    
    def get_sentiment_analysis(self):
        """Perform sentiment analysis on messages"""
        sentiments = []
        
        for _, row in self.df.iterrows():
            if not pd.isna(row['message']) and '<Media omitted>' not in row['message']:
                try:
                    scores = self.sentiment_analyzer.polarity_scores(str(row['message']))
                    sentiments.append({
                        'timestamp': row['timestamp'],
                        'sender': row['sender'],
                        'message': str(row['message'])[:100],  # First 100 chars
                        'positive': scores['pos'],
                        'negative': scores['neg'],
                        'neutral': scores['neu'],
                        'compound': scores['compound']
                    })
                except:
                    continue
        
        sentiment_df = pd.DataFrame(sentiments)
        
        if not sentiment_df.empty:
            analysis = {
                'overall_sentiment': sentiment_df['compound'].mean(),
                'positive_ratio': (sentiment_df['compound'] > 0.05).mean(),
                'negative_ratio': (sentiment_df['compound'] < -0.05).mean(),
                'neutral_ratio': ((sentiment_df['compound'] >= -0.05) & (sentiment_df['compound'] <= 0.05)).mean(),
                'sentiment_by_user': sentiment_df.groupby('sender')['compound'].mean().to_dict(),
                'sentiment_over_time': self.calculate_sentiment_over_time(sentiment_df),
                'most_positive_messages': sentiment_df.nlargest(5, 'compound')[['sender', 'message', 'compound']].to_dict('records'),
                'most_negative_messages': sentiment_df.nsmallest(5, 'compound')[['sender', 'message', 'compound']].to_dict('records')
            }
        else:
            analysis = {
                'overall_sentiment': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 1,
                'sentiment_by_user': {},
                'sentiment_over_time': [],
                'most_positive_messages': [],
                'most_negative_messages': []
            }
        
        return analysis
    
    def calculate_sentiment_over_time(self, sentiment_df):
        """Calculate sentiment trends over time"""
        sentiment_df['date'] = sentiment_df['timestamp'].dt.date
        daily_sentiment = sentiment_df.groupby('date')['compound'].mean().reset_index()
        return daily_sentiment.to_dict('records')
    
    def get_activity_patterns(self):
        """Identify activity patterns and anomalies"""
        patterns = {}
        
        # Daily message counts
        daily_counts = self.df.groupby('date').size()
        
        patterns['avg_daily_messages'] = daily_counts.mean()
        patterns['std_daily_messages'] = daily_counts.std() if len(daily_counts) > 1 else 0
        patterns['max_daily_messages'] = int(daily_counts.max()) if not daily_counts.empty else 0
        patterns['min_daily_messages'] = int(daily_counts.min()) if not daily_counts.empty else 0
        patterns['most_active_date'] = daily_counts.idxmax() if not daily_counts.empty else None
        patterns['least_active_date'] = daily_counts.idxmin() if not daily_counts.empty else None
        
        # Identify anomaly days (>2 std from mean)
        if patterns['std_daily_messages'] > 0:
            threshold = patterns['avg_daily_messages'] + (2 * patterns['std_daily_messages'])
            anomaly_days = daily_counts[daily_counts > threshold]
            patterns['high_activity_days'] = {str(k): int(v) for k, v in anomaly_days.to_dict().items()}
        else:
            patterns['high_activity_days'] = {}
        
        # Weekly patterns
        if 'year_week' not in self.df.columns:
            self.df['week'] = self.df['timestamp'].dt.isocalendar().week
            self.df['year_week'] = self.df['timestamp'].dt.strftime('%Y-%U')
        
        weekly_counts = self.df.groupby('year_week').size()
        
        patterns['avg_weekly_messages'] = weekly_counts.mean()
        patterns['weekly_trend'] = {str(k): int(v) for k, v in weekly_counts.to_dict().items()}
        
        return patterns
