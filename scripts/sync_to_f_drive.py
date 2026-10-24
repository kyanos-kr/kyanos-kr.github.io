import os
import subprocess
import sys

def main():
    print("=" * 60)
    print("  [키아노스 국정 데이터 F: 드라이브 스마트 증분 백업 가동]")
    print("=" * 60)

    tasks = [
        ("1. RPT DB 보도기사 완제품 백업", r"D:\DATA CENTER\RPT DB", r"F:\02_보도기사_데이터아카이브\RPT DB", False),
        ("2. 편집 기사 작업실 백업", r"D:\DATA CENTER\편집 기사", r"F:\02_보도기사_데이터아카이브\편집 기사", False),
        ("3. 안티그래비티 국정 엔진룸 백업", r"D:\안티그래비티파이튼", r"F:\00_키아노스_국가기록보관소\안티그래비티파이튼", True),
    ]

    for title, src, dst, exclude_git in tasks:
        print(f"\n>> {title} 중...")
        if not os.path.exists(src):
            print(f"   [경고] 원본 경로가 없습니다: {src}")
            continue

        os.makedirs(dst, exist_ok=True)
        cmd = ["robocopy", src, dst, "/E", "/XO", "/R:1", "/W:1", "/NP", "/NFL", "/NDL"]
        if exclude_git:
            cmd.extend(["/XD", ".git", "__pycache__"])

        # robocopy exit codes 0-7 are success
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode <= 7:
            print(f"   [성공] 동기화 완료: {dst}")
        else:
            print(f"   [주의] 결과 코드 {res.returncode}")

    print("\n" + "=" * 60)
    print("  [완료] 모든 핵심 데이터가 F: 드라이브로 안전 동기화되었습니다!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
