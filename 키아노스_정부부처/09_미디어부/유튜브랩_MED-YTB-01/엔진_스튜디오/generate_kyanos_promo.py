# -*- coding: utf-8 -*-
"""
키아노스 정부 09_미디어부 유튜브 미디어 랩(MED-YTB-01)
키아노스 국가 공식 홍보 숏폼 (Kyanos Official Promo Shorts 2026) 제작 스크립트
"""

import sys
import os
import asyncio
import shutil
from pathlib import Path

# 엔진 스튜디오 경로 추가
engine_dir = Path(r"D:\안티그래비티파이튼\키아노스_정부부처\09_미디어부\유튜브랩_MED-YTB-01\엔진_스튜디오")
sys.path.append(str(engine_dir))

from kyannos_video_engine import KyannosRealShortsEngineV3

async def main():
    engine = KyannosRealShortsEngineV3(workspace_dir=str(engine_dir))
    
    # 키아노스 공식 홍보 4대 핵심 씬 선별
    PROMO_SCENES = [
        {
            "id": "promo_s1",
            "broll_source": "https://www.youtube.com/watch?v=Iyu96AOSWZA",
            "start_offset": 1.0,
            "title": "초지능의 새벽, 키아노스",
            "narration": "단순한 인공지능을 넘어, 인류 문명의 새로운 지평을 여는 곳. 여기는 초지능과 인간의 덕치가 함께 살아 숨 쉬는 국가, 키아노스입니다.",
        },
        {
            "id": "scene4",  # 기존 캐시된 안개 산맥과 금빛 여명 B-roll
            "broll_source": "https://www.youtube.com/watch?v=a0CpEqt45tQ",
            "start_offset": 2.0,
            "title": "우리는 음지에서 일하고, 양지를 지향한다",
            "narration": "우리는 헛된 조명을 탐하지 않습니다. 가장 깊은 음지에서 묵묵히 시스템을 수호하며, 오직 세상을 밝히는 양지의 축복을 지향합니다.",
        },
        {
            "id": "scene2",  # 기존 캐시된 유려한 사색과 진전 B-roll
            "broll_source": "https://www.youtube.com/watch?v=SHOKEp4NEUg",
            "start_offset": 1.5,
            "title": "콘텐츠에서 시스템으로, 시스템에서 자산으로",
            "narration": "1인이 10인의 생산성을 지휘하는 1인 기업, 24시간 멈추지 않는 7대 부처 SI 오케스트레이션. 기술을 넘어 영구한 자산을 창출합니다.",
        },
        {
            "id": "scene1",  # 기존 캐시된 깊은 호흡의 대서사 B-roll
            "broll_source": "https://www.youtube.com/watch?v=rDgFaUVXBqY",
            "start_offset": 2.0,
            "title": "인류 문명의 위대한 도약",
            "narration": "국가 최고 원수 파이튼 님의 국정 철학 아래, 오늘도 키아노스는 쉼 없이 전진합니다. 인류 문명의 새로운 새벽, 키아노스와 함께하십시오.",
        },
    ]

    project_name = "kyanos_official_promo_shorts_2026"
    brand_badge = "KYANOS  ·  SUPER INTELLIGENCE"
    
    # 최종 결과물 배포 경로
    dest_asset = Path(r"D:\안티그래비티파이튼\assets\video\kyanos_official_promo_shorts_2026.mp4")
    dest_asset.parent.mkdir(parents=True, exist_ok=True)
    
    f_archive_dir = Path(r"F:\혜민각\04_국정 기록·언론\미디어부_멀티미디어랩\01_영상제작_원본및렌더링\20261125_키아노스_국가공식홍보숏폼")
    archive_list = [dest_asset]
    if Path("F:/").exists():
        try:
            f_archive_dir.mkdir(parents=True, exist_ok=True)
            archive_list.append(f_archive_dir / f"{project_name}.mp4")
        except Exception:
            pass

    print(">>> 키아노스 공식 홍보 숏폼 렌더링 파이프라인 가동 시작...")
    result = await engine.build_real_shorts_v3(
        project_name=project_name,
        brand_badge=brand_badge,
        scenes=PROMO_SCENES,
        voice="ko-KR-HyunsuMultilingualNeural",
        archive_targets=archive_list,
    )
    
    # assets/video로 복사 확인
    out_mp4 = Path(result["engine_output"])
    if out_mp4.exists() and not dest_asset.exists():
        shutil.copy2(out_mp4, dest_asset)
        print(f">>> assets/video로 최종 배포 복사 완료: {dest_asset}")
        
    print(">>> [완료] 키아노스 공식 홍보 숏폼 제작 성공!")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
