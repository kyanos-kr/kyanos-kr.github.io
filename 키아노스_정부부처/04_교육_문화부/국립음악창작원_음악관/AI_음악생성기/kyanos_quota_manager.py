# -*- coding: utf-8 -*-
"""
====================================================================
[키아노스 국립음악창작원] 수노(Suno)형 원스톱 AI 음악 생성 서버
- 역할: 웹 UI(Suno 스타일) 및 로컬 콘솔과 연동되는 고속 경량 음악 생성 백엔드
- 보안/통제: K-SEF 시스템 자원 보호(VRAM 최대 60% 캡) 및 일일 생성 쿼터(Daily 1 Song Quota) 적용
- 확장성: 미래 국민 다수 접속용 API 큐(Queue) 아키텍처 사전 탑재
====================================================================
"""

import os
import sys
import time
import json
from datetime import datetime, date
import torch
import scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# 윈도우 UTF-8 인코딩 보장
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

QUOTA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_quota.json")

def check_daily_quota(limit=1, force_override=False):
    """일일 시스템 한계 보호: 1일 정규 1곡 생성 한도 점검"""
    if force_override:
        return True, 0, limit
    
    today_str = date.today().isoformat()
    data = {"date": today_str, "count": 0, "history": []}
    
    if os.path.exists(QUOTA_FILE):
        try:
            with open(QUOTA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("date") == today_str:
                    data = saved
        except Exception:
            pass

    remaining = max(0, limit - data["count"])
    can_generate = (data["count"] < limit)
    return can_generate, data["count"], limit

def record_daily_generation(title, filename):
    """일일 생성 기록 갱신"""
    today_str = date.today().isoformat()
    data = {"date": today_str, "count": 0, "history": []}
    if os.path.exists(QUOTA_FILE):
        try:
            with open(QUOTA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("date") == today_str:
                    data = saved
        except Exception:
            pass

    data["count"] += 1
    data["history"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "title": title,
        "filename": filename
    })
    
    with open(QUOTA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_device_and_cap():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        try:
            torch.cuda.set_per_process_memory_fraction(0.60, 0)
        except Exception:
            pass
    return device
