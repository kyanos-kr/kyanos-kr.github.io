"""
KYANOS Market Pulse - Market Data Collector
Upbit (Crypto), Naver (Domestic & FX), Yahoo (Global & Tech)
No API keys required. 100% Free & Fast.
"""
import urllib.request
import json
import time
import sys

# UTF-8 stdout configuration
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_crypto_upbit():
    """업비트 원화마켓 주요 코인 시세 조회"""
    markets = [
        ('KRW-BTC', '비트코인', 'BTC'),
        ('KRW-ETH', '이더리움', 'ETH'),
        ('KRW-XRP', '리플', 'XRP'),
        ('KRW-SOL', '솔라나', 'SOL'),
        ('KRW-DOGE', '도지코인', 'DOGE')
    ]
    query = ",".join([m[0] for m in markets])
    url = f"https://api.upbit.com/v1/ticker?markets={query}"
    
    results = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode('utf-8'))
            market_map = {item['market']: item for item in data}
            
            for code, name, symbol in markets:
                item = market_map.get(code)
                if not item:
                    continue
                price = item['trade_price']
                change_rate = item['signed_change_rate'] * 100
                change_price = item['signed_change_price']
                high = item['high_price']
                low = item['low_price']
                vol_24h = item['acc_trade_price_24h']
                
                results.append({
                    'category': 'crypto',
                    'symbol': symbol,
                    'name': name,
                    'price': price,
                    'price_str': f"{price:,.0f}원" if price >= 100 else f"{price:,.2f}원",
                    'change': change_price,
                    'change_str': f"{change_price:+,.0f}원" if abs(change_price) >= 100 else f"{change_price:+,.2f}원",
                    'change_rate': change_rate,
                    'change_rate_str': f"{change_rate:+.2f}%",
                    'high_str': f"{high:,.0f}원",
                    'low_str': f"{low:,.0f}원",
                    'status': 'up' if change_rate > 0 else ('down' if change_rate < 0 else 'flat')
                })
    except Exception as e:
        print(f"[Error] Crypto fetch failed: {e}")
    return results

def fetch_domestic_naver():
    """네이버페이 증권 국내 지수, 주요주 및 환율 조회"""
    indices = [
        ('KOSPI', '코스피', 'index'),
        ('KOSDAQ', '코스닥', 'index'),
        ('005930', '삼성전자', 'stock'),
        ('000660', 'SK하이닉스', 'stock')
    ]
    
    results = []
    # 1. 지수 및 종목
    for code, name, itype in indices:
        try:
            url = f"https://m.stock.naver.com/api/{itype}/{code}/basic"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                price_str = data.get('closePrice', '0')
                clean_price = float(price_str.replace(',', ''))
                change_val = float(str(data.get('compareToPreviousClosePrice', 0)).replace(',', ''))
                rate_val = float(str(data.get('fluctuationsRatio', 0)).replace(',', ''))
                
                results.append({
                    'category': 'domestic',
                    'symbol': code,
                    'name': name,
                    'price': clean_price,
                    'price_str': f"{price_str}원" if itype == 'stock' else f"{price_str}pt",
                    'change': change_val,
                    'change_str': f"{change_val:+,.2f}" if itype == 'index' else f"{change_val:+,.0f}원",
                    'change_rate': rate_val,
                    'change_rate_str': f"{rate_val:+.2f}%",
                    'status': 'up' if rate_val > 0 else ('down' if rate_val < 0 else 'flat')
                })
        except Exception as e:
            print(f"[Error] Domestic {name} failed: {e}")
            
    # 2. 원/달러 환율
    try:
        fx_url = "https://m.stock.naver.com/front-api/marketIndex/prices?category=exchange&reutersCode=FX_USDKRW"
        req = urllib.request.Request(fx_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=4) as res:
            fx_data = json.loads(res.read().decode('utf-8'))
            if fx_data.get('result'):
                row = fx_data['result'][0]
                price_str = row['closePrice']
                clean_price = float(price_str.replace(',', ''))
                change_val = float(row.get('fluctuations', 0))
                rate_val = float(row.get('fluctuationsRatio', 0))
                results.append({
                    'category': 'forex',
                    'symbol': 'USD/KRW',
                    'name': '원/달러 환율',
                    'price': clean_price,
                    'price_str': f"{price_str}원",
                    'change': change_val,
                    'change_str': f"{change_val:+.2f}원",
                    'change_rate': rate_val,
                    'change_rate_str': f"{rate_val:+.2f}%",
                    'status': 'up' if rate_val > 0 else ('down' if rate_val < 0 else 'flat')
                })
    except Exception as e:
        print(f"[Error] FX fetch failed: {e}")
        
    return results

