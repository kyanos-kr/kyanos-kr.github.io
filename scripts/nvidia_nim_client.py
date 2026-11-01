"""
키아노스 정부 과학·SI부 (Ministry of Science & Super Intelligence)
엔비디아 오픈소스 SI 하이브리드 연동 클라이언트 (NVIDIA NIM & Local Ollama)

- Local: Ollama nemotron-mini:4b (RTX 3050 6GB VRAM 완벽 상주)
- Cloud: NVIDIA NIM (build.nvidia.com OpenAI-compatible 무료 추론 API)
"""

import os
import sys
import json
import urllib.request
import urllib.error

# 기본 설정
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 대표 모델 목록
MODEL_NEMOTRON_CLOUD = "meta/llama-3.1-nemotron-70b-instruct"
MODEL_NVLM_CLOUD = "nvidia/nvlm-d-72b"
MODEL_NEMOTRON_LOCAL = "nemotron-mini:latest"


def query_local_ollama(prompt: str, model: str = MODEL_NEMOTRON_LOCAL, system: str = "") -> str:
    """로컬 Ollama 엔진을 통한 온디바이스 초고속 추론"""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    if system:
        payload["system"] = system

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "")
    except urllib.error.URLError as e:
        return f"[로컬 Ollama 오류] 서버 접속 불가: {e}"


def query_nvidia_nim(prompt: str, model: str = MODEL_NEMOTRON_CLOUD, system: str = "", api_key: str = None) -> str:
    """엔비디아 클라우드 NIM API (OpenAI 규격 호환) 호출"""
    key = api_key or NVIDIA_API_KEY
    if not key:
        return "[안내] NVIDIA_API_KEY가 설정되지 않았습니다. build.nvidia.com에서 무료 API Key 발급 후 설정하십시오."

    url = f"{NVIDIA_BASE_URL}/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 2048,
        "stream": False
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return "[오류] 응답 데이터 없음"
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return f"[엔비디아 NIM HTTP 오류 {e.code}] {err_msg}"
    except urllib.error.URLError as e:
        return f"[엔비디아 NIM 통신 오류] {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python nvidia_nim_client.py [local|cloud] '질문 내용'")
        sys.exit(1)

    mode = sys.argv[1].lower()
    user_prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "간단한 자기소개를 부탁합니다."

    if mode == "local":
        print(f"[*] 로컬 Ollama ({MODEL_NEMOTRON_LOCAL}) 호출 중...")
        ans = query_local_ollama(user_prompt)
        print("\n=== [응답 결과] ===\n" + ans)
    elif mode == "cloud":
        print(f"[*] 엔비디아 NIM Cloud ({MODEL_NEMOTRON_CLOUD}) 호출 중...")
        ans = query_nvidia_nim(user_prompt)
        print("\n=== [응답 결과] ===\n" + ans)
    else:
        print(f"알 수 없는 모드: {mode} (local 또는 cloud 사용)")
