# 💬 WhatsApp Group Analyzer v2.0

A comprehensive, production-ready WhatsApp chat analysis tool with machine learning predictions, reaction analysis, REST API, and interactive visualizations.

## 🚀 What's New in v2.0

- **📱 Reaction Analysis**: Full support for WhatsApp reactions
- **🔌 FastAPI Backend**: REST API endpoints for integration
- **📊 Enhanced Visualizations**: More interactive charts
- **📄 Multi-format Export**: JSON, CSV, HTML, PDF reports  
- **🎯 Better Predictions**: Improved ML models
- **🔧 Modular Architecture**: Clean, scalable code structure

## 🌟 Features

### Core Analysis
- **Multi-Platform Support**: Works with Android & iOS exports
- **Comprehensive Statistics**: Messages, words, emojis, media, URLs, reactions
- **User Insights**: Individual activity patterns and behaviors
- **Temporal Analysis**: Hour/day/month activity patterns
- **Sentiment Analysis**: Message sentiment scoring and trends
- **Conversation Flow**: Message chains and patterns
- **Reaction Analysis**: Who gives/receives most reactions, popular reactions

### Advanced Features
- **🔮 ML Predictions**:
  - Optimal messaging times for maximum engagement
  - 7-day activity forecast with accuracy metrics
  - User activity predictions
  - Trending topic identification
  - Engagement score calculation

- **📊 Interactive Visualizations**:
  - Zoomable timeline charts
  - Activity heatmaps
  - Word clouds
  - Emoji & reaction analysis
  - Response time analysis
  - Sentiment trends
  - User comparison charts

- **🔌 REST API** (FastAPI):
  - `/upload_chat` - Upload and parse chat
  - `/get_analysis/{session_id}` - Get full analysis
  - `/get_user_stats/{session_id}` - User statistics
  - `/get_predictions/{session_id}` - ML predictions
  - `/get_reactions/{session_id}` - Reaction analysis
  - `/get_wordcloud/{session_id}` - Word cloud data
  - `/export_report` - Export in various formats

- **📥 Export Options**:
  - JSON (complete data structure)
  - CSV (tabular format)
  - HTML (interactive report)
  - PDF (print-ready report)

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

1. **Navigate to project directory**:
```bash
cd "C:\Users\muhammed.Ansari\Documents\CS projects\hmg\HMGenius\Whatsapp_analysis"
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run setup script** (downloads NLTK data, creates sample files):
```bash
python setup.py
```

4. **Launch the application**:
```bash
# For Windows - interactive menu
run.bat

# Or directly:
# Streamlit only
streamlit run app.py

# FastAPI only  
python -m uvicorn api:app --reload

# Both
# Terminal 1: streamlit run app.py
# Terminal 2: python -m uvicorn api:app --reload
```

## 📱 How to Export WhatsApp Chat

### Android
1. Open WhatsApp → Select chat/group
2. Tap menu (⋮) → More → Export chat
3. Choose "Without media" (faster) or "With media"
4. Save the .txt file

### iOS
1. Open WhatsApp → Select chat/group
2. Tap contact/group name → Export Chat
3. Choose "Without Media" or "Attach Media"
4. Save the .txt file

## 🎯 Usage

### Option 1: Streamlit Dashboard (Recommended for Quick Analysis)

1. Run `streamlit run app.py` or use `run.bat`
2. Browser opens at `http://localhost:8501`
3. Upload your WhatsApp export or use sample data
4. Explore:
   - **Analysis Dashboard**: Overall statistics
   - **User Insights**: Individual analysis
   - **Predictions**: ML-based forecasts
   - **Visualizations**: Interactive charts
   - **Export Report**: Download results

### Option 2: FastAPI REST API (For Integration)

1. Run `python -m uvicorn api:app --reload`
2. API available at `http://localhost:8000`
3. Interactive docs at `http://localhost:8000/docs`

**Example API Usage**:
```python
import requests

# Upload chat file
with open('chat.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload_chat',
        files={'file': f}
    )
    session_id = response.json()['session_id']

# Get analysis
analysis = requests.get(f'http://localhost:8000/get_analysis/{session_id}')
print(analysis.json())

# Get predictions
predictions = requests.get(f'http://localhost:8000/get_predictions/{session_id}')
print(predictions.json())
```

## 📊 Analysis Modules

### 1. Parser Module (`parser.py`)
- Auto-detects chat format (Android/iOS)
- Handles multiple date/time formats
- Extracts reactions (new WhatsApp feature)
- Filters system messages
- Handles multi-line messages

### 2. Analyzer Module (`analyzer.py`)
- Basic statistics calculation
- User activity analysis
- Reaction analysis (who gives/receives)
- Temporal pattern detection
- Sentiment analysis (VADER)
- Word frequency analysis
- Conversation flow analysis

### 3. Predictor Module (`predictor.py`)
- Random Forest & Gradient Boosting models
- Optimal messaging time prediction
- Future activity forecasting (7-day)
- User activity pattern prediction
- Topic trend analysis
- Engagement scoring

