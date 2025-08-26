"""
WhatsApp Chat Parser Module - Enhanced Version
Handles parsing of WhatsApp chat exports from both Android and iOS
Includes support for reactions and various date formats
Fixed for iOS format and Arabic text support
"""

import re
import pandas as pd
from datetime import datetime
import emoji
import numpy as np
from typing import Dict, List, Tuple, Optional

class WhatsAppParser:
    def __init__(self):
        # Enhanced regex patterns for different WhatsApp formats
        self.patterns = {
            # iOS patterns - Fixed to handle colon after sender name
            'ios_12h': r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\]\s([^:]+):\s(.+)',
            'ios_24h': r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)',
            
            # Android patterns - Enhanced for better compatibility
            'android_12h_md': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)',
            'android_12h_dm': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)',
            'android_24h_md': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)',
            'android_24h_dm': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)',
            
            # Alternative patterns for different formats
            'android_alt1': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[apAP][mM])\s-\s([^:]+):\s(.+)',
            'android_alt2': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)',
            
            # European format
            'european': r'(\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)',
            
            # Custom format
            'custom': r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s-\s([^:]+):\s(.+)'
        }
        
        # Reaction pattern (for newer WhatsApp versions)
        self.reaction_pattern = r'(.+)\sreacted\s(.+)\sto\s"(.+)"'
        
    def detect_format(self, content):
        """Detect if the chat export is from Android or iOS"""
        lines = content.split('\n')[:100]  # Check first 100 lines for better detection
        
        format_counts = {fmt: 0 for fmt in self.patterns.keys()}
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 20:  # Skip very short lines
                continue
                
            for fmt, pattern in self.patterns.items():
                try:
                    if re.match(pattern, line):
                        format_counts[fmt] += 1
                except:
                    continue
        
        # Return the format with most matches
        max_format = max(format_counts, key=format_counts.get)
        if format_counts[max_format] > 0:
            print(f"Detected format: {max_format} with {format_counts[max_format]} matches")
            return max_format
        
        print("Format detection results:", format_counts)
        return 'unknown'
    
    def parse_chat(self, file_path):
        """Parse WhatsApp chat export file"""
        try:
            # Try different encodings including UTF-8 for Arabic support
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    print(f"Successfully read file with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    print(f"Failed to read with encoding: {encoding}")
                    continue
            
            if content is None:
                raise ValueError("Unable to read file with any encoding")
            
            chat_format = self.detect_format(content)
            
            if chat_format == 'unknown':
                # Try to provide more helpful error message
                sample_lines = content.split('\n')[:5]
                raise ValueError(f"Unable to detect chat format. Sample lines: {sample_lines}")
            
            # Select appropriate pattern
            pattern = self.patterns[chat_format]
            
            messages = []
            reactions = []
            lines = content.split('\n')
            current_message = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Check for reactions first
                reaction_match = re.search(self.reaction_pattern, line)
                if reaction_match:
                    reactions.append({
                        'reactor': reaction_match.group(1),
                        'reaction': reaction_match.group(2),
                        'original_message': reaction_match.group(3)[:50]
                    })
                    continue
                
                match = re.match(pattern, line)
                if match:
                    # Save previous message if exists
                    if current_message:
                        messages.append(current_message)
                    
                    timestamp_str = match.group(1)
                    sender = match.group(2).strip()
                    message = match.group(3).strip()
                    
                    # Skip system messages early
                    if self.is_system_message(sender, message):
                        current_message = None
                        continue
                    
                    try:
                        # Parse timestamp
                        timestamp = self.parse_timestamp(timestamp_str, chat_format)
                        
                        current_message = {
                            'timestamp': timestamp,
                            'sender': self.clean_sender_name(sender),
                            'message': message,
                            'date': timestamp.date(),
                            'time': timestamp.time(),
                            'hour': timestamp.hour,
                            'day_of_week': timestamp.strftime('%A'),
                            'month': timestamp.strftime('%B'),
                            'year': timestamp.year,
                            'month_year': timestamp.strftime('%B %Y')
                        }
                    except Exception as e:
                        print(f"Error parsing timestamp '{timestamp_str}' on line {i}: {e}")
                        current_message = None
                        continue
                        
                elif current_message and line.strip():
                    # Continuation of previous message
                    current_message['message'] += ' ' + line.strip()
            
            # Add last message
            if current_message:
                messages.append(current_message)
            
            if not messages:
                raise ValueError("No valid messages found in the chat file")
            
            df = pd.DataFrame(messages)
            
            # Sort by timestamp to ensure proper order
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Add additional features
            if not df.empty:
                df = self.add_features(df)
                
                # Add reactions data
                if reactions:
                    df = self.add_reactions(df, reactions)
            
            print(f"Successfully parsed {len(df)} messages")
            return df
            
        except Exception as e:
            print(f"Detailed error: {str(e)}")
            raise Exception(f"Error parsing chat: {str(e)}")
    
    def clean_sender_name(self, sender):
        """Clean sender name - remove phone number prefixes and special characters"""
        # Remove invisible characters and special Unicode characters
        sender = re.sub(r'[\u200c\u200d\u200e\u200f\ufeff]', '', sender)
        
        # Remove country codes and clean phone numbers
        sender = re.sub(r'^\+\d+\s*\d*\s*\d*\s*\d*', '', sender)
        
        # Clean up extra spaces and special characters
        sender = re.sub(r'\s+', ' ', sender)
        sender = sender.strip()
        
        # If sender is still a number or very short, keep as is
        if len(sender) < 2:
            return sender
            
        return sender
    
    def add_features(self, df):
        """Add additional features to the dataframe"""
        # Extract emojis
        df['emojis'] = df['message'].apply(self.extract_emojis)
        df['emoji_count'] = df['emojis'].apply(len)
        
        # Word count
        df['word_count'] = df['message'].apply(lambda x: len(str(x).split()))
        
        # Character count
        df['char_count'] = df['message'].apply(len)
        
        # Media messages
        df['is_media'] = df['message'].apply(lambda x: '<Media omitted>' in str(x) or 'media omitted' in str(x).lower())
        
        # URLs
        df['contains_url'] = df['message'].apply(lambda x: bool(re.search(r'http[s]?://\S+|www\.\S+', str(x))))
        
        # Questions
        df['is_question'] = df['message'].apply(lambda x: '?' in str(x))
        
        # Time period
        df['time_period'] = df['hour'].apply(self.get_time_period)
        
        # Initialize reaction columns
        df['reactions_received'] = [[] for _ in range(len(df))]
        df['reaction_count'] = 0
        
        return df
    
    def add_reactions(self, df, reactions):
        """Add reaction data to messages"""
        for reaction in reactions:
            # Find the message that matches
            mask = df['message'].str[:50] == reaction['original_message']
            if mask.any():
                idx = df[mask].index[0]
                df.at[idx, 'reactions_received'].append({
                    'reactor': reaction['reactor'],
                    'reaction': reaction['reaction']
                })
                df.at[idx, 'reaction_count'] += 1
        
        return df
    
    def get_time_period(self, hour):
        """Categorize hour into time periods"""
        if 0 <= hour < 6:
            return 'Late Night'
        elif 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    
    def parse_timestamp(self, timestamp_str, chat_format):
        """Parse timestamp based on format - Enhanced with better error handling"""
        timestamp_str = timestamp_str.strip()
        
        # Remove brackets for iOS format
        if timestamp_str.startswith('[') and timestamp_str.endswith(']'):
            timestamp_str = timestamp_str[1:-1]
        
        # Define format strings for each chat format
        format_strings = {
            'ios_12h': [
                '%d/%m/%Y, %I:%M:%S %p',
                '%m/%d/%Y, %I:%M:%S %p',
                '%d/%m/%y, %I:%M:%S %p',
                '%m/%d/%y, %I:%M:%S %p'
            ],
            'ios_24h': [
                '%d/%m/%Y, %H:%M:%S',
                '%m/%d/%Y, %H:%M:%S',
                '%d/%m/%y, %H:%M:%S',
                '%m/%d/%y, %H:%M:%S'
            ],
            'android_12h_md': [
                '%m/%d/%Y, %I:%M %p',
                '%m/%d/%y, %I:%M %p'
            ],
            'android_12h_dm': [
                '%d/%m/%Y, %I:%M %p',
                '%d/%m/%y, %I:%M %p'
            ],
            'android_24h_md': [
                '%m/%d/%Y, %H:%M',
                '%m/%d/%y, %H:%M'
            ],
            'android_24h_dm': [
                '%d/%m/%Y, %H:%M',
                '%d/%m/%y, %H:%M'
            ],
            'android_alt1': [
                '%m/%d/%Y, %I:%M %p',
                '%d/%m/%Y, %I:%M %p',
                '%m/%d/%y, %I:%M %p',
                '%d/%m/%y, %I:%M %p'
            ],
            'android_alt2': [
                '%m/%d/%Y, %I:%M:%S %p',
                '%d/%m/%Y, %I:%M:%S %p',
                '%m/%d/%y, %I:%M:%S %p',
                '%d/%m/%y, %I:%M:%S %p'
            ],
            'european': [
                '%d.%m.%Y, %H:%M',
                '%d.%m.%y, %H:%M'
            ],
            'custom': ['%Y-%m-%d %H:%M:%S']
        }
        
        # Get format strings for detected format
        formats = format_strings.get(chat_format, [])
        
        # Also try generic formats
        all_formats = formats + [
            '%m/%d/%Y, %I:%M %p',
            '%d/%m/%Y, %I:%M %p',
            '%m/%d/%y, %I:%M %p',
            '%d/%m/%y, %I:%M %p',
            '%Y-%m-%d %H:%M:%S',
            '%d.%m.%Y, %H:%M',
            '%d.%m.%y, %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%m/%d/%Y, %H:%M',
            '%d/%m/%Y, %H:%M',
            '%m/%d/%y, %H:%M',
            '%d/%m/%y, %H:%M'
        ]
        
        for fmt in all_formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")
    
    def is_system_message(self, sender, message):
        """Check if message is a system message"""
        system_indicators = [
            'Messages and calls are end-to-end encrypted',
            'changed the subject',
            'changed the group description', 
            'added',
            'left',
            'removed',
            'created group',
            'created this group',
            'changed this group\'s icon',
            'deleted this message',
            'This message was deleted',
            'Your security code with',
            'joined using this group\'s invite link',
            'Missed voice call',
            'Missed video call',
            'changed their phone number',
            'disappearing messages',
            'created poll',
            'voted',
            'You joined using',
            'You were added',
            'You left',
            'You removed',
            'Only people in this chat can read'
        ]
        
        message_lower = str(message).lower()
        sender_lower = str(sender).lower()
        
        # Check if the entire message is a system message
        for indicator in system_indicators:
            if indicator.lower() in message_lower:
                return True
        
        # Check for specific system message patterns
        if sender_lower == 'system' or 'whatsapp' in sender_lower:
            return True
            
        # Check for messages that start with special characters indicating system messages
        if message.startswith('‎'):  # Invisible character often used in system messages
            return True
            
        return False
    
    def extract_emojis(self, text):
        """Extract emojis from text"""
        return [c for c in str(text) if c in emoji.EMOJI_DATA]
    
    def clean_message(self, text):
        """Clean message text"""
        # Remove <Media omitted>
        text = re.sub(r'<Media omitted>', '', str(text))
        text = re.sub(r'media omitted', '', str(text), flags=re.IGNORECASE)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
