# main.py - AntNews 자동화 파이프라인 메인 실행 파일
# 실행 순서: 수집 → 요약 → HTML 생성 → Git 발행
import sys
import os
from datetime import datetime

# 모듈 경로 설정
sys.path.insert(0, os.path.dirname(__file__))

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from collector import fetch_rss_feeds
from summarizer import summarize_articles
from report_generator import generate_report
from git_publisher import publish_to_github

def run_pipeline():
    print("=" * 60)
    print(f"📰 AntNews 파이프라인 시작: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1단계: 키아노스 공식 의제 및 오픈 지표 수집
    print("\n[1/4] 키아노스 공식 의제 및 오픈 지표 수집 중 (저작권 침해 0%)...")
    articles = fetch_rss_feeds()
    if not articles:
        print("[ERROR] 편성된 의제가 없습니다. 종료합니다.")
        sys.exit(1)
    print(f"  → 총 {len(articles)}건 편성 완료")

    # 2단계: 앤트(Ant) 독자 인텔리전스 및 전략 논평 생성
    print(f"\n[2/4] 앤트(Ant) 오리지널 인텔리전스 집필 중 ({len(articles)}건)...")
    summarized = summarize_articles(articles)
    print(f"  → 집필 완료")

    # 3단계: HTML 리포트 생성
    print("\n[3/4] HTML 리포트 생성 중...")
    output_path = generate_report(summarized)
    print(f"  → 생성 완료: {output_path}")

    # 4단계: GitHub Pages 발행
    print("\n[4/4] GitHub Pages 발행 중...")
    try:
        publish_to_github()
        print("  → 발행 완료!")
    except Exception as e:
        print(f"  → [WARNING] Git 발행 실패 (로컬 파일은 생성됨): {e}")

    print("\n" + "=" * 60)
    print("✅ AntNews 파이프라인 완료!")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
