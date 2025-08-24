"""
WhatsApp Chat Parser Module - Enhanced Version
Handles parsing of WhatsApp chat exports from both Android and iOS
Includes support for reactions and various date formats
"""

import re
import pandas as pd
from datetime import datetime
import emoji
import numpy as np
from typing import Dict, List, Tuple, Optional

class WhatsAppParser:
    def __init__(self):
        # Regex patterns for different WhatsApp formats
        self.patterns = {
            'android_12h_md': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)',
            'android_12h_dm': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm])\s-\s([^:]+):\s(.+)',
            'android_24h': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)',
            'ios': r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm])\]\s([^:]+):\s(.+)',
            'android_new': r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[apAP][mM])\s-\s([^:]+):\s(.+)',
            'custom': r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s-\s([^:]+):\s(.+)'
        }
        
        # Reaction pattern (for newer WhatsApp versions)
        self.reaction_pattern = r'(.+)\sreacted\s(.+)\sto\s"(.+)"'
        
    def detect_format(self, content):
        """Detect if the chat export is from Android or iOS"""
        lines = content.split('\n')[:50]  # Check first 50 lines
        
        format_counts = {fmt: 0 for fmt in self.patterns.keys()}
        
        for line in lines:
            for fmt, pattern in self.patterns.items():
                if re.match(pattern, line):
                    format_counts[fmt] += 1
        
        # Return the format with most matches
        max_format = max(format_counts, key=format_counts.get)
        if format_counts[max_format] > 0:
            return max_format
        
        return 'unknown'
    
    def parse_chat(self, file_path):
        """Parse WhatsApp chat export file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise ValueError("Unable to read file with any encoding")
            
            chat_format = self.detect_format(content)
            
            if chat_format == 'unknown':
                raise ValueError("Unable to detect chat format. Please ensure the file is a valid WhatsApp export.")
            
            # Select appropriate pattern
            pattern = self.patterns[chat_format]
            
            messages = []
            reactions = []
            lines = content.split('\n')
            current_message = None
            
            for line in lines:
                # Check for reactions first
                reaction_match = re.search(self.reaction_pattern, line)
                if reaction_match:
                    reactions.append({
                        'reactor': reaction_match.group(1),
                        'reaction': reaction_match.group(2),
                        'original_message': reaction_match.group(3)[:50]  # First 50 chars for matching
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
                    
                    # Parse timestamp
                    timestamp = self.parse_timestamp(timestamp_str, chat_format)
                    
                    # Skip system messages
                    if not self.is_system_message(sender, message):
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
                elif current_message and line.strip():
                    # Continuation of previous message
                    current_message['message'] += ' ' + line.strip()
            
            # Add last message
            if current_message:
                messages.append(current_message)
            
            df = pd.DataFrame(messages)
            
            # Add additional features
            if not df.empty:
                df = self.add_features(df)
                
                # Add reactions data
                if reactions:
                    df = self.add_reactions(df, reactions)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error parsing chat: {str(e)}")
    
    def clean_sender_name(self, sender):
        """Clean sender name - remove phone number prefixes"""
        # Remove country codes and clean phone numbers
        sender = re.sub(r'^\+\d+\s*', '', sender)
        sender = re.sub(r'^\d+\s*', '', sender)
        return sender.strip()
    
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
        df['is_media'] = df['message'].apply(lambda x: '<Media omitted>' in x)
        
        # URLs
        df['contains_url'] = df['message'].apply(lambda x: bool(re.search(r'http[s]?://\S+', x)))
        
        # Questions
        df['is_question'] = df['message'].apply(lambda x: '?' in x)
        
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
        """Parse timestamp based on format"""
        timestamp_str = timestamp_str.strip()
        
        # Define format strings for each chat format
        format_strings = {
            'android_12h_md': [
                '%m/%d/%y, %I:%M %p',
                '%m/%d/%Y, %I:%M %p',
                '%-m/%-d/%y, %I:%M %p',  # Without leading zeros
                '%-m/%-d/%Y, %I:%M %p'
            ],
            'android_12h_dm': [
                '%d/%m/%y, %I:%M %p',
                '%d/%m/%Y, %I:%M %p',
                '%-d/%-m/%y, %I:%M %p',
                '%-d/%-m/%Y, %I:%M %p'
            ],
            'android_24h': [
                '%m/%d/%y, %H:%M',
                '%d/%m/%y, %H:%M',
                '%m/%d/%Y, %H:%M',
                '%d/%m/%Y, %H:%M',
                '%-m/%-d/%y, %H:%M',
                '%-d/%-m/%y, %H:%M'
            ],
            'ios': [
                '[%m/%d/%y, %I:%M:%S %p]',
                '[%d/%m/%y, %I:%M:%S %p]',
                '[%m/%d/%Y, %I:%M:%S %p]',
                '[%d/%m/%Y, %I:%M:%S %p]'
            ],
            'android_new': [
                '%m/%d/%y, %I:%M %p',
                '%d/%m/%y, %I:%M %p',
                '%m/%d/%Y, %I:%M %p',
                '%d/%m/%Y, %I:%M %p',
                '%-m/%-d/%y, %-I:%M %p',  # Without leading zeros
                '%-d/%-m/%y, %-I:%M %p'
            ],
            'custom': ['%Y-%m-%d %H:%M:%S']
        }
        
        # Get format strings for detected format
        formats = format_strings.get(chat_format, [])
        
        # Also try generic formats
        all_formats = formats + [
            '%m/%d/%y, %I:%M %p',
            '%d/%m/%y, %I:%M %p',
            '%-m/%-d/%y, %-I:%M %p',
            '%Y-%m-%d %H:%M:%S',
            '%d.%m.%Y, %H:%M',
            '%d.%m.%y, %H:%M',
            '%Y/%m/%d %H:%M:%S'
        ]
        
        for fmt in all_formats:
            try:
                # Handle platform differences (%-d vs %d)
                fmt_modified = fmt.replace('%-', '%')
                return datetime.strptime(timestamp_str, fmt_modified)
            except ValueError:
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
            'voted'
        ]
        
        message_lower = message.lower()
        sender_lower = sender.lower()
        
        for indicator in system_indicators:
            if indicator.lower() in message_lower or indicator.lower() in sender_lower:
                return True
        
        return False
    
    def extract_emojis(self, text):
        """Extract emojis from text"""
        return [c for c in str(text) if c in emoji.EMOJI_DATA]
    
    def clean_message(self, text):
        """Clean message text"""
        # Remove <Media omitted>
        text = re.sub(r'<Media omitted>', '', str(text))
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
