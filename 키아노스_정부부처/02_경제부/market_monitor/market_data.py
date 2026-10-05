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
    """국내 실물 금/은 시세(한국금거래소 살때/팔때) 및 글로벌 국제 시세 통합 수집"""
    results = []
    
    # ── 1. 국내 한국금거래소 공식 고시 시세 (실제 살 때 / 팔 때) ──
    try:
        url_kr = 'https://m.koreagoldx.co.kr/api/main'
        req_kr = urllib.request.Request(url_kr, headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)',
            'Referer': 'https://m.koreagoldx.co.kr/'
        })
        with urllib.request.urlopen(req_kr, timeout=4) as res:
            kdata = json.loads(res.read().decode('utf-8'))
            op = kdata.get('officialPrice4', {})
            
            # ① 순금 24K (3.75g 1돈) 내가 살 때 (소비자 구입가)
            s_pure = op.get('s_pure', 0)
            diff_s = op.get('turm_s_pure', 0)
            rate_s = op.get('per_s_pure', 0.0)
            if s_pure:
                results.append({
                    'category': 'metals_kr',
                    'symbol': '24K-BUY',
                    'name': '순금(24K) 내가 살 때 (1돈)',
                    'price': s_pure,
                    'price_str': f"{s_pure:,.0f}원",
                    'change': diff_s,
                    'change_str': f"{diff_s:+,.0f}원",
                    'change_rate': rate_s,
                    'change_rate_str': f"{rate_s:+.2f}%",
                    'status': 'up' if diff_s > 0 else ('down' if diff_s < 0 else 'flat')
                })
                
            # ② 순금 24K (3.75g 1돈) 내가 팔 때 (금은방 매입가)
            p_pure = op.get('p_pure', 0)
            diff_p = op.get('turm_p_pure', 0)
            rate_p = op.get('per_p_pure', 0.0)
            if p_pure:
                results.append({
                    'category': 'metals_kr',
                    'symbol': '24K-SELL',
                    'name': '순금(24K) 내가 팔 때 (1돈)',
                    'price': p_pure,
                    'price_str': f"{p_pure:,.0f}원",
                    'change': diff_p,
                    'change_str': f"{diff_p:+,.0f}원",
                    'change_rate': rate_p,
                    'change_rate_str': f"{rate_p:+.2f}%",
                    'status': 'up' if diff_p > 0 else ('down' if diff_p < 0 else 'flat')
                })
                
            # ③ 국내 실물 은(Silver 3.75g) 살 때 / 팔 때
            s_silver = op.get('s_silver', 0)
            p_silver = op.get('p_silver', 0)
            diff_silver = op.get('turm_s_silver', 0)
            rate_silver = op.get('per_s_silver', 0.0)
            if s_silver:
                results.append({
                    'category': 'metals_kr',
                    'symbol': 'AG-KR',
                    'name': '실물 은(Silver 3.75g)',
                    'price': s_silver,
                    'price_str': f"살때 {s_silver:,.0f}원",
                    'change': p_silver,
                    'change_str': f"팔때 {p_silver:,.0f}원",
                    'change_rate': rate_silver,
                    'change_rate_str': f"{rate_silver:+.2f}%",
                    'status': 'up' if diff_silver > 0 else ('down' if diff_silver < 0 else 'flat')
                })
                
            # ④ 18K / 14K 금 팔 때
            p_18k = op.get('p_18k', 0)
            p_14k = op.get('p_14k', 0)
            if p_18k and p_14k:
                results.append({
                    'category': 'metals_kr',
                    'symbol': '18K-14K',
                    'name': '18K / 14K 내가 팔 때 (1돈)',
                    'price': p_18k,
                    'price_str': f"18K: {p_18k:,.0f}원",
                    'change': p_14k,
                    'change_str': f"14K: {p_14k:,.0f}원",
                    'change_rate': 0,
                    'change_rate_str': '한국금거래소',
                    'status': 'flat'
                })
    except Exception as e:
        print(f"[Error] KoreaGoldX fetch failed: {e}")
        
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
    return data

if __name__ == '__main__':
    all_data = get_all_market_data()
    print(f"[{all_data['timestamp']}] 시세 수집 완료:")
    for cat in ['crypto', 'domestic', 'global', 'metals']:
        print(f"\n--- {cat.upper()} ---")
        for item in all_data[cat]:
            print(f"{item['name']:<20} | {item['price_str']:>12} | {item['change_rate_str']:>8}")
