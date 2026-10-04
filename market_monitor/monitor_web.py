"""
KYANOS Market Pulse - Realtime Web Dashboard
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

# UTF-8 stdout configuration
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from market_data import get_all_market_data

PORT = 8899

HTML_PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>키아노스 마켓 펄스 | KYANOS Market Pulse</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Pretendard:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --card-border: #1f2937;
            --text-main: #f9fafb;
            --text-sub: #9ca3af;
            --up-color: #ef4444;      /* 한국형 상승: 빨강 */
            --down-color: #3b82f6;    /* 한국형 하락: 파랑 */
            --flat-color: #9ca3af;
            --accent-cyan: #06b6d4;
            --accent-gold: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
            padding: 24px 20px;
            min-height: 100vh;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1300px;
            margin: 0 auto 24px auto;
            padding-bottom: 16px;
            border-bottom: 1px solid #1f2937;
        }

        .brand-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .pulse-badge {
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            color: white;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
            padding: 4px 10px;
            border-radius: 20px;
            text-transform: uppercase;
        }

        .title-text {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .title-sub {
            color: var(--text-sub);
            font-size: 13px;
            font-weight: 400;
            margin-left: 6px;
        }

        .status-bar {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 13px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-sub);
        }

        .live-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #10b981;
            box-shadow: 0 0 10px #10b981;
            display: inline-block;
            animation: blink 1.5s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px;
            max-width: 1300px;
            margin: 0 auto;
        }

        .category-panel {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }

        .panel-header {
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .panel-title {
            font-size: 15px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .panel-badge {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-sub);
            font-family: 'JetBrains Mono', monospace;
        }

        .item-list {
            list-style: none;
        }

        .item-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #1a2233;
            transition: background-color 0.2s;
        }

        .item-row:last-child {
            border-bottom: none;
        }

        .item-row:hover {
            background-color: rgba(255, 255, 255, 0.03);
        }

        .item-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .item-name {
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
        }

        .item-symbol {
            font-size: 12px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-sub);
        }

        .item-price-box {
            text-align: right;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        .item-price {
            font-size: 16px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.3px;
            transition: color 0.3s;
        }

        .item-change {
            font-size: 12px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 6px;
        }

        .tag-rate {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
        }

        .up {
            color: var(--up-color);
        }
        .up .tag-rate {
            background: rgba(239, 68, 68, 0.15);
            color: var(--up-color);
        }

        .down {
            color: var(--down-color);
        }
        .down .tag-rate {
            background: rgba(59, 130, 246, 0.15);
            color: var(--down-color);
        }

        .flat {
            color: var(--flat-color);
        }
        .flat .tag-rate {
            background: rgba(156, 163, 175, 0.15);
            color: var(--flat-color);
        }

        .footer {
            max-width: 1300px;
            margin: 28px auto 0 auto;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 14px;
            border-top: 1px solid #1f2937;
        }

        /* 펄스 애니메이션 (가격 변동 시 번쩍임) */
        @keyframes flashUp {
            0% { background-color: rgba(239, 68, 68, 0.3); }
            100% { background-color: transparent; }
        }
        @keyframes flashDown {
            0% { background-color: rgba(59, 130, 246, 0.3); }
            100% { background-color: transparent; }
        }
        .flash-up { animation: flashUp 0.8s ease-out; }
        .flash-down { animation: flashDown 0.8s ease-out; }
    </style>
</head>
<body>
    <header class="header">
        <div class="brand-title">
            <span class="pulse-badge">KYANOS PULSE</span>
            <span class="title-text">실시간 시세 인텔리전스</span>
            <span class="title-sub">키아노스 제국 금융 센터</span>
        </div>
        <div class="status-bar">
            <span><span class="live-dot"></span> LIVE 4초 갱신</span>
            <span id="update-time">동기화 중...</span>
        </div>
    </header>

    <main class="grid-container">
        <!-- 1. 암호화폐 -->
        <section class="category-panel">
            <div class="panel-header">
                <div class="panel-title">🪙 주요 암호화폐 (업비트)</div>
                <div class="panel-badge">UPBIT KRW</div>
            </div>
            <ul class="item-list" id="crypto-list">
                <li class="item-row"><div class="item-info">데이터 로딩 중...</div></li>
            </ul>
        </section>

        <!-- 2. 국내 증시 및 환율 -->
        <section class="category-panel">
            <div class="panel-header">
                <div class="panel-title">📈 국내 증시 & 환율 (네이버)</div>
                <div class="panel-badge">KRX / FX</div>
            </div>
            <ul class="item-list" id="domestic-list">
                <li class="item-row"><div class="item-info">데이터 로딩 중...</div></li>
            </ul>
        </section>

        <!-- 3. 글로벌 증시 및 테크 -->
        <section class="category-panel">
            <div class="panel-header">
                <div class="panel-title">🌐 글로벌 증시 & 빅테크 (야후)</div>
                <div class="panel-badge">US MARKETS</div>
            </div>
            <ul class="item-list" id="global-list">
                <li class="item-row"><div class="item-info">데이터 로딩 중...</div></li>
            </ul>
        </section>

        <!-- 4. 귀금속 & 현물 원자재 -->
        <section class="category-panel">
            <div class="panel-header">
                <div class="panel-title">🥇 귀금속 시세 (국내 살때·팔때 & 국제)</div>
                <div class="panel-badge">금거래소 / COMEX</div>
            </div>
            <ul class="item-list" id="metals-list">
                <li class="item-row"><div class="item-info">데이터 로딩 중...</div></li>
            </ul>
        </section>
    </main>

    <footer class="footer">
        <div>키아노스 앤트 인텔리전스 | KYANOS Ant Intelligence Engine</div>
        <div>100% 무료 무과금 공개 API 연동 | Zero-Cost Real-Time Monitor</div>
    </footer>

    <script>
        const oldPrices = {};

        function renderItems(containerId, items) {
            const container = document.getElementById(containerId);
            if (!items || items.length === 0) return;

            let html = '';
            for (const item of items) {
                const statusClass = item.status === 'up' ? 'up' : (item.status === 'down' ? 'down' : 'flat');
                const sign = item.change_rate > 0 ? '▲ ' : (item.change_rate < 0 ? '▼ ' : '- ');
                
                // 가격 변동 플래시 효과 체크
                const prevPrice = oldPrices[item.symbol];
                let flashClass = '';
                if (prevPrice !== undefined) {
                    if (item.price > prevPrice) flashClass = 'flash-up';
                    else if (item.price < prevPrice) flashClass = 'flash-down';
                }
                oldPrices[item.symbol] = item.price;

                html += `
                    <li class="item-row ${flashClass}">
                        <div class="item-info">
                            <span class="item-name">${item.name}</span>
                            <span class="item-symbol">${item.symbol}</span>
                        </div>
                        <div class="item-price-box ${statusClass}">
                            <span class="item-price">${item.price_str}</span>
                            <div class="item-change">
                                <span>${item.change_str}</span>
                                <span class="tag-rate">${sign}${item.change_rate_str}</span>
                            </div>
                        </div>
                    </li>
                `;
            }
            container.innerHTML = html;
        }

        async function fetchMarket() {
            try {
                const res = await fetch('/api/market');
                if (!res.ok) throw new Error('Network error');
                const data = await res.json();

                document.getElementById('update-time').innerText = '기준: ' + data.timestamp;
                renderItems('crypto-list', data.crypto);
                renderItems('domestic-list', data.domestic);
                renderItems('global-list', data.global);
                renderItems('metals-list', data.metals);
            } catch (err) {
                console.error('Fetch error:', err);
                document.getElementById('update-time').innerText = '갱신 일시 오류 (재시도 중)';
            }
        }

        // 초기 실행 및 4초 주기 갱신
        fetchMarket();
        setInterval(fetchMarket, 4000);
    </script>
</body>
</html>
"""

class MarketHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/api/market':
            data = get_all_market_data()
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # 콘솔 로그 간소화
        pass

def start_server():
    server_address = ('', PORT)
    with socketserver.TCPServer(server_address, MarketHandler) as httpd:
        print(f"==================================================")
        print(f" [KYANOS] 키아노스 마켓 펄스 실시간 웹 대시보드 구동")
        print(f" 브라우저 주소: http://localhost:{PORT}")
        print(f" 종료하려면 터미널에서 Ctrl+C 를 누르세요.")
        print(f"==================================================")
        
        # 1초 후 브라우저 자동 오픈
        threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")

if __name__ == '__main__':
    start_server()
