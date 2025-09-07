#!/usr/bin/env python3
"""
測試 WebSocket 即時數據流
"""
import asyncio
import websockets
import json

async def test_websocket():
    """測試 WebSocket 連接"""
    try:
        # 連接到 WebSocket
        uri = "ws://localhost:8000/stream/AAPL"
        
        print("正在連接 WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("已連接到 AAPL 即時數據流")
            
            # 接收幾個消息
            for i in range(3):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"接收到數據 {i+1}: {data}")
                
    except Exception as e:
        print(f"WebSocket 測試失敗: {str(e)}")

if __name__ == "__main__":
    print("測試 WebSocket 即時數據流...")
    asyncio.run(test_websocket())