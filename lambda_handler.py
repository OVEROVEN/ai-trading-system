
"""
AWS Lambda handler for FastAPI
"""
try:
    from mangum import Mangum
    from src.api.main_core import app
    
    # 創建Lambda處理器
    handler = Mangum(app, lifespan="off")
    
    # Lambda入口點
    def lambda_handler(event, context):
        return handler(event, context)
        
except ImportError:
    # 如果沒有mangum，創建基本處理器
    def lambda_handler(event, context):
        return {
            'statusCode': 200,
            'body': '{"message": "Auto-Trade Core API - Install mangum for full functionality"}'
        }
