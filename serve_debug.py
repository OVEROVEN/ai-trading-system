#!/usr/bin/env python3
"""
簡單的調試頁面服務器
"""

import http.server
import socketserver
import webbrowser
import threading
import time

def serve_debug_page():
    """啟動調試頁面服務器"""
    PORT = 8080
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Debug server started at http://localhost:{PORT}")
            print("Available pages:")
            print(f"  - Debug Tool: http://localhost:{PORT}/debug_right_panel.html")
            print("\nPress Ctrl+C to stop")
            
            # 自動打開瀏覽器
            def open_browser():
                time.sleep(1)
                webbrowser.open(f"http://localhost:{PORT}/debug_right_panel.html")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDebug server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use. Please stop other services or use a different port.")
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    serve_debug_page()