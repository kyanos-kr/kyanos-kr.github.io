# youtube_shorts_generator.py
"""
프로젝트: 키아노스 유튜브 쇼츠 자동 제작
목표: 매일 최신 키아노스 뉴스·시장 동향을 60초 이하 영상으로 자동 생성·업로드
핵심 흐름:
1️⃣ 데이터 수집 – market_monitor/market_data.py 로부터 최신 티커·뉴스 요약
2️⃣ 텍스트 요약 – OpenAI/Gemma 로 간결한 스크립트 생성 (max 150 words)
3️⃣ 영상 합성 – ffmpeg + 이미지·그래프 자동 레이어링
   - 배경: assets/posters/kyanos_official_poster_kr.png
   - 로고·아이콘: assets/banners/kyanos_780x240.png
   - 차트: generate_chart.py (별도 구현) 로 생성된 PNG 삽입
4️⃣ 음성 합성 – Microsoft Edge TTS (ko-KR) 로 나레이션 파일 생성
5️⃣ 최종 인코딩 – 1080p, 30fps, H.264, 5 MB 이하 목표
6️⃣ 업로드 – YouTube Data API v3 (OAuth2) 사용, "키아노스 쇼츠" 재생목록에 자동 추가

※ 현재 스케치 단계이며, 실제 API 키·OAuth 토큰은 별도 보안 파일(.env) 에서 로드합니다.
"""

import os, json, subprocess, datetime

def load_market_snapshot():
    # 간단히 market_data 모듈을 호출해 최신 데이터를 JSON 파일로 저장한다고 가정
    snapshot_path = os.path.abspath('../market_monitor/market_snapshot.json')
    if not os.path.exists(snapshot_path):
        raise FileNotFoundError('Market snapshot not found')
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_script(data):
    # 여기서는 Ollama 로컬 LLM을 호출해 요약 스크립트를 만든다 (예시 명령)
    prompt = f"다음 시장 데이터와 주요 뉴스 요약을 바탕으로 60초 이내 유튜브 쇼츠 스크립트를 한국어로 작성해 주세요. 최대 150단어, 친근하고 흥미로운 어조로.\n\nData: {json.dumps(data, ensure_ascii=False)}"
    # 실제 호출은 ollama_generate 툴을 이용해야 함. 여기선 placeholder 반환.
    return "[스크립트 예시] 오늘의 키아노스 시장 요약..."

def synthesize_audio(script_text, out_path):
    # Edge TTS 사용 예시 (powershell 명령) – 실제 구현 시 별도 함수로 호출
    cmd = f"powershell -Command \"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SelectVoice('Microsoft Heami Desktop'); $s.Rate = -1; $s.Volume = 100; $s.SpeakToWaveFile('{script_text}', '{out_path}')\""
    subprocess.run(cmd, shell=True, check=True)

def render_video(script, audio_path, output_path):
    # ffmpeg 로 영상·오디오 합성 (배경 이미지, 텍스트 오버레이, 차트 등)
    bg_image = os.path.abspath('../assets/posters/kyanos_official_poster_kr.png')
    cmd = [
        'ffmpeg', '-y', '-loop', '1', '-i', bg_image,
        '-i', audio_path,
        '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-pix_fmt', 'yuv420p', output_path
    ]
    subprocess.run(cmd, check=True)

def upload_to_youtube(video_path, title, description):
    # 실제 업로드는 google-auth, google-api-python-client 이용해 구현
    pass

def main():
    data = load_market_snapshot()
    script = generate_script(data)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    audio_file = f'yt_shorts_{timestamp}.wav'
    video_file = f'yt_shorts_{timestamp}.mp4'
    synthesize_audio(script, audio_file)
    render_video(script, audio_file, video_file)
    upload_to_youtube(video_file, f'키아노스 오늘의 시장 요약 {timestamp}', script)

if __name__ == '__main__':
    main()