### 4. Visualizer Module (`visualizer.py`)
- Plotly interactive charts
- Activity heatmaps
- Word clouds
- Emoji visualizations
- Reaction charts
- Response time analysis

### 5. API Module (`api.py`)
- FastAPI REST endpoints
- Session management
- Multi-format export
- CORS enabled for frontend integration

### 6. Report Generator (`report_generator.py`)
- HTML report generation
- PDF export capability
- JSON structured data
- CSV tabular format

## 📈 Visualizations

### Available Charts
1. **Message Timeline**: Daily message count with trends
2. **Activity Heatmap**: Hour vs Day patterns
3. **User Activity**: Comparative statistics
4. **Word Cloud**: Frequently used words
5. **Emoji Analysis**: Top emojis by user
6. **Reaction Analysis**: Most reacted messages
7. **Sentiment Timeline**: Emotion trends
8. **Response Time**: Average by user
9. **Prediction Charts**: Future forecasts
10. **Engagement Heatmap**: Best times to message

## 🔮 Predictions & Insights

### Features
- **Optimal Messaging Times**: Best times for engagement
- **Activity Forecasting**: 7-day predictions with confidence
- **User Patterns**: Individual activity predictions
- **Topic Trends**: Emerging conversation topics
- **Recommendations**: Actionable insights

## 📦 Project Structure

```
Whatsapp_analysis/
├── 📄 app.py                 # Streamlit dashboard
├── 📄 api.py                 # FastAPI backend
├── 📄 parser.py              # Chat parser (Android/iOS)
├── 📄 analyzer.py            # Analysis engine
├── 📄 predictor.py           # ML predictions
├── 📄 visualizer.py          # Chart generation
├── 📄 report_generator.py    # Report exports
├── 📄 setup.py               # Setup script
├── 📄 requirements.txt       # Dependencies
├── 📄 run.bat               # Windows launcher
├── 📄 README.md             # Documentation
├── 📁 .streamlit/           # Streamlit config
│   └── config.toml
└── 📁 reports/              # Generated reports
```

## 🔧 Configuration

### Streamlit Config (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#25D366"      # WhatsApp green
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[server]
maxUploadSize = 50            # Max file size in MB
```

### API Configuration
- Default port: 8000
- CORS enabled for all origins
- Session timeout: 24 hours

## 🛠️ Troubleshooting

### Common Issues & Solutions

1. **"Unable to detect chat format"**
   - Ensure valid WhatsApp export file
   - Check date format (MM/DD/YY or DD/MM/YY)
   - Try different export options

2. **Float formatting error**
   - Fixed in v2.0
   - Update to latest version

3. **Missing reactions**
   - Reactions only available in newer WhatsApp versions
   - Export chat again if recently updated

4. **API not starting**
   - Check port 8000 availability
   - Install FastAPI: `pip install fastapi uvicorn`

5. **Large file processing**
   - Export without media for faster processing
   - Increase Streamlit upload limit in config

## 🚀 Advanced Usage

### Custom Analysis
```python
from parser import WhatsAppParser
from analyzer import ChatAnalyzer
from predictor import ChatPredictor

# Parse chat
parser = WhatsAppParser()
df = parser.parse_chat('chat.txt')

# Analyze
analyzer = ChatAnalyzer(df)
stats = analyzer.get_basic_stats()
reactions = analyzer.get_reaction_analysis()

# Predict
predictor = ChatPredictor(df)
predictions = predictor.get_prediction_summary()
```

### API Integration
```javascript
// React/Angular example
const uploadChat = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/upload_chat', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.session_id;
};
```

## 🔒 Privacy & Security

- **100% Local Processing**: No data leaves your computer
- **No Cloud Storage**: All analysis happens locally
- **Session Management**: Auto-cleanup after 24 hours
- **Open Source**: Full code transparency

## 📄 Export Formats

### JSON
- Complete structured data
- All metrics and predictions
- Easy integration with other tools

### CSV
- Tabular user statistics
- Excel-compatible
- Easy filtering and sorting

### HTML
- Interactive report
- Embedded charts
- Print-friendly styling

### PDF
- Professional reports
- Charts and tables
- Executive summaries

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional visualizations
- More ML models
- Language support
- Real-time analysis
- Group comparison

## 📝 License

MIT License - Free to use and modify

## 🙏 Acknowledgments

- Built with Streamlit, FastAPI, Plotly
- Sentiment analysis by VADER
- ML models by scikit-learn
- Emoji support by emoji package

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Test with sample data
3. Review error logs
4. Check API docs at `/docs`

## 🎉 Quick Start Examples

### Basic Analysis
```bash
# Simple analysis
python -c "from parser import WhatsAppParser; p = WhatsAppParser(); df = p.parse_chat('sample_chat.txt'); print(f'Messages: {len(df)}')"
```

### API Quick Test
```bash
# Test API
curl -X POST "http://localhost:8000/upload_chat" -F "file=@sample_chat.txt"
```

---

**Note**: This tool respects WhatsApp's terms of service by only analyzing exported chat data. It does not access WhatsApp directly or bypass any security measures.

**Version**: 2.0.0 | **Last Updated**: August 2025
