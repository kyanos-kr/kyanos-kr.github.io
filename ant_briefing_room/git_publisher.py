# -*- coding: utf-8 -*-
"""
앤트 취재 인텔리전스 브리핑 룸 - GitHub Pages 실시간 배포 모듈
독립 자율 푸시 엔진 (외부 의존성 없음)
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


def run_git(cmd: list, cwd: str) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.returncode != 0:
        err = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"Git 실행 오류: {err}")
    return (result.stdout or "").strip()


def publish_briefing_to_github():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 브리핑 룸 폴더 변경사항 확인
    status = run_git(["git", "status", "--porcelain", BRIEFING_REL], REPO_ROOT)
    if not status:
        print(f"  [Git] 브리핑 룸 변경사항 없음. 푸시 생략. ({today})")
        return

    # 스테이징 -> 커밋 -> 리베이스 풀 -> 원격 푸시 (경합 시 최대 3회 재시도)
    run_git(["git", "add", BRIEFING_REL], REPO_ROOT)
    run_git(["git", "commit", "-m", f"📡 AntNews Briefing Room 자동 갱신 ({today})"], REPO_ROOT)

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            run_git(["git", "pull", "--rebase", "--autostash", "origin", "main"], REPO_ROOT)
        except Exception as e:
            print(f"  [Git Notice] git pull rebase 알림 (시도 {attempt}/{max_retries}): {e}")
        try:
            run_git(["git", "push", "origin", "main"], REPO_ROOT)
            print(f"  [Git] GitHub Pages 라이브 배포 완료: https://kyanos-kr.github.io/ant_briefing_room/ ({today})")
            return
        except RuntimeError as e:
            if attempt == max_retries:
                raise
            print(f"  [Git Retry] 원격 브랜치 경합 감지, 재동기화 후 재시도 ({attempt}/{max_retries}): {e}")


if __name__ == "__main__":
    publish_briefing_to_github()
