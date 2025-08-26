"""
Database Manager for WhatsApp Analysis
Handles SQLite database operations for storing and retrieving chat analyses
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
import hashlib
import os

class DatabaseManager:
    def __init__(self, db_path='whatsapp_analysis.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for storing chat sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                file_hash TEXT UNIQUE,
                upload_date DATETIME,
                total_messages INTEGER,
                total_participants INTEGER,
                date_range_start DATE,
                date_range_end DATE,
                basic_stats TEXT,
                analysis_results TEXT,
                predictions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create table for storing individual messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp DATETIME,
                sender TEXT,
                message TEXT,
                word_count INTEGER,
                char_count INTEGER,
                emoji_count INTEGER,
                is_media BOOLEAN,
                contains_url BOOLEAN,
                is_question BOOLEAN,
                hour INTEGER,
                day_of_week TEXT,
                time_period TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file for duplicate detection"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return None
    
    def save_analysis(self, session_name, file_path, df, basic_stats, analysis_results, predictions):
        """Save chat analysis to database with proper data type conversion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Calculate file hash for duplicate detection
            file_hash = self.calculate_file_hash(file_path)
            
            # Check if this file has been analyzed before
            cursor.execute('SELECT id, session_name FROM chat_sessions WHERE file_hash = ?', (file_hash,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"File already analyzed as '{existing[1]}'. Updating last accessed time.")
                cursor.execute('UPDATE chat_sessions SET last_accessed = ? WHERE id = ?', 
                              (datetime.now().isoformat(), existing[0]))
                conn.commit()
                conn.close()
                return existing[0]
            
            # Convert data types for SQLite compatibility
            df_json_safe = self.prepare_dataframe_for_storage(df)
            basic_stats_json = self.convert_to_json_safe(basic_stats)
            analysis_results_json = self.convert_to_json_safe(analysis_results)
            predictions_json = self.convert_to_json_safe(predictions)
            
            # Insert session data
            cursor.execute('''
                INSERT INTO chat_sessions 
                (session_name, file_hash, upload_date, total_messages, total_participants,
                 date_range_start, date_range_end, basic_stats, analysis_results, predictions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_name,
                file_hash,
                datetime.now().isoformat(),
                len(df),
                df['sender'].nunique(),
                str(df['date'].min()),
                str(df['date'].max()),
                json.dumps(basic_stats_json),
                json.dumps(analysis_results_json),
                json.dumps(predictions_json)
            ))
            
            session_id = cursor.lastrowid
            
            # Insert messages data in batches for better performance
            messages_data = []
            for _, row in df.iterrows():
                messages_data.append((
                    session_id,
                    row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                    str(row['sender']),
                    str(row['message']),
                    int(row.get('word_count', 0)),
                    int(row.get('char_count', 0)),
                    int(row.get('emoji_count', 0)),
                    bool(row.get('is_media', False)),
                    bool(row.get('contains_url', False)),
                    bool(row.get('is_question', False)),
                    int(row.get('hour', 0)),
                    str(row.get('day_of_week', '')),
                    str(row.get('time_period', ''))
                ))
            
            cursor.executemany('''
                INSERT INTO messages 
                (session_id, timestamp, sender, message, word_count, char_count,
                 emoji_count, is_media, contains_url, is_question, hour, day_of_week, time_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', messages_data)
            
            conn.commit()
            print(f"✅ Automatically saved analysis for session: {session_name}")
            return session_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error saving analysis: {e}")
            import traceback
            traceback.print_exc()
            raise e
        finally:
            conn.close()
    
    def prepare_dataframe_for_storage(self, df):
        """Convert DataFrame to JSON-safe format"""
        df_copy = df.copy()
        
        # Convert datetime columns to strings
        datetime_columns = ['timestamp', 'date', 'time']
        for col in datetime_columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].astype(str)
        
        # Convert numpy types to native Python types
        for col in df_copy.columns:
            if df_copy[col].dtype == 'int64':
                df_copy[col] = df_copy[col].astype(int)
            elif df_copy[col].dtype == 'float64':
                df_copy[col] = df_copy[col].astype(float)
            elif df_copy[col].dtype == 'bool':
                df_copy[col] = df_copy[col].astype(bool)
        
        return df_copy
    
    def convert_to_json_safe(self, obj):
        """Convert complex data types to JSON-safe format"""
        if obj is None:
            return None
            
        if isinstance(obj, dict):
            return {key: self.convert_to_json_safe(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_json_safe(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, 'item'):  # numpy scalar types
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        elif isinstance(obj, (pd.DataFrame, pd.Series)):
            # Store both the data and type information for proper restoration
            return {
                '_type': 'pandas_dataframe' if isinstance(obj, pd.DataFrame) else 'pandas_series',
                '_data': obj.to_dict('records' if isinstance(obj, pd.DataFrame) else 'series')
            }
        elif isinstance(obj, (int, float, str, bool)):
            return obj
        else:
            return str(obj)  # Fallback to string representation
    
    def restore_pandas_objects(self, obj):
        """Restore pandas objects from JSON-safe format"""
        if obj is None:
            return None
            
        if isinstance(obj, dict):
            # Check if this is a stored pandas object
            if '_type' in obj and '_data' in obj:
                if obj['_type'] == 'pandas_dataframe':
                    return pd.DataFrame(obj['_data'])
                elif obj['_type'] == 'pandas_series':
                    return pd.Series(obj['_data'])
            else:
                # Recursively restore nested objects
                return {key: self.restore_pandas_objects(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.restore_pandas_objects(item) for item in obj]
        else:
            return obj
    
    def get_saved_sessions(self):
        """Get list of all saved sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, session_name, upload_date, total_messages, total_participants,
                       date_range_start, date_range_end, last_accessed
                FROM chat_sessions 
                ORDER BY last_accessed DESC
            ''')
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'session_name': row[1],
                    'upload_date': row[2],
                    'total_messages': row[3],
                    'total_participants': row[4],
                    'date_range_start': row[5],
                    'date_range_end': row[6],
                    'last_accessed': row[7]
                })
            
            return sessions
            
        except Exception as e:
            print(f"Error getting saved sessions: {e}")
            return []
        finally:
            conn.close()
    
    def load_analysis(self, session_id):
        """Load analysis from database by session ID with proper type conversion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get session data
            cursor.execute('''
                SELECT session_name, basic_stats, analysis_results, predictions
                FROM chat_sessions WHERE id = ?
            ''', (session_id,))
            
            session_data = cursor.fetchone()
            if not session_data:
                return None, None, None, None
            
            # Get messages data
            cursor.execute('''
                SELECT timestamp, sender, message, word_count, char_count, emoji_count,
                       is_media, contains_url, is_question, hour, day_of_week, time_period
                FROM messages WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            messages_data = cursor.fetchall()
            
            # Convert to DataFrame with proper types
            df = pd.DataFrame(messages_data, columns=[
                'timestamp', 'sender', 'message', 'word_count', 'char_count', 'emoji_count',
                'is_media', 'contains_url', 'is_question', 'hour', 'day_of_week', 'time_period'
            ])
            
            if df.empty:
                return None, None, None, None
            
            # Convert timestamp strings back to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['time'] = df['timestamp'].dt.time
            df['month'] = df['timestamp'].dt.strftime('%B')
            df['year'] = df['timestamp'].dt.year
            df['month_year'] = df['timestamp'].dt.strftime('%B %Y')
            
            # Ensure correct data types
            df['word_count'] = df['word_count'].astype('int64')
            df['char_count'] = df['char_count'].astype('int64')
            df['emoji_count'] = df['emoji_count'].astype('int64')
            df['hour'] = df['hour'].astype('int64')
            df['is_media'] = df['is_media'].astype('bool')
            df['contains_url'] = df['contains_url'].astype('bool')
            df['is_question'] = df['is_question'].astype('bool')
            
            # Add missing columns for compatibility
            df['emojis'] = [[] for _ in range(len(df))]  # Simplified for now
            df['reactions_received'] = [[] for _ in range(len(df))]
            df['reaction_count'] = 0
            
            # Parse JSON data with error handling and restore pandas objects
            try:
                basic_stats = json.loads(session_data[1])
                basic_stats = self.restore_pandas_objects(basic_stats)
            except (json.JSONDecodeError, TypeError):
                basic_stats = {}
                
            try:
                analysis_results_raw = json.loads(session_data[2])
                analysis_results = self.restore_pandas_objects(analysis_results_raw)
            except (json.JSONDecodeError, TypeError):
                analysis_results = {}
                
            try:
                predictions_raw = json.loads(session_data[3])
                predictions = self.restore_pandas_objects(predictions_raw)
            except (json.JSONDecodeError, TypeError):
                predictions = {}
            
            # Update last accessed time
            cursor.execute('UPDATE chat_sessions SET last_accessed = ? WHERE id = ?', 
                          (datetime.now().isoformat(), session_id))
            conn.commit()
            
            print(f"✅ Successfully loaded analysis with {len(df)} messages")
            return df, basic_stats, analysis_results, predictions
            
        except Exception as e:
            print(f"❌ Error loading analysis: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None, None
        finally:
            conn.close()
    
    def delete_session(self, session_id):
        """Delete a session and its associated messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error deleting session: {e}")
            return False
        finally:
            conn.close()
    
    def get_database_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM chat_sessions')
            session_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            message_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(total_messages) FROM chat_sessions')
            total_messages = cursor.fetchone()[0] or 0
            
            # Get database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            db_size_mb = db_size / (1024 * 1024)
            
            return {
                'session_count': session_count,
                'message_count': message_count,
                'total_messages': total_messages,
                'db_size_mb': round(db_size_mb, 2)
            }
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {
                'session_count': 0,
                'message_count': 0,
                'total_messages': 0,
                'db_size_mb': 0
            }
        finally:
            conn.close()
    
    def search_messages(self, session_id, search_term):
        """Search messages within a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT timestamp, sender, message
                FROM messages 
                WHERE session_id = ? AND message LIKE ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (session_id, f'%{search_term}%'))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'timestamp': row[0],
                    'sender': row[1],
                    'message': row[2]
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
        finally:
            conn.close()
