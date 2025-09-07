#!/usr/bin/env python3
"""
HTTPS測試服務器
用於測試TradingView Widget在HTTPS環境下的表現
"""

import http.server
import ssl
import socketserver
import os
from pathlib import Path

def create_test_server():
    """創建HTTPS測試服務器"""
    
    print("=== TradingView Widget HTTPS 測試服務器 ===")
    print()
    
    # 設定服務器參數
    PORT = 8443
    CERT_FILE = "server.crt" 
    KEY_FILE = "server.key"
    
    # 檢查是否需要創建自簽名證書
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print("🔐 創建自簽名SSL證書...")
        create_self_signed_cert()
    
    # 設定文檔根目錄
    os.chdir(Path(__file__).parent)
    
    # 創建HTTP處理器
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        # 包裝為HTTPS
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        print(f"✅ HTTPS服務器啟動成功!")
        print(f"📍 本地訪問: https://localhost:{PORT}")
        print()
        print("🧪 測試連結:")
        print(f"   台積電Widget: https://localhost:{PORT}/demo_charts/2330_fixed.html")
        print(f"   演示首頁:     https://localhost:{PORT}/demo_charts/index.html")
        print(f"   CodePen測試:  https://localhost:{PORT}/codepen_test.html")
        print()
        print("⚠️  瀏覽器會顯示證書警告，點擊「繼續訪問」即可")
        print("🛑 按 Ctrl+C 停止服務器")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服務器已停止")

def create_self_signed_cert():
    """創建自簽名證書（僅用於測試）"""
    try:
        import subprocess
        
        # 使用OpenSSL創建自簽名證書
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", "server.key", "-out", "server.crt", 
            "-days", "365", "-nodes", "-subj", 
            "/C=TW/ST=Taiwan/L=Taipei/O=Test/OU=TradingView Widget Test/CN=localhost"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSL證書創建成功")
        else:
            print("❌ 無法創建SSL證書，請手動安裝OpenSSL")
            print("或使用其他測試方法")
            return False
            
    except FileNotFoundError:
        print("❌ 找不到OpenSSL，使用簡化版本...")
        create_simple_cert()
    
    return True

def create_simple_cert():
    """創建簡單的測試證書"""
    import ssl
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import datetime
    
    try:
        # 生成私鑰
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 創建證書
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"TW"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Taiwan"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Taipei"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Test"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # 保存證書
        with open("server.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open("server.key", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ 使用Python生成SSL證書成功")
        
    except ImportError:
        print("❌ 缺少cryptography庫，使用手動證書生成...")
        print("   請手動運行: pip install cryptography")
        return False
    
    return True

if __name__ == "__main__":
    create_test_server()