def fetch_global_yahoo():
    """야후 파이낸스 글로벌 지수 및 대표 빅테크 시세 조회"""
    targets = [
        ('^IXIC', '나스닥 종합', '지수'),
        ('^GSPC', 'S&P 500', '지수'),
        ('NVDA', '엔비디아', '미국주식'),
        ('TSLA', '테슬라', '미국주식'),
        ('AAPL', '애플', '미국주식')
    ]
    
    results = []
    for sym, name, itype in targets:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                meta = data['chart']['result'][0]['meta']
                price = meta.get('regularMarketPrice', 0.0)
                prev = meta.get('chartPreviousClose', price)
                diff = price - prev if prev else 0.0
                rate = (diff / prev * 100) if prev else 0.0
                
                results.append({
                    'category': 'global',
                    'symbol': sym.replace('^', ''),
                    'name': name,
                    'price': price,
                    'price_str': f"${price:,.2f}" if itype == '미국주식' else f"{price:,.2f}pt",
                    'change': diff,
                    'change_str': f"${diff:+,.2f}" if itype == '미국주식' else f"{diff:+,.2f}pt",
                    'change_rate': rate,
                    'change_rate_str': f"{rate:+.2f}%",
                    'status': 'up' if rate > 0 else ('down' if rate < 0 else 'flat')
                })
        except Exception as e:
            print(f"[Error] Yahoo {name} failed: {e}")
            
    return results

