"""
WhatsApp Chat Predictor Module - Enhanced Version
Provides ML-based predictions for optimal messaging times and user activity
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class ChatPredictor:
    def __init__(self, df):
        self.df = df.copy()
        self.prepare_data()
        self.models = {}
        
    def prepare_data(self):
        """Prepare data for prediction models"""
        # Create hourly activity data
        self.hourly_data = self.df.groupby(['date', 'hour']).size().reset_index(name='message_count')
        
        # Add features
        self.hourly_data['day_of_week'] = pd.to_datetime(self.hourly_data['date']).dt.dayofweek
        self.hourly_data['month'] = pd.to_datetime(self.hourly_data['date']).dt.month
        self.hourly_data['day'] = pd.to_datetime(self.hourly_data['date']).dt.day
        self.hourly_data['is_weekend'] = self.hourly_data['day_of_week'].isin([5, 6]).astype(int)
        
        # Create complete hourly grid
        date_range = pd.date_range(start=self.df['date'].min(), end=self.df['date'].max(), freq='D')
        hour_range = range(24)
        
        complete_grid = []
        for date in date_range:
            for hour in hour_range:
                complete_grid.append({
                    'date': date.date(),
                    'hour': hour,
                    'day_of_week': date.dayofweek,
                    'month': date.month,
                    'day': date.day,
                    'is_weekend': int(date.dayofweek in [5, 6])
                })
        
        complete_df = pd.DataFrame(complete_grid)
        
        # Merge with actual data
        self.hourly_data = complete_df.merge(
            self.hourly_data[['date', 'hour', 'message_count']], 
            on=['date', 'hour'], 
            how='left'
        )
        self.hourly_data['message_count'].fillna(0, inplace=True)
        
        # Add lag features
        for lag in [1, 2, 3, 7, 14]:
            self.hourly_data[f'lag_{lag}'] = self.hourly_data['message_count'].shift(lag * 24)
        
        # Add rolling statistics
        self.hourly_data['rolling_mean_7d'] = self.hourly_data['message_count'].rolling(window=7*24, min_periods=1).mean()
        self.hourly_data['rolling_std_7d'] = self.hourly_data['message_count'].rolling(window=7*24, min_periods=1).std()
        
        # Drop NaN values
        self.hourly_data.dropna(inplace=True)
    
    def predict_optimal_messaging_time(self):
        """Predict optimal times to send messages for maximum engagement"""
        
        # Aggregate activity by hour and day
        activity_matrix = self.df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        
        # Calculate engagement score (messages + responses)
        engagement_scores = {}
        
        for day in range(7):
            for hour in range(24):
                # Get messages sent at this time
                messages_at_time = self.df[
                    (self.df['timestamp'].dt.dayofweek == day) & 
                    (self.df['hour'] == hour)
                ]
                
                if len(messages_at_time) > 0:
                    # Calculate average response rate within next 2 hours
                    response_count = 0
                    for _, msg in messages_at_time.iterrows():
                        next_messages = self.df[
                            (self.df['timestamp'] > msg['timestamp']) & 
                            (self.df['timestamp'] <= msg['timestamp'] + timedelta(hours=2)) &
                            (self.df['sender'] != msg['sender'])
                        ]
                        response_count += len(next_messages)
                    
                    engagement_score = response_count / len(messages_at_time)
                else:
                    engagement_score = 0
                
                engagement_scores[(day, hour)] = engagement_score
        
        # Convert to DataFrame for analysis
        engagement_df = pd.DataFrame([
            {'day_of_week': k[0], 'hour': k[1], 'engagement_score': v}
            for k, v in engagement_scores.items()
        ])
        
        # Get top times for each day
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        optimal_times = {}
        
        for day in range(7):
            day_data = engagement_df[engagement_df['day_of_week'] == day]
            if not day_data.empty:
                top_hours = day_data.nlargest(3, 'engagement_score')
                optimal_times[day_names[day]] = [
                    {
                        'hour': int(row['hour']),  # Convert to int
                        'time': f"{int(row['hour']):02d}:00",  # Convert to int before formatting
                        'engagement_score': row['engagement_score']
                    }
                    for _, row in top_hours.iterrows()
                ]
        
        # Overall best times
        overall_best = engagement_df.nlargest(10, 'engagement_score')
        overall_best_times = [
            {
                'day': day_names[int(row['day_of_week'])],  # Convert to int
                'hour': int(row['hour']),  # Convert to int
                'time': f"{day_names[int(row['day_of_week'])]} {int(row['hour']):02d}:00",  # Convert to int
                'engagement_score': row['engagement_score']
            }
            for _, row in overall_best.iterrows()
        ]
        
        return {
            'optimal_times_by_day': optimal_times,
            'overall_best_times': overall_best_times,
            'engagement_heatmap': engagement_df.to_dict('records')
        }
    
    def predict_future_activity(self, days_ahead=7):
        """Predict future chat activity"""
        
        if len(self.hourly_data) < 10:
            # Not enough data for prediction
            return {
                'hourly_predictions': [],
                'daily_predictions': [],
                'model_accuracy': 0,
                'peak_predicted_hours': {},
                'total_predicted_messages': 0
            }
        
        # Prepare features
        feature_cols = ['hour', 'day_of_week', 'month', 'day', 'is_weekend']
        
        # Add lag features if they exist
        for col in ['lag_1', 'lag_2', 'lag_3', 'lag_7', 'rolling_mean_7d']:
            if col in self.hourly_data.columns:
                feature_cols.append(col)
        
        # Filter to existing columns
        feature_cols = [col for col in feature_cols if col in self.hourly_data.columns]
        
        X = self.hourly_data[feature_cols]
        y = self.hourly_data['message_count']
        
        # Handle small datasets
        if len(X) < 20:
            # Use simple average for prediction
            avg_by_hour = self.hourly_data.groupby('hour')['message_count'].mean()
            
            predictions = []
            last_date = pd.to_datetime(self.df['date'].max())
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead, freq='D')
            
            for date in future_dates:
                for hour in range(24):
                    pred_value = avg_by_hour.get(hour, 0)
                    predictions.append({
                        'date': date.date(),
                        'hour': hour,
                        'datetime': datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=hour),
                        'predicted_messages': max(0, int(pred_value)),
                        'day_name': date.strftime('%A')
                    })
            
            predictions_df = pd.DataFrame(predictions)
            daily_predictions = predictions_df.groupby(['date', 'day_name'])['predicted_messages'].sum().reset_index()
            
            return {
                'hourly_predictions': predictions_df.to_dict('records'),
                'daily_predictions': daily_predictions.to_dict('records'),
                'model_accuracy': 0.5,  # Simple model
                'peak_predicted_hours': avg_by_hour.nlargest(5).to_dict() if len(avg_by_hour) > 0 else {},
                'total_predicted_messages': predictions_df['predicted_messages'].sum()
            }
        
        # Split data for larger datasets
        split_index = int(len(X) * 0.8)
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        
        # Train multiple models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5),
            'linear_regression': LinearRegression()
        }
        
        best_model = None
        best_score = -float('inf')
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                score = model.score(X_test, y_test) if len(X_test) > 0 else 0
                self.models[name] = model
                
                if score > best_score:
                    best_score = score
                    best_model = model
            except:
                continue
        
        if best_model is None:
            best_model = LinearRegression()
            best_model.fit(X, y)
            best_score = 0.5
        
        # Generate future predictions
        last_date = pd.to_datetime(self.df['date'].max())
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead, freq='D')
        
        predictions = []
        
        for date in future_dates:
            for hour in range(24):
                # Prepare features for prediction
                features = {
                    'hour': hour,
                    'day_of_week': date.dayofweek,
                    'month': date.month,
                    'day': date.day,
                    'is_weekend': int(date.dayofweek in [5, 6])
                }
                
                # Add lag features if needed
                if 'lag_1' in feature_cols:
                    recent_data = self.hourly_data.tail(14*24) if len(self.hourly_data) > 14*24 else self.hourly_data
                    features['lag_1'] = recent_data['message_count'].mean()
                    if 'lag_2' in feature_cols:
                        features['lag_2'] = features['lag_1'] * 0.9
                    if 'lag_3' in feature_cols:
                        features['lag_3'] = features['lag_1'] * 0.8
                    if 'lag_7' in feature_cols:
                        features['lag_7'] = features['lag_1'] * 0.7
                    if 'rolling_mean_7d' in feature_cols:
                        features['rolling_mean_7d'] = features['lag_1']
                
                # Make prediction
                feature_vector = pd.DataFrame([features])[feature_cols]
                try:
                    pred = best_model.predict(feature_vector)[0]
                except:
                    pred = 0
                
                predictions.append({
                    'date': date.date(),
                    'hour': hour,
                    'datetime': datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=hour),
                    'predicted_messages': max(0, int(pred)),
                    'day_name': date.strftime('%A')
                })
        
        predictions_df = pd.DataFrame(predictions)
        
        # Aggregate daily predictions
        daily_predictions = predictions_df.groupby(['date', 'day_name'])['predicted_messages'].sum().reset_index()
        
        # Identify peak hours in predictions
        peak_hours = predictions_df.groupby('hour')['predicted_messages'].mean().nlargest(5)
        
        return {
            'hourly_predictions': predictions_df.to_dict('records'),
            'daily_predictions': daily_predictions.to_dict('records'),
            'model_accuracy': max(0, best_score),
            'peak_predicted_hours': peak_hours.to_dict() if len(peak_hours) > 0 else {},
            'total_predicted_messages': predictions_df['predicted_messages'].sum()
        }
    
    def predict_user_activity(self):
        """Predict when specific users are likely to be active"""
        
        user_predictions = {}
        
        for user in self.df['sender'].unique():
            user_df = self.df[self.df['sender'] == user]
            
            if len(user_df) < 5:
                continue
            
            # Create activity pattern
            user_activity = user_df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
            
            # Calculate probability of activity
            total_messages = len(user_df)
            user_activity['probability'] = user_activity['count'] / total_messages
            
            # Find peak activity times
            peak_times = user_activity.nlargest(10, 'probability')
            
            # Create prediction model for this user
            user_hourly = user_df.groupby(['date', 'hour']).size().reset_index(name='message_count')
            
            if len(user_hourly) > 10:  # Need enough data for prediction
                # Add features
                user_hourly['day_of_week'] = pd.to_datetime(user_hourly['date']).dt.dayofweek
                user_hourly['is_weekend'] = user_hourly['day_of_week'].isin([5, 6]).astype(int)
                
                # Simple prediction based on historical patterns
                avg_by_hour = user_hourly.groupby('hour')['message_count'].mean()
                avg_by_day = user_hourly.groupby('day_of_week')['message_count'].mean()
                
                user_predictions[user] = {
                    'peak_hours': peak_times[['day_of_week', 'hour', 'probability']].to_dict('records'),
                    'avg_messages_by_hour': avg_by_hour.to_dict(),
                    'avg_messages_by_day': avg_by_day.to_dict(),
                    'total_messages': total_messages,
                    'active_probability': user_activity.to_dict('records')
                }
        
        return user_predictions
    
    def predict_conversation_topics(self):
        """Predict trending topics based on recent conversations"""
        
        # Check if we have enough recent data
        if len(self.df) < 10:
            return {
                'trending_topics': [],
                'topic_evolution': []
            }
        
        # Get recent messages (last 30 days or all if less)
        recent_date = self.df['date'].max() - timedelta(days=30)
        recent_messages = self.df[self.df['date'] >= recent_date] if len(self.df) > 100 else self.df
        
        # Extract keywords from recent messages
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Clean messages
        messages = recent_messages[~recent_messages['is_media']]['message'].dropna()
        messages = messages.apply(lambda x: re.sub(r'http\S+', '', str(x)))  # Remove URLs
        
        if len(messages) > 5:
            try:
                # TF-IDF analysis
                vectorizer = TfidfVectorizer(
                    max_features=20, 
                    stop_words='english', 
                    ngram_range=(1, 2),
                    min_df=2 if len(messages) > 20 else 1
                )
                tfidf_matrix = vectorizer.fit_transform(messages)
                
                # Get feature names and scores
                feature_names = vectorizer.get_feature_names_out()
                scores = tfidf_matrix.sum(axis=0).A1
                
                # Create topic predictions
                topics = []
                for idx, feature in enumerate(feature_names):
                    topics.append({
                        'topic': feature,
                        'score': float(scores[idx]),
                        'trend': 'rising' if scores[idx] > np.median(scores) else 'stable'
                    })
                
                topics.sort(key=lambda x: x['score'], reverse=True)
                
                return {
                    'trending_topics': topics[:10],
                    'topic_evolution': self.analyze_topic_evolution(messages)
                }
            except:
                pass
        
        return {
            'trending_topics': [],
            'topic_evolution': []
        }
    
    def analyze_topic_evolution(self, messages):
        """Analyze how topics evolve over time"""
        
        # Group messages by week
        weekly_messages = []
        for week_offset in range(min(4, len(self.df) // 7)):
            week_start = self.df['date'].max() - timedelta(weeks=week_offset+1)
            week_end = self.df['date'].max() - timedelta(weeks=week_offset)
            
            week_msgs = self.df[
                (self.df['date'] >= week_start) & 
                (self.df['date'] < week_end) & 
                (~self.df['is_media'])
            ]['message'].dropna()
            
            if len(week_msgs) > 3:
                weekly_messages.append({
                    'week': f"Week {4-week_offset}",
                    'messages': ' '.join(week_msgs.astype(str))
                })
        
        # Extract top words for each week
        evolution = []
        for week_data in weekly_messages:
            words = re.sub(r'[^\w\s]', ' ', week_data['messages'].lower()).split()
            words = [w for w in words if len(w) > 3]
            
            if words:
                word_freq = pd.Series(words).value_counts().head(5)
                evolution.append({
                    'week': week_data['week'],
                    'top_words': word_freq.to_dict()
                })
        
        return evolution
    
    def get_prediction_summary(self):
        """Get comprehensive prediction summary"""
        
        try:
            summary = {
                'optimal_messaging_times': self.predict_optimal_messaging_time(),
                'future_activity': self.predict_future_activity(),
                'user_activity_predictions': self.predict_user_activity(),
                'trending_topics': self.predict_conversation_topics()
            }
            
            # Add recommendations
            summary['recommendations'] = self.generate_recommendations(summary)
            
            return summary
        except Exception as e:
            # Return safe defaults if prediction fails
            return {
                'optimal_messaging_times': {
                    'optimal_times_by_day': {},
                    'overall_best_times': [],
                    'engagement_heatmap': []
                },
                'future_activity': {
                    'hourly_predictions': [],
                    'daily_predictions': [],
                    'model_accuracy': 0,
                    'peak_predicted_hours': {},
                    'total_predicted_messages': 0
                },
                'user_activity_predictions': {},
                'trending_topics': {
                    'trending_topics': [],
                    'topic_evolution': []
                },
                'recommendations': []
            }
    
    def generate_recommendations(self, predictions):
        """Generate actionable recommendations based on predictions"""
        
        recommendations = []
        
        # Best time to message
        if predictions['optimal_messaging_times']['overall_best_times']:
            best_time = predictions['optimal_messaging_times']['overall_best_times'][0]
            recommendations.append({
                'type': 'timing',
                'priority': 'high',
                'recommendation': f"Send important messages on {best_time['day']} at {best_time['time']} for maximum engagement"
            })
        
        # Activity trend
        if predictions['future_activity']['daily_predictions']:
            try:
                avg_predicted = np.mean([d['predicted_messages'] for d in predictions['future_activity']['daily_predictions']])
                current_avg = self.df.groupby('date').size().mean()
                
                if avg_predicted > current_avg * 1.2:
                    recommendations.append({
                        'type': 'activity',
                        'priority': 'medium',
                        'recommendation': f"Chat activity is predicted to increase by {((avg_predicted/current_avg - 1) * 100):.1f}% in the next week"
                    })
                elif avg_predicted < current_avg * 0.8:
                    recommendations.append({
                        'type': 'activity',
                        'priority': 'medium',
                        'recommendation': f"Chat activity is predicted to decrease by {((1 - avg_predicted/current_avg) * 100):.1f}% in the next week"
                    })
            except:
                pass
        
        # Trending topics
        if predictions['trending_topics']['trending_topics']:
            top_topics = predictions['trending_topics']['trending_topics'][:3]
            topics_str = ', '.join([t['topic'] for t in top_topics])
            recommendations.append({
                'type': 'topics',
                'priority': 'low',
                'recommendation': f"Current trending topics: {topics_str}"
            })
        
        return recommendations
