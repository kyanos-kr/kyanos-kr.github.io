# git_publisher.py - GitHub Pages 자동 커밋/푸시 모듈
import subprocess
import os
from datetime import datetime

# 레포지토리 최상위 루트 (d:\안티그래비티파이튼)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
OUTPUT_REL = os.path.relpath(OUTPUT_DIR, REPO_ROOT)

def run_git(cmd: list, cwd: str) -> str:
    """git 명령 실행 헬퍼"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        err = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"Git 오류: {err}")
    return (result.stdout or "").strip()

def publish_to_github():
    """
    antnews_auto/output/ 폴더의 변경사항을 GitHub에 자동 커밋·푸시
    사전 조건: 저장소가 이미 git remote origin에 연결되어 있어야 함
    """
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # output 폴더의 변경사항 확인
    status = run_git(["git", "status", "--porcelain", OUTPUT_REL], REPO_ROOT)
    if not status:
        print("  변경사항 없음. 발행 건너뜀.")
        return

    # 스테이징 → 커밋 → 리베이스 풀 → 푸시
    run_git(["git", "add", OUTPUT_REL], REPO_ROOT)
    run_git(["git", "commit", "-m", f"📰 AntNews 자동 업데이트 - {today}"], REPO_ROOT)
    try:
        run_git(["git", "pull", "--rebase", "--autostash"], REPO_ROOT)
    except Exception as e:
        print(f"  [Notice] git pull rebase 알림: {e}")
    run_git(["git", "push", "origin", "main"], REPO_ROOT)
    print(f"  GitHub 푸시 완료: {today}")

if __name__ == "__main__":
    publish_to_github()
