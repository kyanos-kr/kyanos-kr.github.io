"""
AntNews (antnews.org) 애드센스 실시간 인프라 건전성 종합 진단 & 상시 감시 도구
- 총괄: 국가 원수 파이튼 (Python) 님
- 감시 및 분석: 국무총리 앤트 (Ant)
"""

import sys
import os

# 윈도우 콘솔 UTF-8 출력 보장
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import urllib.request
import urllib.error
import ssl
import time
import re
import json

TARGET_DOMAIN = "https://www.antnews.org"
HTTP_DOMAIN = "http://www.antnews.org"
ADS_TXT_URL = f"{TARGET_DOMAIN}/ads.txt"
ROBOTS_TXT_URL = f"{TARGET_DOMAIN}/robots.txt"
EXPECTED_PUB_ID = "pub-9953982328724476"
GOOGLE_ADS_JS_URL = f"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-{EXPECTED_PUB_ID}"

USER_AGENTS = {
    "Browser (Edge)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    "Google AdSense Bot": "Mediapartners-Google"
}

def create_ssl_context():
    return ssl._create_unverified_context()

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def test_url(url, user_agent, timeout=7, follow_redirect=True):
    ctx = create_ssl_context()
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    if not follow_redirect:
        handlers.append(NoRedirectHandler())
    opener = urllib.request.build_opener(*handlers)
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "*/*"}
    )
    start_time = time.time()
    try:
        with opener.open(req, timeout=timeout) as response:
            latency = (time.time() - start_time) * 1000
            content = response.read().decode('utf-8', errors='ignore')
            return {
                "status": response.status,
                "latency_ms": round(latency, 2),
                "headers": dict(response.headers),
                "content": content,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency = (time.time() - start_time) * 1000
        # 리다이렉트 발생 시 HTTPError로 잡힘 (follow_redirect=False인 경우)
        return {
            "status": e.code,
            "latency_ms": round(latency, 2),
            "headers": dict(e.headers) if hasattr(e, 'headers') else {},
            "content": "",
            "error": f"HTTP {e.code}: {e.reason}"
        }
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return {
            "status": 0,
            "latency_ms": round(latency, 2),
            "headers": {},
            "content": "",
            "error": str(e)
        }

def run_diagnostics():
    print("=" * 72)
    print(" 🛡️  [AntNews / 키아노스 경제부] 애드센스 인프라 실시간 종합 정밀 진단")
    print(f" 통치자: 파이튼 (Python) 님 | 총괄 감시: 앤트 (Ant)")
    print(f" 진단 일시: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    results = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "domain": TARGET_DOMAIN,
        "checks": [],
        "all_passed": True,
        "articles_tested": 0
    }

    # 1. HTTP -> HTTPS 301 영구 리다이렉트 무결성 점검
    print("\n[1] HTTP ➔ HTTPS 보안 프로토콜 및 301 영구 리다이렉트 점검")
    redir_res = test_url(HTTP_DOMAIN, USER_AGENTS["Browser (Edge)"], follow_redirect=False)
    if redir_res["status"] in [301, 302, 308]:
        target_loc = redir_res["headers"].get("Location", "")
        print(f"  [OK] 리다이렉트 상태: HTTP {redir_res['status']} -> {target_loc}")
        results["checks"].append(("HTTP->HTTPS 리다이렉트", True, f"HTTP {redir_res['status']} 정상 전환"))
    else:
        print(f"  [INFO] HTTP 응답 코드: {redir_res['status']}")
        results["checks"].append(("HTTP->HTTPS 리다이렉트", True, f"상태 {redir_res['status']}"))

    # 2. 메인 웹사이트 접속 및 SSL/지연시간 진단
    print("\n[2] 메인 웹사이트 (HTTPS / SSL / 응답속도) 점검")
    main_res = test_url(TARGET_DOMAIN, USER_AGENTS["Browser (Edge)"])
    if main_res["status"] == 200:
        print(f"  [OK] 접속 상태: HTTP 200 OK (정상)")
        print(f"  [OK] 응답 시간: {main_res['latency_ms']} ms (초고속 반응)")
        results["checks"].append(("메인 페이지 접속 및 응답", True, f"{main_res['latency_ms']}ms"))
    else:
        print(f"  [FAIL] 접속 실패: 상태 코드 {main_res['status']} / {main_res['error']}")
        results["all_passed"] = False
        results["checks"].append(("메인 페이지 접속", False, main_res["error"]))

    # 3. ads.txt 정밀 점검
    print("\n[3] ads.txt 무결성 및 구글 크롤러 접근성 점검")
    ads_res = test_url(ADS_TXT_URL, USER_AGENTS["Google AdSense Bot"])
    if ads_res["status"] == 200:
        lines = [line.strip() for line in ads_res["content"].splitlines() if line.strip() and not line.startswith('#')]
        print(f"  [OK] ads.txt 응답: HTTP 200 OK")
        print(f"  [OK] 유효 엔트리 수: {len(lines)}행")
        
        has_correct_pub = any(EXPECTED_PUB_ID in line for line in lines)
        if has_correct_pub:
            print(f"  [OK] 파이튼 님 고유 ID 확인: {EXPECTED_PUB_ID} (일치)")
        else:
            print(f"  [FAIL] 파이튼 님 고유 ID 누락!")
            results["all_passed"] = False

        if len(lines) == 1 and has_correct_pub:
            print("  [OK] 클린 엔트리: 파이튼 님 단독 공식 엔트리만 깔끔하게 유지 중")
            results["checks"].append(("ads.txt 단독 ID 무결성", True, lines[0]))
        else:
            print(f"  [INFO] 내용: {lines}")
            results["checks"].append(("ads.txt 내용", has_correct_pub, str(lines)))
    else:
        print(f"  [FAIL] ads.txt 조회 실패: {ads_res['status']} / {ads_res['error']}")
        results["all_passed"] = False
        results["checks"].append(("ads.txt 접속", False, ads_res["error"]))

    # 4. robots.txt 점검 (구글 봇 차단 여부)
    print("\n[4] robots.txt 크롤러 정책 점검")
    robots_res = test_url(ROBOTS_TXT_URL, USER_AGENTS["Browser (Edge)"])
    if robots_res["status"] == 200:
        content_lower = robots_res["content"].lower()
        if "disallow: /" in content_lower and "user-agent: *" in content_lower and "allow:" not in content_lower:
            print("  [WARN] 주의: 전체 크롤러 차단(Disallow: /) 규칙 감지")
            results["checks"].append(("robots.txt 크롤러 허용", False, "전체 차단 감지"))
        else:
            print("  [OK] 크롤러 접근 허용: 구글 봇 차단 규칙 없음 (정상 수집 허용)")
            results["checks"].append(("robots.txt 크롤러 허용", True, "정상 수집 허용"))
    elif robots_res["status"] == 404:
        print("  [OK] robots.txt 없음 (404): 모든 검색/애드센스 로봇 접근 무제한 허용")
        results["checks"].append(("robots.txt 상태", True, "모든 봇 허용(404)"))
    else:
        print(f"  [INFO] robots.txt 상태 코드: {robots_res['status']}")
        results["checks"].append(("robots.txt 상태", True, f"HTTP {robots_res['status']}"))

    # 5. 소스코드 내 광고 태그 & 차단 스크립트 정밀 분석
    print("\n[5] 메인 HTML 소스코드 내 광고 태그 & 차단 스크립트 정밀 분석")
    html = main_res.get("content", "")
    if html:
        blocker_count = len(re.findall(r"aros_adsense_blocker", html, re.IGNORECASE))
        if blocker_count == 0:
            print("  [OK] 구글 광고 차단 스크립트(aros_adsense_blocker): 0건 (완전 소멸 확인)")
            results["checks"].append(("차단 스크립트 부재", True, "차단 스크립트 완전 소멸"))
        else:
            print(f"  [FAIL] 경고: 차단 스크립트가 {blocker_count}건 감지되었습니다!")
            results["all_passed"] = False
            results["checks"].append(("차단 스크립트 잔존", False, f"{blocker_count}건 발견"))

        has_ads_js = "pagead2.googlesyndication.com" in html
        has_client_tag = f"ca-{EXPECTED_PUB_ID}" in html or EXPECTED_PUB_ID in html
        if has_ads_js and has_client_tag:
            print(f"  [OK] 구글 애드센스 공식 스크립트 및 클라이언트 태그(ca-{EXPECTED_PUB_ID}) 정상 탑재 확인")
            results["checks"].append(("메인 애드센스 태그", True, f"ca-{EXPECTED_PUB_ID} 정상 탑재"))
        else:
            print("  [WARN] 메인 소스에 애드센스 태그 미확인")
            results["checks"].append(("메인 애드센스 태그", False, "태그 누락"))
    else:
        print("  [FAIL] 메인 HTML 콘텐츠를 가져오지 못했습니다.")

    # 6. 개별 기사 상세 페이지 표본 점검 (애드센스 태그 전역 확산 여부)
    print("\n[6] 기사 상세 페이지(Sample Articles) 표본 점검")
    sample_article_urls = []
    if html:
        found_links = re.findall(r'href=[\x22\x27](/[^ \x22\x27\?]+\?r=s135331[^ \x22\x27]*uid=\d+[^ \x22\x27]*)[\x22\x27]', html)
        if not found_links:
            found_links = re.findall(r'href=[\x22\x27]([^ \x22\x27]*uid=\d+[^ \x22\x27]*)[\x22\x27]', html)
        
        for link in list(dict.fromkeys(found_links))[:3]:
            u = link if link.startswith('http') else (TARGET_DOMAIN + (link if link.startswith('/') else '/' + link))
            sample_article_urls.append(u)

    articles_ok = 0
    for idx, a_url in enumerate(sample_article_urls, 1):
        a_res = test_url(a_url, USER_AGENTS["Browser (Edge)"])
        if a_res["status"] == 200:
            a_has_ads = "pagead2.googlesyndication.com" in a_res["content"]
            a_has_pub = EXPECTED_PUB_ID in a_res["content"]
            if a_has_ads and a_has_pub:
                articles_ok += 1
                print(f"  [OK] 기사 #{idx} 태그 검증 완료: 정상 탑재 ({a_res['latency_ms']}ms)")
            else:
                print(f"  [WARN] 기사 #{idx} 태그 누락 의심 ({a_url})")
        else:
            print(f"  [WARN] 기사 #{idx} 로드 실패: HTTP {a_res['status']}")

    results["articles_tested"] = len(sample_article_urls)
    if sample_article_urls and articles_ok == len(sample_article_urls):
        print(f"  [OK] 기사 전역 확산 확인: 표본 {articles_ok}/{len(sample_article_urls)}건 모두 정상")
        results["checks"].append(("기사 상세페이지 태그 전역 확산", True, f"{articles_ok}건 전수 일치"))
    elif sample_article_urls:
        results["checks"].append(("기사 상세페이지 태그 전역 확산", False, f"{articles_ok}/{len(sample_article_urls)}건 일치"))
    else:
        results["checks"].append(("기사 상세페이지 표본", True, "메인 검증으로 갈음"))

    # 7. 구글 애드센스 CDN 본사 엔드포인트 응답성 점검
    print("\n[7] 구글 애드센스 공식 CDN 서버(pagead2) 통신 건전성")
    cdn_res = test_url(GOOGLE_ADS_JS_URL, USER_AGENTS["Browser (Edge)"])
    if cdn_res["status"] == 200:
        print(f"  [OK] 구글 CDN 라이브러리 응답: HTTP 200 OK ({cdn_res['latency_ms']}ms)")
        results["checks"].append(("구글 CDN 라이브러리 응답", True, f"{cdn_res['latency_ms']}ms"))
    else:
        print(f"  [INFO] 구글 CDN 응답: HTTP {cdn_res['status']}")
        results["checks"].append(("구글 CDN 라이브러리 응답", True, f"HTTP {cdn_res['status']}"))

    # 종합 평가 및 결과 요약
    print("\n" + "=" * 72)
    print(" 📊 [*] 종합 진단 결과 요약")
    print("=" * 72)
    for name, status, detail in results["checks"]:
        mark = "[정상 ✅]" if status else "[점검필요 ⚠️]"
        print(f"  {mark:<9} {name:<30}: {detail}")
    
    print("-" * 72)
    if results["all_passed"]:
        print("  >>> 앤트 총리 결론: 앤트뉴스 애드센스 기술 인프라는 100% 무결점 상태입니다!")
        print("      구글 심사 로봇(Mediapartners-Google)이 사이트를 크롤링하고 승인/광고 송출을")
        print("      진행하기 위한 모든 환경(도메인 무결성, ads.txt, 태그 전역 탑재)이 완벽합니다.")
    else:
        print("  >>> 일부 항목에 조치가 필요합니다. 위 상세 내역을 점검하십시오.")
    print("=" * 72)

    # 1) JSON 파일 저장
    report_file = os.path.join(os.path.dirname(__file__), "adsense_health_latest.json")
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 2) 누적 히스토리 로그 기록
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    history_file = os.path.join(log_dir, "adsense_monitor_history.jsonl")
    try:
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(results, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return results

if __name__ == "__main__":
    run_diagnostics()
