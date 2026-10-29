"""
KYANOS Market Pulse - Realtime Web Dashboard Server
Directly serves d:\\안티그래비티파이튼\\market_monitor.html with live /api/market API
Lightweight, Zero-dependency Python HTTP Server
Access via http://localhost:8899
"""
import http.server
import socketserver
import json
import webbrowser
import threading
import sys
import os
import mimetypes

# UTF-8 stdout configuration
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path에 현재 디렉터리 추가 (market_data 임포트 보장)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from market_data import get_all_market_data

PORT = 8899
WORKSPACE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
MARKET_HTML_FILE = os.path.join(WORKSPACE_ROOT, "market_monitor.html")

class MarketHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        clean_path = self.path.split('?')[0]
        
        # 1. 루트 또는 메인 HTML 요청
        if clean_path in ('/', '/index.html', '/market_monitor.html'):
            if os.path.exists(MARKET_HTML_FILE):
                try:
                    with open(MARKET_HTML_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    self.send_error(500, f"HTML Read Error: {e}")
                    return
            else:
                self.send_error(404, "market_monitor.html not found")
                return

        # 2. 실시간 시세 API 엔드포인트
        elif clean_path == '/api/market':
            try:
                data = get_all_market_data()
                payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(payload)
                return
            except Exception as e:
                self.send_error(500, f"API Data Error: {e}")
                return

        # 3. assets 및 정적 파일 서빙
        target_file = os.path.normpath(os.path.join(WORKSPACE_ROOT, clean_path.lstrip('/')))
        if target_file.startswith(WORKSPACE_ROOT) and os.path.isfile(target_file):
            mime_type, _ = mimetypes.guess_type(target_file)
            mime_type = mime_type or 'application/octet-stream'
            try:
                with open(target_file, 'rb') as f:
                    file_data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(file_data)
                return
            except Exception as e:
                self.send_error(500, f"Static File Read Error: {e}")
                return

        # 4. 기타 미지원 경로
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # 콘솔 로그 간소화
        pass

socketserver.TCPServer.allow_reuse_address = True

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        pass

def auto_git_sync(workspace_root):
    """정기적으로 최신 시세 스냅샷을 GitHub origin/main에 자동 커밋 및 푸시"""
    import subprocess
    try:
        status = subprocess.run(['git', 'status', '--porcelain', 'assets/market_snapshot.json'], cwd=workspace_root, capture_output=True, text=True, timeout=10)
        if status.stdout.strip():
            subprocess.run(['git', 'add', 'assets/market_snapshot.json'], cwd=workspace_root, check=True, timeout=15)
            subprocess.run(['git', 'commit', '-m', 'chore(market): 자율 감시 엔진 4대 마켓 실시간 스냅샷 자동 동기화'], cwd=workspace_root, check=True, timeout=15)
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=workspace_root, check=True, timeout=30)
            safe_print("[Market Sentinel] GitHub Pages 실시간 자동 동기화 완결")
    except Exception as e:
        safe_print(f"[Market Sentinel] Git 자동 푸시 대기: {e}")

def background_snapshot_updater():
    """백그라운드에서 60초마다 최신 시세를 수집하고 정기적으로 GitHub에 자율 배포"""
    import time
    import datetime
    last_git_push = time.time()
    
    while True:
        try:
            get_all_market_data()
            now = datetime.datetime.now()
            # 30분 주기(1800초) 또는 장 마감 직후(15:35), 장 개장 직후(09:05) 자율 동기화
            is_market_close = (now.hour == 15 and 33 <= now.minute <= 36)
            is_market_open = (now.hour == 9 and 5 <= now.minute <= 8)
            time_elapsed = time.time() - last_git_push
            
            if time_elapsed >= 1800 or ((is_market_close or is_market_open) and time_elapsed >= 300):
                auto_git_sync(WORKSPACE_ROOT)
                last_git_push = time.time()
        except Exception as e:
            safe_print(f"[Market Sentinel Updater Error] {e}")
        time.sleep(60)

def start_server():
    # 백그라운드 자동 스냅샷 갱신 데몬 스레드 가동
    updater = threading.Thread(target=background_snapshot_updater, daemon=True)
    updater.start()

    server_address = ('', PORT)
    with socketserver.TCPServer(server_address, MarketHandler) as httpd:
        safe_print(f"==================================================")
        safe_print(f" [KYANOS] 키아노스 마켓 펄스 실시간 웹 대시보드 구동")
        safe_print(f" 연동 파일: {MARKET_HTML_FILE}")
        safe_print(f" 브라우저 주소: http://localhost:{PORT}")
        safe_print(f"==================================================")
        
        # --no-browser 옵션이 없을 때만 1초 후 브라우저 자동 오픈
        if '--no-browser' not in sys.argv:
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            safe_print("\n서버를 종료합니다.")

if __name__ == '__main__':
    start_server()
