"""5월의 사랑 - 기타 반주 가이드 트랙 생성기 (Karplus-Strong 기타 합성, C Major, 96 BPM)
보컬 없는 반주 데모입니다. 실제 보컬곡은 수노(유료 플랜) 또는 녹음으로 제작합니다."""
import sys
import numpy as np
import wave

SR = 44100
BPM = 96
EIGHTH = 60.0 / BPM / 2

CH = {
    "C":   [48, 52, 55, 60, 64],
    "G/B": [47, 55, 59, 62, 67],
    "Am":  [45, 52, 57, 60, 64],
    "Em7": [40, 47, 50, 55, 59, 64],
    "F":   [53, 57, 60, 64],
    "C/E": [40, 48, 52, 55, 60, 64],
    "Dm7": [50, 57, 60, 65],
    "G":   [43, 47, 50, 55, 59, 67],
    "Gs4": [43, 48, 50, 55, 60, 67],
    "Em":  [40, 47, 52, 55, 59, 64],
    "C7":  [48, 52, 58, 60, 64],
}

INTRO = ["C", "G/B", "Am", "Em7", "F", "C/E", "Dm7", "Gs4"]
VERSE = ["C", "G/B", "Am", "Em7", "F", "C/E", "Dm7", "G"] * 1 + ["C", "G/B", "Am", "Em7", "F", "C/E", "Dm7", "Gs4"]
CHORUS = ["F", "G", "Em7", "Am", "F", "G", "C", "C", "F", "G", "Em7", "Am", "Dm7", "G", "C", "Gs4"]
BRIDGE = ["Am", "Em", "F", "G", "F", "G", "Am", "Gs4"]
OUTRO = ["F", "C/E", "Dm7", "G", "C", "C"]

# 각 코드 = 1/2마디 (4 eighth → 2박) 로 배치: 코드당 4 eighth notes
SONG = (INTRO + VERSE[:8] + VERSE[8:] + CHORUS + VERSE[:8] + VERSE[8:] + CHORUS + BRIDGE + CHORUS + OUTRO)


def pluck(midi, dur, vel=0.5):
    f = 440.0 * 2 ** ((midi - 69) / 12.0)
    n = int(SR * dur)
    N = int(SR / f)
    y = np.zeros(n + N)
    rng = np.random.default_rng(midi)
    y[:N] = (rng.random(N) - 0.5) * 2
    for i in range(N, n + N, N):
        blk = y[i - N:i]
        prev = np.concatenate(([blk[0]], blk[:-1]))
        y[i:i + N] = (0.5 * (blk + prev) * 0.996)[: len(y[i:i + N])]
    y = y[:n]
    env = np.minimum(1, np.arange(n) / (0.003 * SR)) * np.exp(-np.arange(n) / (SR * dur * 0.9))
    return y * env * vel


def render():
    total = len(SONG) * 4 * EIGHTH + 4
    out = np.zeros(int(SR * total))
    t = 0.0
    pat = [0, 2, 3, 2]
    pat2 = [1, 2, 3, 2]
    for ci, name in enumerate(SONG):
        notes = CH[name]
        chorus_like = False
        for k in range(4):
            idx = (pat if ci % 2 == 0 else pat2)[k]
            idx = min(idx, len(notes) - 1)
            m = notes[0] if k == 0 else notes[idx]
            v = 0.55 if k == 0 else 0.4
            # 베이스 + 위쪽 음 함께
            s = pluck(m, 1.6, v)
            if k == 0:
                s = s[:]  # 첫 박에 코드 윗음 한 번 더 얹음
                top = pluck(notes[-1], 1.4, 0.28)
                s[: len(top)] += top
            st = int(SR * (t + k * EIGHTH))
            out[st:st + len(s)] += s[: len(out) - st]
        t += 4 * EIGHTH
    # 간단 리버브(딜레이 2탭)
    for d, g in ((0.09, 0.25), (0.17, 0.15)):
        sh = int(SR * d)
        out[sh:] += out[:-sh] * g
    out /= max(1e-9, np.abs(out).max())
    out *= 0.85
    fade = int(SR * 3)
    out[-fade:] *= np.linspace(1, 0, fade)
    return (out * 32767).astype(np.int16)


if __name__ == "__main__":
    dst = sys.argv[1]
    data = render()
    with wave.open(dst, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("saved", dst, len(data) / SR, "sec")