def fetch_metals(usdkrw=1350.0):
    """국내 실물 금 시세(네이버 금융 공식 연동) 및 글로벌 국제 금/은 시세 통합 수집"""
    results = []
    
    # ── 1. 국내 공식 고시 금 시세 (네이버 금융 공식 연동) ──
    try:
        url_gold = "https://m.stock.naver.com/front-api/marketIndex/prices?category=metals&reutersCode=CMDT_GD"
        req_gold = urllib.request.Request(url_gold, headers=HEADERS)
        with urllib.request.urlopen(req_gold, timeout=4) as res:
            gdata = json.loads(res.read().decode('utf-8'))
            if gdata.get('result'):
                row = gdata['result'][0]
                price_1g = float(row.get('closePrice', '0').replace(',', ''))
                change_1g = float(row.get('fluctuations', '0').replace(',', ''))
                rate_1g = float(row.get('fluctuationsRatio', '0'))
                
                # 1돈(3.75g) 환산 기준
                price_don = price_1g * 3.75
                change_don = change_1g * 3.75
                
                # 내가 살 때 (buyVal 1g -> 1돈)
                buy_val_str = row.get('buyVal', '0').replace(',', '')
                buy_val_don = float(buy_val_str) * 3.75 if buy_val_str else price_don * 1.05
                
                # 내가 팔 때 (sellVal 1g -> 1돈)
                sell_val_str = row.get('sellVal', '0').replace(',', '')
                sell_val_don = float(sell_val_str) * 3.75 if sell_val_str else price_don * 0.95
                
                results.append({
                    'category': 'metals_kr',
                    'symbol': '24K-BUY',
                    'name': '국내 순금(24K) 살 때 (1돈)',
                    'price': buy_val_don,
                    'price_str': f"{buy_val_don:,.0f}원",
                    'change': change_don,
                    'change_str': f"{change_don:+,.0f}원",
                    'change_rate': rate_1g,
                    'change_rate_str': f"{rate_1g:+.2f}%",
                    'status': 'up' if change_1g > 0 else ('down' if change_1g < 0 else 'flat')
                })
                
                results.append({
                    'category': 'metals_kr',
                    'symbol': '24K-SELL',
                    'name': '국내 순금(24K) 팔 때 (1돈)',
                    'price': sell_val_don,
                    'price_str': f"{sell_val_don:,.0f}원",
                    'change': change_don,
                    'change_str': f"{change_don:+,.0f}원",
                    'change_rate': rate_1g,
                    'change_rate_str': f"{rate_1g:+.2f}%",
                    'status': 'up' if change_1g > 0 else ('down' if change_1g < 0 else 'flat')
                })
    except Exception as e:
        print(f"[Warning] Naver Gold fetch failed: {e}")
        
    # ── 2. 글로벌 국제 선물 시세 (COMEX) ──
    targets = [
        ('GC=F', '국제 금 선물 (COMEX)', 'USD/oz'),
        ('SI=F', '국제 은 선물 (COMEX)', 'USD/oz')
    ]
    gold_usd = 0.0
    silver_usd = 0.0
    
    for sym, name, unit in targets:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode('utf-8'))
                meta = data['chart']['result'][0]['meta']
                price = meta.get('regularMarketPrice', 0.0)
                prev = meta.get('chartPreviousClose', price)
                diff = price - prev if prev else 0.0
                rate = (diff / prev * 100) if prev else 0.0
                
                if sym == 'GC=F':
                    gold_usd = price
                elif sym == 'SI=F':
                    silver_usd = price
                    
                results.append({
                    'category': 'metals_global',
                    'symbol': sym.replace('=F', ''),
                    'name': name,
                    'price': price,
                    'price_str': f"${price:,.2f}",
                    'change': diff,
                    'change_str': f"${diff:+,.2f}",
                    'change_rate': rate,
                    'change_rate_str': f"{rate:+.2f}%",
                    'status': 'up' if rate > 0 else ('down' if rate < 0 else 'flat')
                })
        except Exception as e:
            print(f"[Error] Global metals {name} failed: {e}")
            
    # ⑤ 금/은 비율 (Gold-Silver Ratio)
    if gold_usd > 0 and silver_usd > 0:
        ratio = gold_usd / silver_usd
        results.append({
            'category': 'metals_global',
            'symbol': 'GSR',
            'name': '금/은 교환비율 (GSR)',
            'price': ratio,
            'price_str': f"{ratio:.2f}배",
            'change': 0,
            'change_str': '국제 자산배분',
            'change_rate': 0,
            'change_rate_str': '적정 60~80',
            'status': 'flat'
        })
        
    return results

def get_all_market_data():
    """모든 시장 시세 수집 및 통일 포맷 반환"""
    domestic_data = fetch_domestic_naver()
    
    # 환율 추출
    usdkrw_val = 1350.0
    for item in domestic_data:
        if item.get('symbol') == 'USD/KRW':
            usdkrw_val = item.get('price', 1350.0)
            break
            
    data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'crypto': fetch_crypto_upbit(),
        'domestic': domestic_data,
        'global': fetch_global_yahoo(),
        'metals': fetch_metals(usdkrw_val)
    }

    # 스냅샷 자동 저장 (정적 브라우저 열람 및 깃허브 배포 동기화)
    try:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        snapshot_path = os.path.join(root_dir, "assets", "market_snapshot.json")
        if os.path.exists(os.path.dirname(snapshot_path)):
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Warning] Snapshot auto-save failed: {e}")

    return data

if __name__ == '__main__':
    all_data = get_all_market_data()
    print(f"[{all_data['timestamp']}] 시세 수집 완료:")
    for cat in ['crypto', 'domestic', 'global', 'metals']:
        print(f"\n--- {cat.upper()} ---")
        for item in all_data[cat]:
            print(f"{item['name']:<20} | {item['price_str']:>12} | {item['change_rate_str']:>8}")
