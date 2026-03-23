#!/usr/bin/env python3
"""
简单的HTTP服务器，用于测试FlowNav前端
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from datetime import datetime

PORT = 8081
HOST = 'localhost'

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""

    def end_headers(self):
        # 添加CORS头部
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        # 自定义日志格式
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

def main():
    # 切换到脚本所在目录（项目根目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 检查必需文件
    required_files = ['index.html', 'style.css', 'app.js', 'mockData.js', 'api.js']
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        print("错误: 以下文件缺失:")
        for f in missing_files:
            print(f"  - {f}")
        print("\n请确保所有前端文件已创建。")
        return 1

    print("=" * 60)
    print("FlowNav 前端测试服务器")
    print("=" * 60)
    print(f"目录: {os.getcwd()}")
    print(f"地址: http://{HOST}:{PORT}")
    print("=" * 60)
    print("\n可用文件:")
    for file in os.listdir('.'):
        if file.endswith(('.html', '.css', '.js', '.md')):
            print(f"  - {file}")

    print("\n正在启动服务器...")
    print("按 Ctrl+C 停止服务器")

    try:
        with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
            # 尝试自动打开浏览器
            try:
                webbrowser.open(f'http://{HOST}:{PORT}')
                print(f"已尝试在浏览器中打开 http://{HOST}:{PORT}")
            except:
                print(f"请在浏览器中手动访问: http://{HOST}:{PORT}")

            print(f"服务器运行在端口 {PORT}")
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n服务器已停止")
        return 0
    except OSError as e:
        if e.errno == 10048:  # 端口被占用
            print(f"\n错误: 端口 {PORT} 已被占用")
            print("请尝试:")
            print(f"  1. 关闭占用端口 {PORT} 的其他程序")
            print(f"  2. 修改 serve.py 中的 PORT 变量为其他端口")
        else:
            print(f"\n错误: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())