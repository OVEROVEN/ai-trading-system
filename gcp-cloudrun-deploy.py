#!/usr/bin/env python3
"""
Google Cloud Run部署腳本
"""
import subprocess
import json

def deploy_to_cloudrun():
    """部署到Google Cloud Run"""
    
    print("☁️ Google Cloud Run部署指南")
    print("=" * 50)
    
    # 項目配置
    project_id = "your-project-id"  # 需要替換
    service_name = "auto-trade-ai"
    region = "asia-northeast1"  # 東京
    
    print(f"\n📋 部署配置:")
    print(f"   專案ID: {project_id}")
    print(f"   服務名稱: {service_name}")
    print(f"   地區: {region} (東京)")
    print(f"   記憶體: 1GB")
    print(f"   CPU: 1")
    
    # 創建Dockerfile（針對Cloud Run優化）
    cloudrun_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements-core.txt .
RUN pip install --no-cache-dir -r requirements-core.txt

# 複製代碼
COPY src/ ./src/
COPY config/ ./config/

# 設置環境
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///tmp/trading.db

# Cloud Run會自動設置PORT
EXPOSE $PORT

CMD python -m uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
"""
    
    with open("Dockerfile.cloudrun", "w") as f:
        f.write(cloudrun_dockerfile)
    
    print(f"\n✅ Dockerfile.cloudrun 已創建")
    
    # 部署命令
    deploy_commands = [
        "# 1. 設置專案",
        f"gcloud config set project {project_id}",
        "",
        "# 2. 啟用服務",
        "gcloud services enable run.googleapis.com",
        "gcloud services enable cloudbuild.googleapis.com", 
        "",
        "# 3. 構建並部署",
        f"gcloud run deploy {service_name} \\",
        "  --source . \\",
        f"  --region {region} \\",
        "  --platform managed \\",
        "  --allow-unauthenticated \\",
        "  --memory 1Gi \\",
        "  --cpu 1 \\",
        "  --timeout 900 \\",
        "  --set-env-vars ENVIRONMENT=production,DEBUG=false,DATABASE_URL=sqlite:///tmp/trading.db",
        "",
        "# 4. 設置敏感環境變數",
        f"gcloud run services update {service_name} \\",
        f"  --region {region} \\",
        "  --set-env-vars OPENAI_API_KEY=YOUR_KEY,JWT_SECRET_KEY=YOUR_SECRET"
    ]
    
    with open("cloudrun-deploy.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Google Cloud Run部署腳本\n\n")
        for cmd in deploy_commands:
            f.write(cmd + "\n")
    
    print(f"✅ cloudrun-deploy.sh 部署腳本已創建")
    
    print(f"\n🚀 快速部署步驟:")
    print("1. 登入 https://console.cloud.google.com")
    print("2. 創建新項目或選擇現有項目")
    print("3. 開啟 Cloud Shell")
    print("4. 上傳代碼並執行 bash cloudrun-deploy.sh")
    print("5. 5分鐘內完成部署")
    
    print(f"\n💰 費用評估:")
    print("   免費額度: 每月200萬請求")
    print("   付費: ~$0.001/請求 (超出免費額度後)")
    print("   預估月費: $0-10 (免費額度通常夠用)")
    
    return True

if __name__ == "__main__":
    deploy_to_cloudrun()
    
    print(f"\n🎯 建議選擇:")
    print("✅ Google Cloud Run - 免費額度充足，適合個人項目")
    print("✅ AWS App Runner - 企業級穩定，適合商業使用")
    print("\n您偏好哪個平台？我立即幫您完成部署配置！")