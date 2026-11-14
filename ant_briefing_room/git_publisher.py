# -*- coding: utf-8 -*-
"""
앤트 취재 인텔리전스 브리핑 룸 - GitHub Pages 실시간 배포 모듈
"""
import os
import sys
import subprocess
from datetime import datetime

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRIEFING_REL = "ant_briefing_room"
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from safe_git_sync import sync_and_push


def publish_briefing_to_github():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    pushed = sync_and_push(
        repo_root=REPO_ROOT,
        target_paths=[BRIEFING_REL],
        commit_message=f"📡 AntNews Briefing Room 자동 갱신 ({today})",
    )
    if pushed:
        print(f"  [Git] GitHub Pages 라이브 배포 완료: https://kyanos-kr.github.io/ant_briefing_room/ ({today})")
    else:
        print("  [Git] 브리핑 룸 변경사항 없음. 푸시 생략.")


if __name__ == "__main__":
    publish_briefing_to_github()
