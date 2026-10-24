import subprocess

commands = [
    (
        r'D:\b\RPT DB\보도 기사 정보\테슬라_스페이스X_합병_전망_심층분석\테슬라_스페이스X_합병_전망_심층분석.jpg',
        '앤트뉴스 경제부 | M&A ANALYSIS',
        '테슬라·스페이스X 전격 합병설… 월가 AI 시너지 촉각',
        '머스크 \'양사 중첩 영역 확대\' 언급에 초대형 M&A 논의 재점화\\n옵티머스 로봇·스타링크·테라팹 반도체 우주 AI 수직계열화',
        (20, 20, 45), (8, 8, 25), (255, 90, 40)
    ),
    (
        r'D:\b\RPT DB\보도 기사 정보\하버드대_심장_역노화_생체메커니즘_규명\하버드대_심장_역노화_생체메커니즘_규명.jpg',
        '앤트뉴스 과학·SI부 | MEDICAL SCIENCE',
        '하버드대 연구진, 심장·혈관 \'역노화\' 생체 메커니즘 규명',
        'NAD+ 활성화 및 GDF11 조절로 노화 혈관 신생·근육 기능 회복\\n인간 전신 역노화 단초 마련… 퇴행성 심혈관 질환 치료 새 지평',
        (10, 35, 45), (5, 15, 25), (40, 220, 170)
    ),
    (
        r'D:\b\RPT DB\보도 기사 정보\슈퍼인텔리전스_기반_유전체설계_바이오혁신동향_신판\슈퍼인텔리전스_기반_유전체설계_바이오혁신동향.jpg',
        '앤트뉴스 과학·SI부 | SUPER INTELLIGENCE',
        '초지능(SI), 유전체 직접 설계… \'생성형 바이오\' 대혁명',
        '스탠퍼드·아크 \'에보 10G\' 가동… 바이러스 DNA 자율 합성 검증\\n로봇 파운드리 폐쇄루프 연동… 맞춤 신약·생물학적 설계 현실화',
        (25, 15, 45), (10, 5, 25), (200, 100, 255)
    ),
    (
        r'D:\b\RPT DB\보도 기사 정보\후티_사우디_충돌격화와_중동정세_향방\후티_사우디_충돌격화와_중동정세_향방.jpg',
        '앤트뉴스 국제부 | MIDDLE EAST INTELLIGENCE',
        '예멘 후티-사우디 전면 격돌… 중동 안보 질서 격랑',
        '리야드 공항 기습 타격에 대규모 보복 공습… 확전 위기 최고조\\n미 이스라엘·사우디 수교 중재 속 \'팔레스타인 해법\' 최대 걸림돌',
        (40, 20, 15), (20, 10, 5), (255, 180, 50)
    )
]

for idx, (dest, cat, title, sub, top, btm, acc) in enumerate(commands):
    ps_file = f'd:\\안티그래비티파이튼\\temp_render_{idx}.ps1'
    safe_title = title.replace('"', '`"')
    safe_sub = sub.replace('"', '`"').replace('\\n', '`r`n')
    ps_code = f"""
Add-Type -AssemblyName System.Drawing

$width = 640
$height = 360
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

$cTop = [System.Drawing.Color]::FromArgb({top[0]}, {top[1]}, {top[2]})
$cBottom = [System.Drawing.Color]::FromArgb({btm[0]}, {btm[1]}, {btm[2]})
$cAccent = [System.Drawing.Color]::FromArgb({acc[0]}, {acc[1]}, {acc[2]})

$rect = New-Object System.Drawing.Rectangle(0, 0, $width, $height)
$brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $cTop, $cBottom, [System.Drawing.Drawing2D.LinearGradientMode]::ForwardDiagonal)
$g.FillRectangle($brush, $rect)
$brush.Dispose()

$penGrid = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(25, 255, 255, 255), 1)
for ($x = 40; $x -lt $width; $x += 60) {{
    $g.DrawLine($penGrid, $x, 0, $x, $height)
}}
for ($y = 40; $y -lt $height; $y += 60) {{
    $g.DrawLine($penGrid, 0, $y, $width, $y)
}}
$penGrid.Dispose()

$barBrush = New-Object System.Drawing.SolidBrush($cAccent)
$g.FillRectangle($barBrush, 36, 32, 6, 24)
$barBrush.Dispose()

$fontCat = New-Object System.Drawing.Font("Malgun Gothic", 11, [System.Drawing.FontStyle]::Bold)
$fontTitle = New-Object System.Drawing.Font("Malgun Gothic", 18, [System.Drawing.FontStyle]::Bold)
$fontSub = New-Object System.Drawing.Font("Malgun Gothic", 10, [System.Drawing.FontStyle]::Regular)
$fontBrand = New-Object System.Drawing.Font("Malgun Gothic", 9, [System.Drawing.FontStyle]::Bold)

$brushCat = New-Object System.Drawing.SolidBrush($cAccent)
$g.DrawString("{cat}", $fontCat, $brushCat, 50, 34)
$brushCat.Dispose()

$brushBrand = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(180, 255, 255, 255))
$g.DrawString("KYANOS ANTNEWS INTELLIGENCE", $fontBrand, $brushBrand, 410, 36)
$brushBrand.Dispose()

$brushTitle = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$titleRect = New-Object System.Drawing.RectangleF(36, 85, 568, 120)
$formatTitle = New-Object System.Drawing.StringFormat
$g.DrawString("{safe_title}", $fontTitle, $brushTitle, $titleRect, $formatTitle)
$brushTitle.Dispose()

$brushSub = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(215, 225, 235))
$subRect = New-Object System.Drawing.RectangleF(36, 215, 568, 75)
$g.DrawString("{safe_sub}", $fontSub, $brushSub, $subRect, $formatTitle)
$brushSub.Dispose()

$penLine = New-Object System.Drawing.Pen($cAccent, 3)
$g.DrawLine($penLine, 36, 305, 604, 305)
$penLine.Dispose()

$brushFoot = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(160, 180, 200))
$g.DrawString("2026.10.24 | ANTNEWS EDITORIAL REPORT", $fontBrand, $brushFoot, 36, 320)
$g.DrawString("STANDARD 640PX IMAGE", $fontBrand, $brushFoot, 470, 320)
$brushFoot.Dispose()

$fontCat.Dispose()
$fontTitle.Dispose()
$fontSub.Dispose()
$fontBrand.Dispose()
$g.Dispose()

$dest = "{dest}"
$dir = [System.IO.Path]::GetDirectoryName($dest)
if (-not (Test-Path $dir)) {{ New-Item -ItemType Directory -Path $dir -Force | Out-Null }}
$bmp.Save($dest, [System.Drawing.Imaging.ImageFormat]::Jpeg)
$bmp.Dispose()
Write-Host "SUCCESS: $dest"
"""
    with open(ps_file, 'w', encoding='utf-8-sig') as f:
        f.write(ps_code)
    ret = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file])
    print(f"Task {idx} exited with {ret.returncode}")
