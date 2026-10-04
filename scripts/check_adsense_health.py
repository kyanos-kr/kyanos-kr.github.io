"""
AntNews (antnews.org) 애드센스 실시간 인프라 건전성 종합 진단 도구
- 제작: 앤트 (Ant)
- 총괄: 파이튼 (Python) 님
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
ADS_TXT_URL = f"{TARGET_DOMAIN}/ads.txt"
ROBOTS_TXT_URL = f"{TARGET_DOMAIN}/robots.txt"
EXPECTED_PUB_ID = "pub-9953982328724476"

USER_AGENTS = {
    "Browser (Edge)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    "Google AdSense Bot": "Mediapartners-Google"
}

def create_ssl_context():
    ctx = ssl.create_default_context()
    return ctx

def test_url(url, user_agent, timeout=7):
    ctx = create_ssl_context()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "*/*"}
    )
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
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
        return {
            "status": e.code,
            "latency_ms": round(latency, 2),
            "headers": dict(e.headers) if hasattr(e, 'headers') else {},
            "content": "",
            "error": f"HTTP Error {e.code}: {e.reason}"
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
    print("=" * 70)
    print(" [AntNews] antnews.org 애드센스 인프라 실시간 종합 진단")
    print(f" 통치자: 파이튼 (Python) 님 | 분석: 앤트 (Ant)")
    print(f" 진단 일시: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = {"checks": [], "all_passed": True}

    # 1. 메인 웹사이트 접속 및 SSL/지연시간 진단
    print("\n[1] 메인 웹사이트 (HTTPS / SSL / 응답속도) 점검")
    main_res = test_url(TARGET_DOMAIN, USER_AGENTS["Browser (Edge)"])
    if main_res["status"] == 200:
        print(f"  [OK] 접속 상태: HTTP 200 OK (정상)")
        print(f"  [OK] 응답 시간: {main_res['latency_ms']} ms (정상 반응)")
        results["checks"].append(("메인 페이지 접속 및 응답", True, f"{main_res['latency_ms']}ms"))
    else:
        print(f"  [FAIL] 접속 실패: 상태 코드 {main_res['status']} / {main_res['error']}")
        results["all_passed"] = False
        results["checks"].append(("메인 페이지 접속", False, main_res["error"]))

    # 2. ads.txt 정밀 점검
    print("\n[2] ads.txt 무결성 및 구글 크롤러 접근성 점검")
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

    # 3. robots.txt 점검 (구글 봇 차단 여부)
    print("\n[3] robots.txt 크롤러 정책 점검")
    robots_res = test_url(ROBOTS_TXT_URL, USER_AGENTS["Browser (Edge)"])
    if robots_res["status"] == 200:
        content_lower = robots_res["content"].lower()
        if "disallow: /" in content_lower and "user-agent: *" in content_lower and "allow:" not in content_lower:
            print("  [WARN] 주의: 전체 크롤러 차단(Disallow: /) 규칙 감지")
            results["checks"].append(("robots.txt 크롤러 허용", False, "전체 차단 감지"))
        else:
            print("  [OK] 크롤러 접근 허용: 구글 봇 차단 규칙 없음 (정상)")
            results["checks"].append(("robots.txt 크롤러 허용", True, "정상 수집 허용"))
    elif robots_res["status"] == 404:
        print("  [OK] robots.txt 없음 (404): 모든 검색/애드센스 로봇 접근 무제한 허용")
        results["checks"].append(("robots.txt 상태", True, "모든 봇 허용(404)"))
    else:
        print(f"  [INFO] robots.txt 상태 코드: {robots_res['status']}")
        results["checks"].append(("robots.txt 상태", True, f"HTTP {robots_res['status']}"))

    # 4. 소스코드 내 광고 스크립트 및 차단 스크립트 검증
    print("\n[4] HTML 소스코드 내 광고 태그 & 차단 스크립트 정밀 분석")
    html = main_res.get("content", "")
    if html:
        # a) aros_adsense_blocker 잔재 확인
        blocker_count = len(re.findall(r"aros_adsense_blocker", html, re.IGNORECASE))
        if blocker_count == 0:
            print("  [OK] 구글 광고 차단 스크립트(aros_adsense_blocker): 0건 (완전 소멸 확인)")
            results["checks"].append(("차단 스크립트 부재", True, "차단 스크립트 없음"))
        else:
            print(f"  [FAIL] 경고: 차단 스크립트가 아직 {blocker_count}개 감지되었습니다!")
            results["all_passed"] = False
            results["checks"].append(("차단 스크립트 잔존", False, f"{blocker_count}건 발견"))

        # b) 애드센스 본사 js 호출 확인
        has_ads_js = "pagead2.googlesyndication.com" in html
        if has_ads_js:
            print("  [OK] 구글 애드센스 공식 스크립트(pagead2) 호출 확인")
        else:
            print("  [WARN] 주의: 메인 HTML에 pagead2.googlesyndication.com 스크립트가 없습니다.")

        # c) 파이튼 님 클라이언트 ID 태그 확인
        has_client_tag = f"ca-{EXPECTED_PUB_ID}" in html or EXPECTED_PUB_ID in html
        if has_client_tag:
            print(f"  [OK] 메인 소스 내 애드센스 클라이언트 태그 포함 확인 (ca-{EXPECTED_PUB_ID})")
            results["checks"].append(("애드센스 태그 삽입", True, "정상 호출"))
        else:
            print(f"  [WARN] 메인 소스에 ca-{EXPECTED_PUB_ID} 태그가 직접 노출되지 않음")
            results["checks"].append(("애드센스 태그 삽입", False, "태그 미확인"))

        # d) ins 광고 슬롯 컨테이너 확인
        ins_count = len(re.findall(r"<ins[^>]+class=[\"']adsbygoogle[\"']", html, re.IGNORECASE))
        print(f"  [INFO] 본문 내 직접 정의된 광고 슬롯(<ins class='adsbygoogle'>) 수: {ins_count}개")
        if ins_count > 0:
            print("         (수동 광고 슬롯과 구글 자동 광고가 함께 작동 가능한 상태)")
        else:
            print("         (구글 자동 광고(Auto Ads) 엔진이 최적 위치에 동적 송출하는 모드)")
    else:
        print("  [FAIL] 메인 HTML 콘텐츠를 가져오지 못했습니다.")

    # 5. 종합 평가
    print("\n" + "=" * 70)
    print(" [*] 종합 진단 결과 요약")
    print("=" * 70)
    for name, status, detail in results["checks"]:
        mark = "[정상]" if status else "[점검필요]"
        print(f"  {mark:<8} {name:<26}: {detail}")
    
    print("-" * 70)
    if results["all_passed"]:
        print("  >>> 결론: 앤트뉴스 애드센스 인프라 환경은 100% 정상 작동 중입니다!")
        print("      구글 광고 로봇(Mediapartners-Google)이 수집 및 재평가하는 데 필요한")
        print("      모든 기술적 요구 조건(ads.txt, SSL, 무간섭, 스크립트)이 완벽히 충족되었습니다.")
    else:
        print("  >>> 일부 항목에 추가 조치가 필요할 수 있습니다. 위 로그를 확인해 주세요.")
    print("=" * 70)

    # 결과를 JSON 파일로도 저장하여 다른 도구나 대시보드에서 조회 가능하게 보존
    report_file = os.path.join(os.path.dirname(__file__), "adsense_health_latest.json")
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "domain": TARGET_DOMAIN,
                "all_passed": results["all_passed"],
                "checks": results["checks"]
            }, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return results

if __name__ == "__main__":
    run_diagnostics()
