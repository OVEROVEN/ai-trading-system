#!/usr/bin/env python3
"""
圖表生成微服務
專門處理所有可視化和圖表生成功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import logging
from datetime import datetime

# 圖表生成模組 (容錯導入)
chart_generator = None
professional_chart_generator = None
tradingview_chart_generator = None

try:
    from src.visualization.chart_generator import ChartGenerator
    chart_generator = ChartGenerator()
    logging.info("基礎圖表生成器初始化成功")
except Exception as e:
    logging.error(f"基礎圖表生成器初始化失敗: {e}")

try:
    from src.visualization.professional_charts import ProfessionalChartGenerator
    professional_chart_generator = ProfessionalChartGenerator()
    logging.info("專業圖表生成器初始化成功")
except Exception as e:
    logging.error(f"專業圖表生成器初始化失敗: {e}")

try:
    from src.visualization.tradingview_charts import TradingViewStyleChart
    tradingview_chart_generator = TradingViewStyleChart()
    logging.info("TradingView圖表生成器初始化成功")
except Exception as e:
    logging.error(f"TradingView圖表生成器初始化失敗: {e}")

# FastAPI app
app = FastAPI(
    title="Chart Generation Service",
    description="專業圖表生成微服務",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChartRequest(BaseModel):
    symbol: str
    period: str = "3mo"
    chart_type: str = "professional"  # professional, tradingview, basic
    theme: str = "dark"
    indicators: Optional[Dict[str, Any]] = {}
    patterns: Optional[List[Dict]] = []
    data: Optional[Dict[str, Any]] = None

class ChartResponse(BaseModel):
    chart_html: str
    chart_type: str
    symbol: str
    generated_at: str
    success: bool
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "service": "Chart Generation Service",
        "version": "1.0.0",
        "status": "operational",
        "available_generators": {
            "basic": chart_generator is not None,
            "professional": professional_chart_generator is not None,
            "tradingview": tradingview_chart_generator is not None
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "generators_status": {
            "basic": "available" if chart_generator else "unavailable",
            "professional": "available" if professional_chart_generator else "unavailable", 
            "tradingview": "available" if tradingview_chart_generator else "unavailable"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate-chart", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    """生成圖表的核心API"""
    try:
        # 模擬數據準備 (實際應用中會從核心服務獲取)
        if not request.data:
            # 返回示例圖表
            return ChartResponse(
                chart_html="<div>示例圖表 - 需要數據集成</div>",
                chart_type=request.chart_type,
                symbol=request.symbol,
                generated_at=datetime.now().isoformat(),
                success=True
            )
        
        # 準備數據
        data_df = pd.DataFrame(request.data)
        
        chart_html = None
        
        # 根據類型選擇生成器
        if request.chart_type == "professional":
            if professional_chart_generator is None:
                raise HTTPException(status_code=503, detail="專業圖表生成器不可用")
            
            chart_html = professional_chart_generator.create_professional_chart(
                data=data_df,
                symbol=request.symbol,
                indicators=request.indicators,
                patterns=request.patterns,
                theme=request.theme
            )
            
        elif request.chart_type == "tradingview":
            if tradingview_chart_generator is None:
                raise HTTPException(status_code=503, detail="TradingView圖表生成器不可用")
            
            chart_html = tradingview_chart_generator.create_chart(
                data=data_df,
                symbol=request.symbol,
                indicators=request.indicators,
                patterns=request.patterns,
                theme=request.theme
            )
            
        else:  # basic
            if chart_generator is None:
                raise HTTPException(status_code=503, detail="基礎圖表生成器不可用")
            
            chart_html = chart_generator.create_candlestick_chart(
                data=data_df,
                symbol=request.symbol,
                indicators=request.indicators,
                patterns=request.patterns
            )
        
        if chart_html is None:
            raise HTTPException(status_code=500, detail="圖表生成失敗")
        
        return ChartResponse(
            chart_html=chart_html,
            chart_type=request.chart_type,
            symbol=request.symbol,
            generated_at=datetime.now().isoformat(),
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"圖表生成失敗: {str(e)}")
        return ChartResponse(
            chart_html=f"<div class='error'>圖表生成失敗: {str(e)}</div>",
            chart_type=request.chart_type,
            symbol=request.symbol,
            generated_at=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/chart-types")
async def get_chart_types():
    """獲取可用的圖表類型"""
    return {
        "basic": {
            "available": chart_generator is not None,
            "description": "基礎K線圖表"
        },
        "professional": {
            "available": professional_chart_generator is not None,
            "description": "專業技術分析圖表"
        },
        "tradingview": {
            "available": tradingview_chart_generator is not None,
            "description": "TradingView風格圖表"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)