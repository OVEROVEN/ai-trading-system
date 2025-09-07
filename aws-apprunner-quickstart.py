#!/usr/bin/env python3
"""
AWS App Runner快速部署腳本
"""
import boto3
import json
import time
from datetime import datetime

def create_apprunner_service():
    """創建AWS App Runner服務"""
    
    # 配置
    service_name = "auto-trade-ai-system"
    github_repo = "https://github.com/OVEROVEN/auto_trade"
    
    # App Runner配置
    app_runner_config = {
        "ServiceName": service_name,
        "SourceConfiguration": {
            "ImageRepository": {
                "ImageIdentifier": "public.ecr.aws/docker/library/python:3.11",
                "ImageConfiguration": {
                    "Port": "8000",
                    "RuntimeEnvironmentVariables": {
                        "ENVIRONMENT": "production",
                        "DEBUG": "false",
                        "DATABASE_URL": "sqlite:///tmp/trading.db",
                        "JWT_SECRET_KEY": "pI3tqLLwskk4HQ4fSlLOo32VuRsllB3Z_1eMzgrqjmY",
                        "GOOGLE_CLIENT_ID": "610357573971-t2r6c0b3i8fq8kng1j8e5s4l6jiqiggf.apps.googleusercontent.com",
                        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
                    },
                    "StartCommand": "pip install -r requirements-core.txt && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
                }
            },
            "AutoDeploymentsEnabled": True
        },
        "InstanceConfiguration": {
            "Cpu": "0.25 vCPU",
            "Memory": "0.5 GB"
        },
        "HealthCheckConfiguration": {
            "Protocol": "HTTP", 
            "Path": "/health",
            "Interval": 10,
            "Timeout": 5,
            "HealthyThreshold": 1,
            "UnhealthyThreshold": 5
        },
        "Tags": [
            {"Key": "Project", "Value": "AI-Trading-System"},
            {"Key": "Environment", "Value": "Production"},
            {"Key": "CreatedBy", "Value": "Claude-Code"}
        ]
    }
    
    print("🚀 AWS App Runner部署指南")
    print("=" * 50)
    print("\n📋 部署配置:")
    print(f"   服務名稱: {service_name}")
    print(f"   GitHub倉庫: {github_repo}")
    print(f"   CPU: 0.25 vCPU")
    print(f"   Memory: 0.5 GB") 
    print(f"   健康檢查: /health")
    
    print(f"\n💰 預估月費: $5-15")
    print(f"🌍 建議區域: us-east-1 或 ap-northeast-1 (東京)")
    
    # 生成CloudFormation模板
    cloudformation_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "AI Trading System - AWS App Runner Deployment",
        "Resources": {
            "AutoTradeAppRunnerService": {
                "Type": "AWS::AppRunner::Service",
                "Properties": app_runner_config
            }
        },
        "Outputs": {
            "ServiceUrl": {
                "Description": "App Runner服務URL",
                "Value": {"Fn::GetAtt": ["AutoTradeAppRunnerService", "ServiceUrl"]}
            },
            "ServiceArn": {
                "Description": "App Runner服務ARN", 
                "Value": {"Ref": "AutoTradeAppRunnerService"}
            }
        }
    }
    
    # 保存CloudFormation模板
    with open("aws-apprunner-template.json", "w") as f:
        json.dump(cloudformation_template, f, indent=2)
    
    print(f"\n✅ CloudFormation模板已生成: aws-apprunner-template.json")
    
    print(f"\n🚀 部署步驟:")
    print("1. 登入AWS控制台")
    print("2. 前往CloudFormation服務")
    print("3. 創建新Stack")
    print("4. 上傳模板文件")
    print("5. 5-10分鐘完成部署")
    
    print(f"\n🎯 部署後測試:")
    print("1. 訪問 https://YOUR-SERVICE-URL/health")
    print("2. 測試 https://YOUR-SERVICE-URL/docs")
    print("3. 驗證兌換碼功能正常")
    
    return True

if __name__ == "__main__":
    create_apprunner_service()
    
    print(f"\n🎊 準備完成！")
    print(f"📁 文件生成: aws-apprunner-template.json")
    print(f"⏰ 部署時間: 5-10分鐘")
    print(f"💎 穩定性: 企業級 (99.9% SLA)")
    print(f"\n需要我幫您執行部署嗎？")