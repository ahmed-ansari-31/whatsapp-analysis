"""
WhatsApp Chat Analyzer Module - High Performance Version
Performs comprehensive analysis on parsed chat data with optimization for large datasets
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
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
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

class HighPerformanceAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.timing = {}
        
        # Pre-compile regex patterns for performance
        self.url_pattern = re.compile(r'http\S+')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        
        # Cache frequently used calculations
        self._user_message_counts = None
        self._date_range = None
        
        print(f"🔧 Initialized analyzer for {len(df)} messages")
    
    def time_and_log(self, operation_name, start_time):
        """Helper method to time operations"""
        elapsed = time.time() - start_time
        self.timing[operation_name] = elapsed
        print(f"⏱️  {operation_name}: {elapsed:.2f}s")
        return elapsed
    
    @property
    def user_message_counts(self):
        """Cached user message counts"""
        if self._user_message_counts is None:
            self._user_message_counts = self.df['sender'].value_counts()
        return self._user_message_counts
    
    @property 
    def date_range(self):
        """Cached date range"""
        if self._date_range is None:
            self._date_range = (self.df['date'].min(), self.df['date'].max())
        return self._date_range
    
    def get_basic_stats(self):
        """Get basic statistics about the chat - optimized"""
        # Use cached values and vectorized operations
        min_date, max_date = self.date_range
        total_days = (max_date - min_date).days + 1
        
        # Handle reaction columns efficiently
        total_reactions = 0
        if 'reaction_count' in self.df.columns:
            total_reactions = self.df['reaction_count'].sum()
        
        stats = {
            'total_messages': len(self.df),
            'total_participants': self.df['sender'].nunique(),
            'total_days': total_days,
            'avg_messages_per_day': len(self.df) / max(1, total_days),
            'total_words': self.df['word_count'].sum() if 'word_count' in self.df.columns else 0,
            'total_media': self.df['is_media'].sum() if 'is_media' in self.df.columns else 0,
            'total_urls': self.df['contains_url'].sum() if 'contains_url' in self.df.columns else 0,
            'total_emojis': self.df['emoji_count'].sum() if 'emoji_count' in self.df.columns else 0,
            'total_reactions': total_reactions,
            'date_range': f"{min_date} to {max_date}"
        }
        return stats
    
    def get_user_stats(self):
        """Get statistics for each user - optimized for large datasets"""
        start_time = time.time()
        
        user_stats = []
        
        # Pre-calculate grouped data for efficiency
        user_groups = self.df.groupby('sender')
        
        for user, user_df in user_groups:
            # Basic stats using vectorized operations
            message_count = len(user_df)
            word_count = user_df['word_count'].sum() if 'word_count' in user_df.columns else 0
            avg_words = user_df['word_count'].mean() if 'word_count' in user_df.columns else 0
            emoji_count = user_df['emoji_count'].sum() if 'emoji_count' in user_df.columns else 0
            media_count = user_df['is_media'].sum() if 'is_media' in user_df.columns else 0
            url_count = user_df['contains_url'].sum() if 'contains_url' in user_df.columns else 0
            question_count = user_df['is_question'].sum() if 'is_question' in user_df.columns else 0
            
            # Calculate response times efficiently
            response_times = self.calculate_response_time_fast(user, user_df)
            
            # Calculate reactions
            reactions_given = 0
            reactions_received = 0
            
            if 'reactions_received' in self.df.columns:
                reactions_received = user_df['reaction_count'].sum() if 'reaction_count' in user_df.columns else 0
                
                # Count reactions given (optimized)
                for reactions_list in self.df['reactions_received']:
                    if isinstance(reactions_list, list):
                        reactions_given += sum(1 for r in reactions_list if r.get('reactor') == user)
            
            # Most active periods
            most_active_hour = user_df['hour'].mode().iloc[0] if not user_df.empty and 'hour' in user_df.columns else None
            most_active_day = user_df['day_of_week'].mode().iloc[0] if not user_df.empty and 'day_of_week' in user_df.columns else None
            
            # Sentiment calculation (simplified for performance)
            sentiment_score = self.calculate_user_sentiment_fast(user, user_df)
            
            stats = {
                'user': user,
                'message_count': message_count,
                'message_percentage': (message_count / len(self.df)) * 100,
                'word_count': word_count,
                'avg_words_per_message': avg_words,
                'emoji_count': emoji_count,
                'media_count': media_count,
                'url_count': url_count,
                'question_count': question_count,
                'reactions_given': reactions_given,
                'reactions_received': reactions_received,
                'avg_response_time_minutes': response_times['avg'] if response_times else None,
                'min_response_time_minutes': response_times['min'] if response_times else None,
                'max_response_time_minutes': response_times['max'] if response_times else None,
                'most_active_hour': most_active_hour,
                'most_active_day': most_active_day,
                'sentiment_score': sentiment_score
            }
            
            # Get top emojis efficiently (only for users with emojis)
            if emoji_count > 0 and 'emojis' in user_df.columns:
                all_emojis = []
                for emoji_list in user_df['emojis']:
                    if isinstance(emoji_list, list):
                        all_emojis.extend(emoji_list)
                
                if all_emojis:
                    stats['top_emojis'] = Counter(all_emojis).most_common(5)
                else:
                    stats['top_emojis'] = []
            else:
                stats['top_emojis'] = []
            
            user_stats.append(stats)
        
        self.time_and_log("User Stats Calculation", start_time)
        return pd.DataFrame(user_stats).sort_values('message_count', ascending=False)
    
    def calculate_response_time_fast(self, user, user_df=None):
        """Optimized response time calculation"""
        if user_df is None:
            user_df = self.df[self.df['sender'] == user]
        
        # Get user message indices for faster lookup
        user_indices = set(user_df.index)
        
        response_times = []
        
        # Vectorized approach using numpy
        timestamps = self.df['timestamp'].values
        senders = self.df['sender'].values
        
        for i in range(1, len(self.df)):
            if (i in user_indices and 
                senders[i] == user and 
                senders[i-1] != user):
                
                time_diff = (timestamps[i] - timestamps[i-1]) / np.timedelta64(1, 'm')  # Minutes
                
                if 0 < time_diff <= 1440:  # 0 to 24 hours
                    response_times.append(float(time_diff))
        
        if response_times:
            return {
                'avg': np.mean(response_times),
                'min': np.min(response_times),
                'max': np.max(response_times),
                'median': np.median(response_times),
                'count': len(response_times)
            }
        return None
    
    def calculate_user_sentiment_fast(self, user, user_df=None):
        """Fast sentiment calculation using sampling for large datasets"""
        if user_df is None:
            user_df = self.df[self.df['sender'] == user]
        
        messages = user_df['message'].dropna()
        
        # Sample messages for very active users to improve performance
        if len(messages) > 1000:
            messages = messages.sample(n=500, random_state=42)
        
        sentiments = []
        for message in messages:
            if not pd.isna(message) and '<Media omitted>' not in str(message):
                try:
                    scores = self.sentiment_analyzer.polarity_scores(str(message))
                    sentiments.append(scores['compound'])
                except:
                    continue
                    
                # Break early if we have enough samples
                if len(sentiments) >= 100:
                    break
        
        return np.mean(sentiments) if sentiments else 0
    
    def get_temporal_analysis(self):
        """Optimized temporal analysis using pandas groupby"""
        start_time = time.time()
        # Use vectorized groupby operations
        hourly_dist = self.df['hour'].value_counts().sort_index().to_dict()
        daily_dist = self.df['day_of_week'].value_counts().to_dict()
        
        # Monthly distribution (if available)
        monthly_dist = {}
        if 'month_year' in self.df.columns:
            monthly_dist = self.df['month_year'].value_counts().sort_index().to_dict()
        
        # Time period distribution
        time_period_dist = {}
        if 'time_period' in self.df.columns:
            time_period_dist = self.df['time_period'].value_counts().to_dict()
        
        analysis = {
            'hourly_distribution': hourly_dist,
            'daily_distribution': daily_dist,
            'monthly_distribution': monthly_dist,
            'time_period_distribution': time_period_dist
        }
        
        # Peak activity calculations
        if hourly_dist:
            peak_hour = max(hourly_dist, key=hourly_dist.get)
            analysis['peak_hour'] = peak_hour
            analysis['peak_hour_messages'] = hourly_dist[peak_hour]
        
        if daily_dist:
            peak_day = max(daily_dist, key=daily_dist.get)
            analysis['peak_day'] = peak_day
            analysis['peak_day_messages'] = daily_dist[peak_day]
        
        # Heatmap data (optimized)
        analysis['heatmap_data'] = self.create_heatmap_data_fast()
        
        self.time_and_log("Temporal Analysis", start_time)
        return analysis
    
    def create_heatmap_data_fast(self):
        """Fast heatmap data creation using pivot tables"""
        if 'day_of_week' not in self.df.columns or 'hour' not in self.df.columns:
            return []
        
        # Use pivot table for efficiency
        heatmap_pivot = self.df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        
        # Convert to required format
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        full_data = []
        
        for day in days:
            if day in heatmap_pivot.index:
                for hour in range(24):
                    count = heatmap_pivot.loc[day, hour] if hour in heatmap_pivot.columns else 0
                    full_data.append({'day': day, 'hour': hour, 'count': int(count)})
            else:
                for hour in range(24):
                    full_data.append({'day': day, 'hour': hour, 'count': 0})
        
        return full_data
    
    def get_emoji_analysis(self):
        """Optimized emoji analysis"""
        start_time = time.time()
        if 'emojis' not in self.df.columns:
            return {
                'total_emojis': 0,
                'unique_emojis': 0,
                'top_emojis': [],
                'emoji_by_user': {}
            }
        
        # Flatten all emojis efficiently
        all_emojis = []
        for emoji_list in self.df['emojis']:
            if isinstance(emoji_list, list):
                all_emojis.extend(emoji_list)
        
        emoji_counter = Counter(all_emojis)
        
        # User emoji analysis using groupby
        emoji_by_user = {}
        user_groups = self.df.groupby('sender')
        
        for user, user_df in user_groups:
            user_emojis = []
            for emoji_list in user_df['emojis']:
                if isinstance(emoji_list, list):
                    user_emojis.extend(emoji_list)
            
            if user_emojis:
                user_counter = Counter(user_emojis)
                emoji_by_user[user] = {
                    'total': len(user_emojis),
                    'unique': len(user_counter),
                    'top_5': user_counter.most_common(5)
                }
        
        self.time_and_log("Emoji Analysis", start_time)
        return {
            'total_emojis': len(all_emojis),
            'unique_emojis': len(emoji_counter),
            'top_emojis': emoji_counter.most_common(20),
            'emoji_by_user': emoji_by_user
        }
    
    def get_word_analysis(self):
        """Optimized word analysis using vectorized operations"""
        start_time = time.time()
        # Filter non-media messages
        text_messages = self.df[~self.df.get('is_media', False)]['message'].dropna()
        
        if text_messages.empty:
            return self._empty_word_analysis()
        
        # Combine all text efficiently
        all_text = ' '.join(text_messages.astype(str))
        
        # Clean text using vectorized operations
        all_text = re.sub(r'http\S+', '', all_text)  # Remove URLs
        all_text = re.sub(r'[^\w\s]', ' ', all_text)  # Remove punctuation
        all_text = all_text.lower()
        
        # Tokenize and filter
        words = all_text.split()
        words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        word_freq = Counter(words)
        
        # User-specific analysis (limited for performance)
        user_words = {}
        for user in self.df['sender'].unique()[:10]:  # Limit to top 10 users for performance
            user_text_messages = self.df[
                (self.df['sender'] == user) & 
                (~self.df.get('is_media', False))
            ]['message'].dropna()
            
            if not user_text_messages.empty:
                user_text = ' '.join(user_text_messages.astype(str))
                user_text = re.sub(r'http\S+', '', user_text)
                user_text = re.sub(r'[^\w\s]', ' ', user_text)
                user_text = user_text.lower()
                
                user_word_list = user_text.split()
                user_word_list = [word for word in user_word_list if len(word) > 2 and word not in stop_words]
                
                if user_word_list:
                    user_words[user] = Counter(user_word_list).most_common(10)
        
        self.time_and_log("Word Analysis", start_time)
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'top_words': word_freq.most_common(30),
            'user_top_words': user_words,
            'avg_words_per_message': self.df.get('word_count', pd.Series([0])).mean(),
            'word_frequency': word_freq
        }
    
    def _empty_word_analysis(self):
        """Return empty word analysis structure"""
        return {
            'total_words': 0,
            'unique_words': 0,
            'top_words': [],
            'user_top_words': {},
            'avg_words_per_message': 0,
            'word_frequency': Counter()
        }
    
    def get_reaction_analysis(self):
        """Simplified reaction analysis for performance"""
        if 'reactions_received' not in self.df.columns:
            return {
                'total_reactions': 0,
                'reaction_types': {},
                'most_reacted_messages': [],
                'reaction_givers': {},
                'reaction_receivers': {},
                'reaction_timeline': []
            }
        
        # Quick reaction summary using vectorized operations
        total_reactions = self.df['reaction_count'].sum()
        
        # Most reacted messages (top 10 for performance)
        most_reacted = self.df.nlargest(10, 'reaction_count')[
            ['sender', 'message', 'reaction_count', 'timestamp']
        ].to_dict('records')
        
        # Simplify for performance
        return {
            'total_reactions': int(total_reactions),
            'reaction_types': {},
            'most_reacted_messages': most_reacted,
            'reaction_givers': {},
            'reaction_receivers': {},
            'reaction_timeline': []
        }
    
    def get_conversation_flow(self):
        """Simplified conversation flow analysis"""
        # Basic chain analysis
        chains = []
        current_chain = {'sender': None, 'count': 0}
        
        prev_sender = None
        for sender in self.df['sender']:
            if sender == prev_sender:
                current_chain['count'] += 1
            else:
                if current_chain['count'] > 0:
                    chains.append(current_chain.copy())
                current_chain = {'sender': sender, 'count': 1}
            prev_sender = sender
        
        if current_chain['count'] > 0:
            chains.append(current_chain)
        
        if chains:
            chain_lengths = [c['count'] for c in chains]
            return {
                'avg_chain_length': np.mean(chain_lengths),
                'max_chain_length': np.max(chain_lengths),
                'total_chains': len(chains)
            }
        
        return {'avg_chain_length': 1, 'max_chain_length': 1, 'total_chains': len(self.df)}
    
    def get_sentiment_analysis(self):
        """Optimized sentiment analysis with sampling for large datasets"""
        start_time = time.time()
        # Sample messages for very large datasets
        messages_to_analyze = self.df['message'].dropna()
        
        if len(messages_to_analyze) > 5000:
            messages_to_analyze = messages_to_analyze.sample(n=2000, random_state=42)
            print(f"📊 Sampling {len(messages_to_analyze)} messages for sentiment analysis")
        
        sentiments = []
        batch_size = 100
        
        # Process in batches
        for i in range(0, len(messages_to_analyze), batch_size):
            batch = messages_to_analyze.iloc[i:i+batch_size]
            
            for message in batch:
                if not pd.isna(message) and '<Media omitted>' not in str(message):
                    try:
                        scores = self.sentiment_analyzer.polarity_scores(str(message))
                        sentiments.append(scores['compound'])
                    except:
                        continue
        
        if not sentiments:
            return self._empty_sentiment_analysis()
        
        sentiments = np.array(sentiments)
        
        result = {
            'overall_sentiment': float(np.mean(sentiments)),
            'positive_ratio': float(np.mean(sentiments > 0.05)),
            'negative_ratio': float(np.mean(sentiments < -0.05)),
            'neutral_ratio': float(np.mean((-0.05 <= sentiments) & (sentiments <= 0.05))),
            'sentiment_by_user': {},  # Simplified for performance
            'sentiment_over_time': [],
            'most_positive_messages': [],
            'most_negative_messages': []
        }
        
        self.time_and_log("Sentiment Analysis", start_time)
        return result
    
    def _empty_sentiment_analysis(self):
        """Return empty sentiment analysis structure"""
        return {
            'overall_sentiment': 0,
            'positive_ratio': 0,
            'negative_ratio': 0,
            'neutral_ratio': 1,
            'sentiment_by_user': {},
            'sentiment_over_time': [],
            'most_positive_messages': [],
            'most_negative_messages': []
        }
    
    def get_activity_patterns(self):
        """Optimized activity pattern analysis"""
        daily_counts = self.df.groupby('date').size()
        
        patterns = {
            'avg_daily_messages': float(daily_counts.mean()),
            'std_daily_messages': float(daily_counts.std()) if len(daily_counts) > 1 else 0.0,
            'max_daily_messages': int(daily_counts.max()),
            'min_daily_messages': int(daily_counts.min()),
            'most_active_date': str(daily_counts.idxmax()),
            'least_active_date': str(daily_counts.idxmin())
        }
        
        # High activity days (simplified)
        if patterns['std_daily_messages'] > 0:
            threshold = patterns['avg_daily_messages'] + (2 * patterns['std_daily_messages'])
            anomaly_days = daily_counts[daily_counts > threshold]
            patterns['high_activity_days'] = {str(k): int(v) for k, v in anomaly_days.to_dict().items()}
        else:
            patterns['high_activity_days'] = {}
        
        return patterns
    
    def get_performance_stats(self):
        """Get analyzer performance statistics"""
        return {
            'timing': self.timing,
            'total_analysis_time': sum(self.timing.values()),
            'messages_processed': len(self.df),
            'analysis_rate': len(self.df) / sum(self.timing.values()) if self.timing else 0
        }

# Backward compatibility
class ChatAnalyzer(HighPerformanceAnalyzer):
    """Backward compatible wrapper"""
    pass
