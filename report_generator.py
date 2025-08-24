"""
Report Generator Module
Generates comprehensive reports in various formats (HTML, PDF, etc.)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import base64
from io import BytesIO
import json
from typing import Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class ReportGenerator:
    def __init__(self, df: pd.DataFrame, analyzer, predictor):
        self.df = df
        self.analyzer = analyzer
        self.predictor = predictor
        self.timestamp = datetime.now()
        
    def generate_html_report(self, include_charts: bool = True) -> str:
        """Generate comprehensive HTML report"""
        
        # Get all analysis results
        basic_stats = self.analyzer.get_basic_stats()
        user_stats = self.analyzer.get_user_stats()
        temporal = self.analyzer.get_temporal_analysis()
        emoji_analysis = self.analyzer.get_emoji_analysis()
        sentiment = self.analyzer.get_sentiment_analysis()
        reaction_analysis = self.analyzer.get_reaction_analysis()
        predictions = self.predictor.get_prediction_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WhatsApp Chat Analysis Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 3rem;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                }}
                
                .header p {{
                    font-size: 1.2rem;
                    opacity: 0.95;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                .section {{
                    margin-bottom: 50px;
                }}
                
                .section-title {{
                    font-size: 2rem;
                    color: #128C7E;
                    margin-bottom: 25px;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #25D366;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .metric-card {{
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }}
                
                .metric-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                }}
                
                .metric-value {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: #128C7E;
                    margin-bottom: 5px;
                }}
                
                .metric-label {{
                    font-size: 1rem;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .table-responsive {{
                    overflow-x: auto;
                    margin: 20px 0;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-radius: 10px;
                    overflow: hidden;
                }}
                
                th {{
                    background: #25D366;
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #f0f0f0;
                }}
                
                tr:hover {{
                    background: #f8f9fa;
                }}
                
                tr:last-child td {{
                    border-bottom: none;
                }}
                
                .chart-container {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 15px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                
                .emoji-display {{
                    font-size: 2rem;
                    margin-right: 10px;
                }}
                
                .recommendation {{
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 10px;
                    border-left: 5px solid;
                }}
                
                .recommendation.high {{
                    background: #ffebee;
                    border-color: #f44336;
                    color: #c62828;
                }}
                
                .recommendation.medium {{
                    background: #fff3e0;
                    border-color: #ff9800;
                    color: #e65100;
                }}
                
                .recommendation.low {{
                    background: #e3f2fd;
                    border-color: #2196f3;
                    color: #0d47a1;
                }}
                
                .user-card {{
                    background: white;
                    border: 2px solid #25D366;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 15px 0;
                    transition: all 0.3s ease;
                }}
                
                .user-card:hover {{
                    box-shadow: 0 5px 20px rgba(37, 211, 102, 0.3);
                    transform: translateY(-2px);
                }}
                
                .user-name {{
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #128C7E;
                    margin-bottom: 15px;
                }}
                
                .user-stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                }}
                
                .user-stat {{
                    text-align: center;
                }}
                
                .user-stat-value {{
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #25D366;
                }}
                
                .user-stat-label {{
                    font-size: 0.9rem;
                    color: #666;
                    margin-top: 5px;
                }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    color: #666;
                    border-top: 2px solid #e0e0e0;
                }}
                
                .footer p {{
                    margin: 5px 0;
                }}
                
                @media (max-width: 768px) {{
                    .header h1 {{
                        font-size: 2rem;
                    }}
                    
                    .metrics-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .content {{
                        padding: 20px;
                    }}
                }}
                
                @media print {{
                    body {{
                        background: white;
                    }}
                    
                    .container {{
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💬 WhatsApp Chat Analysis Report</h1>
                    <p>Generated on {self.timestamp.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p>{basic_stats['date_range']}</p>
                </div>
                
                <div class="content">
                    <!-- Overview Section -->
                    <div class="section">
                        <h2 class="section-title">📊 Overview</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['total_messages']:,}</div>
                                <div class="metric-label">Total Messages</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['total_participants']}</div>
                                <div class="metric-label">Participants</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['total_days']}</div>
                                <div class="metric-label">Total Days</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['avg_messages_per_day']:.1f}</div>
                                <div class="metric-label">Avg Messages/Day</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['total_words']:,}</div>
                                <div class="metric-label">Total Words</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['total_emojis']:,}</div>
                                <div class="metric-label">Total Emojis</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats['total_media']:,}</div>
                                <div class="metric-label">Media Shared</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{basic_stats.get('total_reactions', 0):,}</div>
                                <div class="metric-label">Total Reactions</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- User Statistics Section -->
                    <div class="section">
                        <h2 class="section-title">👥 User Statistics</h2>
                        {self._generate_user_cards_html(user_stats)}
                    </div>
                    
                    <!-- Activity Patterns Section -->
                    <div class="section">
                        <h2 class="section-title">⏰ Activity Patterns</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">{temporal['peak_hour']:02d}:00</div>
                                <div class="metric-label">Peak Hour</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{temporal['peak_day']}</div>
                                <div class="metric-label">Most Active Day</div>
                            </div>
                        </div>
                        {self._generate_activity_chart_html() if include_charts else ''}
                    </div>
                    
                    <!-- Emoji Analysis Section -->
                    <div class="section">
                        <h2 class="section-title">😊 Emoji Analysis</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">{emoji_analysis['total_emojis']:,}</div>
                                <div class="metric-label">Total Emojis Used</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{emoji_analysis['unique_emojis']}</div>
                                <div class="metric-label">Unique Emojis</div>
                            </div>
                        </div>
                        {self._generate_top_emojis_html(emoji_analysis['top_emojis'][:10])}
                    </div>
                    
                    <!-- Reaction Analysis Section -->
                    {self._generate_reaction_section_html(reaction_analysis) if reaction_analysis['total_reactions'] > 0 else ''}
                    
                    <!-- Sentiment Analysis Section -->
                    <div class="section">
                        <h2 class="section-title">💭 Sentiment Analysis</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">{sentiment['overall_sentiment']:.3f}</div>
                                <div class="metric-label">Overall Sentiment</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{sentiment['positive_ratio']*100:.1f}%</div>
                                <div class="metric-label">Positive Messages</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{sentiment['neutral_ratio']*100:.1f}%</div>
                                <div class="metric-label">Neutral Messages</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{sentiment['negative_ratio']*100:.1f}%</div>
                                <div class="metric-label">Negative Messages</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Predictions Section -->
                    <div class="section">
                        <h2 class="section-title">🔮 Predictions & Recommendations</h2>
                        {self._generate_recommendations_html(predictions['recommendations'])}
                        {self._generate_optimal_times_html(predictions['optimal_messaging_times'])}
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>WhatsApp Chat Analyzer v2.0</strong></p>
                    <p>Report generated on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Analysis based on {basic_stats['total_messages']:,} messages from {basic_stats['total_participants']} participants</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_user_cards_html(self, user_stats: pd.DataFrame) -> str:
        """Generate HTML for user cards"""
        html = '<div class="user-cards">'
        
        for _, user in user_stats.iterrows():
            html += f"""
            <div class="user-card">
                <div class="user-name">{user['user']}</div>
                <div class="user-stats">
                    <div class="user-stat">
                        <div class="user-stat-value">{user['message_count']:,}</div>
                        <div class="user-stat-label">Messages</div>
                    </div>
                    <div class="user-stat">
                        <div class="user-stat-value">{user['word_count']:,}</div>
                        <div class="user-stat-label">Words</div>
                    </div>
                    <div class="user-stat">
                        <div class="user-stat-value">{user['emoji_count']:,}</div>
                        <div class="user-stat-label">Emojis</div>
                    </div>
                    <div class="user-stat">
                        <div class="user-stat-value">{user['media_count']:,}</div>
                        <div class="user-stat-label">Media</div>
                    </div>
                    <div class="user-stat">
                        <div class="user-stat-value">{user.get('reactions_received', 0):,}</div>
                        <div class="user-stat-label">Reactions</div>
                    </div>
                    <div class="user-stat">
                        <div class="user-stat-value">{user['message_percentage']:.1f}%</div>
                        <div class="user-stat-label">of Total</div>
                    </div>
                </div>
            </div>
            """
        
        html += '</div>'
        return html
    
    def _generate_activity_chart_html(self) -> str:
        """Generate activity chart HTML"""
        return """
        <div class="chart-container">
            <div id="activityChart"></div>
        </div>
        <script>
            // Activity chart would be generated here using Plotly
        </script>
        """
    
    def _generate_top_emojis_html(self, top_emojis: list) -> str:
        """Generate HTML for top emojis"""
        html = '<div class="table-responsive"><table><thead><tr><th>Emoji</th><th>Count</th></tr></thead><tbody>'
        
        for emoji, count in top_emojis:
            html += f"""
            <tr>
                <td><span class="emoji-display">{emoji}</span></td>
                <td>{count:,}</td>
            </tr>
            """
        
        html += '</tbody></table></div>'
        return html
    
    def _generate_reaction_section_html(self, reaction_analysis: dict) -> str:
        """Generate reaction analysis section HTML"""
        return f"""
        <div class="section">
            <h2 class="section-title">👍 Reaction Analysis</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{reaction_analysis['total_reactions']:,}</div>
                    <div class="metric-label">Total Reactions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(reaction_analysis['reaction_types'])}</div>
                    <div class="metric-label">Reaction Types</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_recommendations_html(self, recommendations: list) -> str:
        """Generate recommendations HTML"""
        html = '<div class="recommendations">'
        
        for rec in recommendations:
            priority_class = rec['priority']
            html += f"""
            <div class="recommendation {priority_class}">
                <strong>{rec['priority'].upper()} Priority:</strong> {rec['recommendation']}
            </div>
            """
        
        html += '</div>'
        return html
    
    def _generate_optimal_times_html(self, optimal_times: dict) -> str:
        """Generate optimal messaging times HTML"""
        html = '<div class="optimal-times"><h3>Best Times to Send Messages:</h3><ul>'
        
        for time_slot in optimal_times.get('overall_best_times', [])[:5]:
            html += f"<li>{time_slot['time']} - Engagement Score: {time_slot['engagement_score']:.2f}</li>"
        
        html += '</ul></div>'
        return html
    
    def generate_pdf_report(self) -> str:
        """Generate PDF report (requires additional libraries like reportlab or weasyprint)"""
        # This would require additional PDF generation libraries
        # For now, returning a placeholder path
        pdf_path = f"/tmp/report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # In production, you would use libraries like:
        # - reportlab for programmatic PDF creation
        # - weasyprint to convert HTML to PDF
        # - pdfkit with wkhtmltopdf
        
        return pdf_path
    
    def generate_json_report(self) -> dict:
        """Generate JSON report with all analysis data"""
        return {
            "metadata": {
                "generated_at": self.timestamp.isoformat(),
                "total_messages": len(self.df),
                "participants": self.df['sender'].nunique(),
                "date_range": f"{self.df['date'].min()} to {self.df['date'].max()}"
            },
            "analysis": {
                "basic_stats": self.analyzer.get_basic_stats(),
                "user_stats": self.analyzer.get_user_stats().to_dict('records'),
                "temporal_analysis": self.analyzer.get_temporal_analysis(),
                "emoji_analysis": self.analyzer.get_emoji_analysis(),
                "sentiment_analysis": self.analyzer.get_sentiment_analysis(),
                "reaction_analysis": self.analyzer.get_reaction_analysis(),
                "word_analysis": {
                    "total_words": self.analyzer.get_word_analysis()['total_words'],
                    "unique_words": self.analyzer.get_word_analysis()['unique_words'],
                    "top_words": self.analyzer.get_word_analysis()['top_words'][:20]
                },
                "conversation_flow": self.analyzer.get_conversation_flow(),
                "activity_patterns": self.analyzer.get_activity_patterns()
            },
            "predictions": self.predictor.get_prediction_summary()
        }
