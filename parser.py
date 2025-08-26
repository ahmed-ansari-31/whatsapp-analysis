"""
High-Performance WhatsApp Chat Parser Module - Optimized Version
Handles parsing of WhatsApp chat exports with significant performance improvements
"""

import re
import pandas as pd
from datetime import datetime
import emoji
import numpy as np
from typing import Dict, List, Tuple, Optional
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
from functools import lru_cache

class HighPerformanceWhatsAppParser:
    def __init__(self):
        # Pre-compiled regex patterns for better performance
        self.compiled_patterns = {
            'ios_12h': re.compile(r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\]\s([^:]+):\s(.+)'),
            'ios_24h': re.compile(r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)'),
            'android_12h': re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)'),
            'android_24h': re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)'),
            'android_alt': re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)'),
            'european': re.compile(r'(\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)')
        }
        
        # Pre-compiled system message patterns
        self.system_patterns = re.compile(r'(?:Messages and calls are end-to-end encrypted|'
                                        r'changed the subject|changed the group description|'
                                        r'added|left|removed|created group|created this group|'
                                        r'joined using.*invite link|You joined using|'
                                        r'Missed voice call|Missed video call|This message was deleted|'
                                        r'security code|disappearing messages)', re.IGNORECASE)
        
        # Pre-compiled emoji pattern for faster emoji extraction
        self.emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]')
        
        # URL pattern
        self.url_pattern = re.compile(r'http[s]?://\S+|www\.\S+')
        
        # Media pattern
        self.media_pattern = re.compile(r'<Media omitted>|media omitted', re.IGNORECASE)
        
        # Format cache for timestamp parsing
        self.format_cache = {}
        
        # Performance tracking
        self.timing = {}
    
    def time_and_log(self, operation_name, start_time):
        """Helper method to time operations"""
        elapsed = time.time() - start_time
        self.timing[operation_name] = elapsed
        print(f"⏱️  {operation_name}: {elapsed:.2f}s")
        return elapsed
    
    def read_file_optimized(self, file_path):
        """Optimized file reading with encoding detection"""
        start_time = time.time()
        
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, buffering=8192) as file:
                    content = file.read()
                
                self.time_and_log("File Reading", start_time)
                return content, encoding
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Unable to read file with any encoding")
    
    def detect_format_fast(self, content):
        """Fast format detection using sample of lines"""
        start_time = time.time()
        
        # Use only first 200 lines for detection (much faster)
        sample_lines = content.split('\n')[:200]
        
        format_scores = {fmt: 0 for fmt in self.compiled_patterns.keys()}
        
        for line in sample_lines:
            if len(line) < 20:  # Skip very short lines
                continue
                
            for fmt, pattern in self.compiled_patterns.items():
                if pattern.match(line):
                    format_scores[fmt] += 1
                    if format_scores[fmt] >= 5:  # Early exit when we find enough matches
                        self.time_and_log("Format Detection", start_time)
                        return fmt
        
        best_format = max(format_scores, key=format_scores.get)
        if format_scores[best_format] > 0:
            self.time_and_log("Format Detection", start_time)
            return best_format
        
        self.time_and_log("Format Detection", start_time)
        return 'unknown'
    
    @lru_cache(maxsize=1000)
    def parse_timestamp_cached(self, timestamp_str, chat_format):
        """Cached timestamp parsing for repeated patterns"""
        return self._parse_timestamp_internal(timestamp_str, chat_format)
    
    def _parse_timestamp_internal(self, timestamp_str, chat_format):
        """Internal timestamp parsing with optimized format selection"""
        timestamp_str = timestamp_str.strip()
        
        # Remove brackets for iOS
        if timestamp_str.startswith('[') and timestamp_str.endswith(']'):
            timestamp_str = timestamp_str[1:-1]
        
        # Use cached format if available
        if chat_format in self.format_cache:
            try:
                return datetime.strptime(timestamp_str, self.format_cache[chat_format])
            except ValueError:
                pass
        
        # Format strings optimized based on detected format
        format_groups = {
            'ios_12h': ['%d/%m/%Y, %I:%M:%S %p', '%m/%d/%Y, %I:%M:%S %p'],
            'ios_24h': ['%d/%m/%Y, %H:%M:%S', '%m/%d/%Y, %H:%M:%S'],
            'android_12h': ['%m/%d/%y, %I:%M %p', '%d/%m/%y, %I:%M %p', '%m/%d/%Y, %I:%M %p', '%d/%m/%Y, %I:%M %p'],
            'android_24h': ['%m/%d/%y, %H:%M', '%d/%m/%y, %H:%M', '%m/%d/%Y, %H:%M', '%d/%m/%Y, %H:%M'],
            'android_alt': ['%m/%d/%Y, %I:%M:%S %p', '%d/%m/%Y, %I:%M:%S %p', '%m/%d/%y, %I:%M:%S %p', '%d/%m/%y, %I:%M:%S %p'],
            'european': ['%d.%m.%Y, %H:%M', '%d.%m.%y, %H:%M']
        }
        
        formats = format_groups.get(chat_format, [
            '%m/%d/%Y, %I:%M %p', '%d/%m/%Y, %I:%M %p',
            '%m/%d/%Y, %H:%M', '%d/%m/%Y, %H:%M'
        ])
        
        for fmt in formats:
            try:
                result = datetime.strptime(timestamp_str, fmt)
                # Cache successful format
                self.format_cache[chat_format] = fmt
                return result
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")
    
    def parse_messages_batch(self, content, chat_format):
        """Batch message parsing with optimizations"""
        start_time = time.time()
        
        pattern = self.compiled_patterns[chat_format]
        lines = content.split('\n')
        
        messages = []
        current_message = None
        processed = 0
        
        # Process in batches for better memory usage
        batch_size = 1000
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            match = pattern.match(line)
            if match:
                # Save previous message
                if current_message:
                    messages.append(current_message)
                
                timestamp_str, sender, message = match.groups()
                sender = sender.strip()
                message = message.strip()
                
                # Quick system message check
                if self.is_system_message_fast(sender, message):
                    current_message = None
                    continue
                
                try:
                    timestamp = self.parse_timestamp_cached(timestamp_str, chat_format)
                    
                    current_message = {
                        'timestamp': timestamp,
                        'sender': self.clean_sender_name_fast(sender),
                        'message': message,
                        'raw_line': i  # Store line number for debugging
                    }
                except Exception:
                    current_message = None
                    continue
                    
            elif current_message and line:
                # Multi-line message continuation
                current_message['message'] += ' ' + line
            
            processed += 1
            if processed % batch_size == 0:
                print(f"📊 Processed {processed} lines...")
        
        # Add last message
        if current_message:
            messages.append(current_message)
        
        self.time_and_log("Message Parsing", start_time)
        return messages
    
    def is_system_message_fast(self, sender, message):
        """Fast system message detection - Fixed to be less aggressive"""
        # Only check for clear system message patterns in the message content
        if self.system_patterns.search(message) is not None:
            return True
            
        # Check for invisible character at start (common in system messages)
        if message.startswith('\u202e'):  # Right-to-left override
            return True
            
        # Very specific sender patterns that indicate system messages
        if sender.lower() in ['system', 'whatsapp', '']:
            return True
            
        # Don't filter normal user messages
        return False
    
    # def clean_sender_name_fast(self, sender):
    #     """Fast sender name cleaning"""
    #     # Remove country codes and phone numbers
    #     sender = re.sub(r'^\+\d+\s*\d*\s*\d*\s*', '', sender)
    #     # Remove invisible characters
    #     sender = re.sub(r'[\u200c\u200d\u200e\u200f\ufeff~]', '', sender)
    #     return sender.strip()
    def clean_sender_name_fast(self, sender: str) -> str:
        """Clean sender names or phone numbers (mask middle digits, keep last 4)."""
        # Remove invisible/unwanted characters
        sender = re.sub(r'[\u200c\u200d\u200e\u200f\ufeff~]', '', sender).strip()

        # Detect phone number
        if re.match(r'^\+\d+', sender):
            digits = re.sub(r'\D', '', sender)  # keep only digits
            if len(digits) > 7:
                country = digits[:len(digits)-10] if len(digits) > 10 else digits[:2]
                last4 = digits[-4:]
                return f"+{country}*****{last4}"
        return sender
    
    def add_features_batch(self, df):
        """Batch feature extraction using vectorized operations"""
        start_time = time.time()
        print("🔧 Extracting basic features...")
        
        # Vectorized operations for better performance
        df['word_count'] = df['message'].str.split().str.len()
        df['char_count'] = df['message'].str.len()
        
        # Fast media detection
        df['is_media'] = df['message'].str.contains(self.media_pattern, regex=True, na=False)
        
        # Fast URL detection  
        df['contains_url'] = df['message'].str.contains(self.url_pattern, regex=True, na=False)
        
        # Fast question detection
        df['is_question'] = df['message'].str.contains(r'\?', regex=True, na=False)
        
        # Extract date/time features
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.time
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['month'] = df['timestamp'].dt.strftime('%B')
        df['year'] = df['timestamp'].dt.year
        df['month_year'] = df['timestamp'].dt.strftime('%B %Y')
        
        # Time period categorization
        df['time_period'] = pd.cut(df['hour'], 
                                  bins=[-1, 6, 12, 17, 21, 24],
                                  labels=['Late Night', 'Morning', 'Afternoon', 'Evening', 'Night'])
        
        self.time_and_log("Feature Extraction", start_time)
        return df
    
    def add_emoji_features_parallel(self, df):
        """Parallel emoji extraction for large datasets"""
        start_time = time.time()
        print("😊 Extracting emojis...")
        
        def extract_emojis_batch(messages):
            return [self.emoji_pattern.findall(str(msg)) for msg in messages]
        
        # Use parallel processing for emoji extraction if dataset is large
        if len(df) > 5000:
            chunk_size = max(1, len(df) // mp.cpu_count())
            chunks = [df['message'].iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
            
            with ThreadPoolExecutor(max_workers=min(mp.cpu_count(), 4)) as executor:
                emoji_results = list(executor.map(extract_emojis_batch, chunks))
            
            # Flatten results
            all_emojis = []
            for chunk_result in emoji_results:
                all_emojis.extend(chunk_result)
        else:
            all_emojis = extract_emojis_batch(df['message'])
        
        df['emojis'] = all_emojis
        df['emoji_count'] = [len(emojis) for emojis in all_emojis]
        
        # Initialize reaction columns
        df['reactions_received'] = [[] for _ in range(len(df))]
        df['reaction_count'] = 0
        
        self.time_and_log("Emoji Extraction", start_time)
        return df
    
    def parse_chat(self, file_path):
        """High-performance chat parsing with comprehensive optimizations"""
        total_start_time = time.time()
        
        try:
            print("🚀 Starting high-performance parsing...")
            
            # Read file
            content, encoding = self.read_file_optimized(file_path)
            print(f"📄 File size: {len(content):,} characters, encoding: {encoding}")
            
            # Detect format
            chat_format = self.detect_format_fast(content)
            if chat_format == 'unknown':
                raise ValueError("Unable to detect chat format")
            
            print(f"🔍 Detected format: {chat_format}")
            
            # Parse messages in batches
            messages = self.parse_messages_batch(content, chat_format)
            
            if not messages:
                raise ValueError("No valid messages found")
            
            print(f"💬 Parsed {len(messages)} messages")
            
            # Create DataFrame
            df_start = time.time()
            df = pd.DataFrame(messages)
            # Sort by timestamp for consistency
            df = df.sort_values('timestamp').reset_index(drop=True)
            self.time_and_log("DataFrame Creation", df_start)
            
            # Add features in batches
            df = self.add_features_batch(df)
            
            # Add emoji features (can be slow for large datasets)
            if len(df) < 50000:  # Only do emoji extraction for reasonable sizes
                df = self.add_emoji_features_parallel(df)
            else:
                print("⚠️  Skipping emoji extraction for very large dataset (>50k messages)")
                df['emojis'] = [[] for _ in range(len(df))]
                df['emoji_count'] = 0
                df['reactions_received'] = [[] for _ in range(len(df))]
                df['reaction_count'] = 0
            
            # Clean up temporary columns
            if 'raw_line' in df.columns:
                df = df.drop('raw_line', axis=1)
            
            # Performance summary
            total_time = time.time() - total_start_time
            self.timing['Total Parsing Time'] = total_time
            
            print(f"\n🎉 Parsing completed!")
            print(f"📊 Total time: {total_time:.2f}s")
            print(f"📈 Messages/second: {len(df)/total_time:.1f}")
            print(f"💾 Memory usage: ~{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
            
            return df
            
        except Exception as e:
            print(f"❌ Error during parsing: {str(e)}")
            raise Exception(f"Error parsing chat: {str(e)}")
    
    def get_performance_stats(self):
        """Get detailed performance statistics"""
        return {
            'timing': self.timing,
            'total_time': sum(self.timing.values()),
            'cache_hits': len(self.format_cache)
        }

# Backward compatibility wrapper
class WhatsAppParser(HighPerformanceWhatsAppParser):
    """Backward compatible wrapper for existing code"""
    pass
