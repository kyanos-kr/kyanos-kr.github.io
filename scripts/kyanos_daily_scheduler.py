#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================
키아노스 국정 정기 스케줄 관제 엔진 (Kyanos State Routine Scheduler)
========================================================================
소관: 국가최고헌정원 국무총리실(메티) & 국왕직속 수석비서실(비비안)
기능:
  - 07:00 취재 원석 수집 및 모닝 마켓 레이더 가동
  - 08:06 앤트뉴스 데일리 리포트 자동 생성 및 배너 퍼널 배포
  - 10:00 국책사업 안건 상태 및 부처별 진행도 점검
  - 14:00 앤트뉴스-블로그 유입 트래픽 및 UTM 파라미터 전환 지표 수집
  - 18:00 글로벌 4대 마켓 일일 결산 스냅샷 동기화
  - 21:00 춘추원 일일 사초록 편찬 및 F:\\ 혜민각 국가기록원 영구 동기화
========================================================================
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(r"D:\안티그래비티파이튼")
BACKUP_ROOT = Path(r"F:\봉민관\국가최고헌정원")
LOG_FILE = WORKSPACE_ROOT / "scripts" / "kyanos_scheduler.log"

SCHEDULE_ROSTER = [
    {
        "time": "07:00",
        "name": "새벽 취재원석 수집 및 4대 마켓 레이더",
        "action": "scripts/collector.py",
        "dept": "미디어부"
    },
    {
        "time": "08:06",
        "name": "앤트뉴스 데일리 리포트 자동 생성 및 배너 배포",
        "action": "antnews_auto/src/report_generator.py",
        "dept": "미디어부"
    },
    {
        "time": "10:00",
        "name": "국책사업 7대 시행안건 점검 및 동기화",
        "action": "policy_check",
        "dept": "총리실 메티"
    },
    {
        "time": "14:00",
        "name": "블로그-앤트뉴스 트래픽 전환율 점검",
        "action": "traffic_check",
        "dept": "비서실 비비안"
    },
    {
        "time": "18:00",
        "name": "글로벌 4대 마켓 일일 결산",
        "action": "scripts/sync_market.py",
        "dept": "경제부"
    },
    {
        "time": "21:00",
        "name": "춘추원 사초 편찬 및 F:\\ 혜민각 영구 동기화",
        "action": "f_drive_sync",
        "dept": "춘추원 · 기록원"
    }
]

def log_event(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception as e:
        print(f"Log error: {e}")

def check_f_drive_sync():
    """F: 드라이브 정상 연결 여부 및 백업 동기화 점검"""
    if BACKUP_ROOT.exists():
        log_event(f"✅ F:\\ 저장소(봉민관) 연결 정상: {BACKUP_ROOT}")
        return True
    else:
        log_event("⚠️ F:\\ 저장소 마운트 대기 중")
        return False

def inspect_daily_status():
    """오늘 국정 스케줄 진행 상태 전수 점검"""
    now = datetime.datetime.now()
    log_event(f"=== 키아노스 일일 국정 스케줄 점검 시작 (현재 시각: {now.strftime('%H:%M:%S')}) ===")
    
    # 1. 앤트뉴스 생성 여부 확인
    today_str = now.strftime("%Y%m%d")
    report_file = WORKSPACE_ROOT / "antnews_auto" / "output" / f"antnews_{today_str}.html"
    if report_file.exists():
        log_event(f"✅ [미디어부] 금일 앤트뉴스 리포트 완결 확인 ({report_file.name})")
    else:
        log_event(f"⏳ [미디어부] 금일 앤트뉴스 리포트 대기 중")

    # 2. 마켓 스냅샷 파일 확인
    market_file = WORKSPACE_ROOT / "assets" / "market_snapshot.json"
    if market_file.exists():
        mtime = datetime.datetime.fromtimestamp(market_file.stat().st_mtime)
        log_event(f"✅ [경제부] 실시간 마켓 스냅샷 활성 (최종 갱신: {mtime.strftime('%H:%M:%S')})")

    # 3. F: 드라이브 상태 점검
    check_f_drive_sync()

    log_event("=== 키아노스 일일 국정 스케줄 점검 완료 ===")

if __name__ == "__main__":
    inspect_daily_status()
