"""
FastAPI Backend for WhatsApp Analyzer
Provides REST API endpoints for the analysis
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import json
import pandas as pd
from datetime import datetime
import tempfile
import os
import shutil
from pathlib import Path

# Import analyzer modules
from parser import WhatsAppParser
from analyzer import ChatAnalyzer
from predictor import ChatPredictor
from visualizer import ChatVisualizer
from report_generator import ReportGenerator

app = FastAPI(
    title="WhatsApp Analyzer API",
    description="Comprehensive WhatsApp chat analysis with predictions",
    version="2.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store analysis results temporarily (in production, use Redis or database)
analysis_cache = {}

class AnalysisRequest(BaseModel):
    session_id: str
    include_predictions: bool = True
    include_reactions: bool = True

class PredictionRequest(BaseModel):
    session_id: str
    days_ahead: int = 7

class ExportRequest(BaseModel):
    session_id: str
    format: str = "json"  # json, csv, html, pdf
    include_visualizations: bool = True

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "WhatsApp Analyzer API",
        "version": "2.0.0",
        "endpoints": [
            "/upload_chat",
            "/get_analysis/{session_id}",
            "/get_user_stats/{session_id}",
            "/get_predictions/{session_id}",
            "/get_reactions/{session_id}",
            "/get_wordcloud/{session_id}",
            "/export_report",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload_chat")
async def upload_chat(file: UploadFile = File(...)):
    """
    Upload and parse WhatsApp chat export
    Returns session_id for subsequent API calls
    """
    try:
        # Generate session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse chat
        parser = WhatsAppParser()
        df = parser.parse_chat(temp_path)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No messages found in the file")
        
        # Store in cache
        analysis_cache[session_id] = {
            "df": df,
            "upload_time": datetime.now(),
            "filename": file.filename,
            "message_count": len(df),
            "participants": df['sender'].nunique()
        }
        
        # Clean up temp file
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        return {
            "session_id": session_id,
            "status": "success",
            "messages_parsed": len(df),
            "participants": df['sender'].nunique(),
            "date_range": f"{df['date'].min()} to {df['date'].max()}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_analysis/{session_id}")
async def get_analysis(session_id: str):
    """Get comprehensive analysis results"""
    if session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[session_id]["df"]
        analyzer = ChatAnalyzer(df)
        
        analysis = {
            "basic_stats": analyzer.get_basic_stats(),
            "temporal_analysis": analyzer.get_temporal_analysis(),
            "emoji_analysis": analyzer.get_emoji_analysis(),
            "word_analysis": analyzer.get_word_analysis(),
            "conversation_flow": analyzer.get_conversation_flow(),
            "sentiment_analysis": analyzer.get_sentiment_analysis(),
            "activity_patterns": analyzer.get_activity_patterns(),
            "reaction_analysis": analyzer.get_reaction_analysis()
        }
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_user_stats/{session_id}")
async def get_user_stats(session_id: str):
    """Get detailed user statistics"""
    if session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[session_id]["df"]
        analyzer = ChatAnalyzer(df)
        user_stats = analyzer.get_user_stats()
        
        # Convert DataFrame to dict for JSON response
        return JSONResponse(content=user_stats.to_dict('records'))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_predictions/{session_id}")
async def get_predictions(session_id: str, days_ahead: int = 7):
    """Get ML-based predictions"""
    if session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[session_id]["df"]
        predictor = ChatPredictor(df)
        
        predictions = {
            "optimal_messaging_times": predictor.predict_optimal_messaging_time(),
            "future_activity": predictor.predict_future_activity(days_ahead),
            "user_activity_predictions": predictor.predict_user_activity(),
            "trending_topics": predictor.predict_conversation_topics()
        }
        
        # Add recommendations
        predictions["recommendations"] = predictor.generate_recommendations(predictions)
        
        return JSONResponse(content=predictions)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_reactions/{session_id}")
async def get_reactions(session_id: str):
    """Get reaction analysis"""
    if session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[session_id]["df"]
        analyzer = ChatAnalyzer(df)
        reaction_analysis = analyzer.get_reaction_analysis()
        
        return JSONResponse(content=reaction_analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_wordcloud/{session_id}")
async def get_wordcloud(session_id: str):
    """Generate and return word cloud data"""
    if session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[session_id]["df"]
        analyzer = ChatAnalyzer(df)
        word_analysis = analyzer.get_word_analysis()
        
        # Return word frequency for frontend to generate cloud
        return JSONResponse(content={
            "word_frequency": dict(word_analysis["word_frequency"].most_common(100)),
            "total_words": word_analysis["total_words"],
            "unique_words": word_analysis["unique_words"]
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export_report")
async def export_report(request: ExportRequest):
    """Export analysis report in various formats"""
    if request.session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[request.session_id]["df"]
        analyzer = ChatAnalyzer(df)
        predictor = ChatPredictor(df)
        
        # Generate report based on format
        if request.format == "json":
            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_messages": len(df),
                    "participants": df['sender'].nunique()
                },
                "analysis": {
                    "basic_stats": analyzer.get_basic_stats(),
                    "user_stats": analyzer.get_user_stats().to_dict('records'),
                    "temporal_analysis": analyzer.get_temporal_analysis(),
                    "emoji_analysis": analyzer.get_emoji_analysis(),
                    "sentiment_analysis": analyzer.get_sentiment_analysis(),
                    "reaction_analysis": analyzer.get_reaction_analysis()
                }
            }
            
            if request.include_visualizations:
                report_data["predictions"] = predictor.get_prediction_summary()
            
            return JSONResponse(content=report_data)
            
        elif request.format == "csv":
            # Export user statistics as CSV
            user_stats = analyzer.get_user_stats()
            csv_path = f"/tmp/report_{request.session_id}.csv"
            user_stats.to_csv(csv_path, index=False)
            
            return FileResponse(
                path=csv_path,
                filename=f"whatsapp_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                media_type="text/csv"
            )
            
        elif request.format == "html":
            # Generate HTML report
            generator = ReportGenerator(df, analyzer, predictor)
            html_content = generator.generate_html_report()
            
            return HTMLResponse(content=html_content)
            
        elif request.format == "pdf":
            # Generate PDF report (requires additional library)
            generator = ReportGenerator(df, analyzer, predictor)
            pdf_path = generator.generate_pdf_report()
            
            return FileResponse(
                path=pdf_path,
                filename=f"whatsapp_analysis_{datetime.now().strftime('%Y%m%d')}.pdf",
                media_type="application/pdf"
            )
            
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_activity_heatmap/{session_id}")
async def get_activity_heatmap(session_id: str):
    """Get activity heatmap data"""
    if session_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        df = analysis_cache[session_id]["df"]
        analyzer = ChatAnalyzer(df)
        temporal_analysis = analyzer.get_temporal_analysis()
        
        return JSONResponse(content={
            "heatmap_data": temporal_analysis["heatmap_data"],
            "peak_hour": temporal_analysis["peak_hour"],
            "peak_day": temporal_analysis["peak_day"]
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_session/{session_id}")
async def clear_session(session_id: str):
    """Clear session data from cache"""
    if session_id in analysis_cache:
        del analysis_cache[session_id]
        return {"status": "success", "message": "Session cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/list_sessions")
async def list_sessions():
    """List all active sessions (for debugging)"""
    sessions = []
    for sid, data in analysis_cache.items():
        sessions.append({
            "session_id": sid,
            "upload_time": data["upload_time"].isoformat(),
            "filename": data["filename"],
            "message_count": data["message_count"],
            "participants": data["participants"]
        })
    
    return JSONResponse(content={"sessions": sessions, "total": len(sessions)})

# Background task to clean old sessions
async def cleanup_old_sessions():
    """Remove sessions older than 24 hours"""
    current_time = datetime.now()
    to_remove = []
    
    for session_id, data in analysis_cache.items():
        if (current_time - data["upload_time"]).total_seconds() > 86400:  # 24 hours
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del analysis_cache[session_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
