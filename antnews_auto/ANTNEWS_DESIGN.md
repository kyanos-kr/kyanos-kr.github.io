# 📰 AntNews 자동화 시스템 설계

> 설계: 티탄(exaone3.5:2.4b) + 앤트(Claude) | 총괄: 파이튼 님  
> 작성일: 2026-09-30

---

## 1. 전체 아키텍처 (Python 모듈별 역할)

| 모듈 | 파일명 | 역할 |
|------|--------|------|
| **NewsCollector** | `src/collector.py` | RSS 피드 수집, 파싱, 필터링 |
| **NewsSummarizer** | `src/summarizer.py` | Ollama(로컬 AI)로 뉴스 요약 생성 |
| **ReportGenerator** | `src/report_generator.py` | 요약 → HTML 리포트 변환 |
| **GitPublisher** | `src/git_publisher.py` | GitHub Pages에 자동 커밋/푸시 |
| **Main Runner** | `src/main.py` | 전체 파이프라인 실행 진입점 |

## 2. 무료 RSS 뉴스 소스

| 매체 | 분야 | RSS URL |
|------|------|---------|
| BBC News | 글로벌 종합 | https://feeds.bbci.co.uk/news/rss.xml |
| CNN World | 국제 뉴스 | https://rss.cnn.com/rss/edition_world.rss |
| TechCrunch | 테크/스타트업 | https://techcrunch.com/feed/ |
| Reuters Business | 금융/경제 | https://feeds.reuters.com/reuters/businessNews |
| NYT Technology | 기술 심층 | https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml |

## 3. GitHub Actions 스케줄 (매일 오전 6시 KST = 21:00 UTC)

```yaml
# .github/workflows/daily_news.yml
on:
  schedule:
    - cron: '0 21 * * *'  # KST 오전 6시
```

## 4. 단계별 구현 우선순위

| 주차 | 목표 | 완료 기준 |
|------|------|-----------|
| **1주차** | RSS 수집 + Ollama 요약 | 터미널에서 요약 출력 확인 |
| **2주차** | HTML 리포트 생성 | 브라우저에서 리포트 렌더링 |
| **3주차** | GitHub Pages 자동 발행 | antnews.org에 자동 업데이트 |
| **4주차** | GitHub Actions 스케줄 + 안정화 | 무인 자동 실행 72시간 검증 |

## 5. 핵심 설계 결정

- **요약 AI**: Hugging Face 대신 **로컬 Ollama(exaone3.5:2.4b)** 사용 → API 비용 0원
- **스케줄러**: GitHub Actions (무료 2000분/월) 우선, 백업으로 Windows Task Scheduler
- **저장소**: SQLite (로컬 캐시) + GitHub repo (발행 소스)
