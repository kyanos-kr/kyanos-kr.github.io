# 키아노스 Blogger 자동 업로드 도구

`blogger_upload.ps1` — 앤트가 3대 블로그 중 구글 블로그 2곳(초지능 미래 오디세이 · Ant-Travel Korea)에 원고를 직접 올리는 도구.

## 운영 원칙
- **기본은 초안 저장**: 업로드하면 블로거에 '임시저장 초안'으로 들어가고, 파이튼 님이 블로거 화면에서 바로 미리보기할 수 있다.
- **발행은 승인 후에만**: 파이튼 님 승인 뒤에만 `-Publish`로 발행한다. 원고 주석에 `승인 대기`가 남아 있으면 도구가 발행을 거부한다.
- **인증 정보는 저장소 밖에 보관**: `%USERPROFILE%\.kyanos_blogger\` (`client_secret.json`, `token.json`). GitHub에는 절대 올리지 않는다.

## 최초 1회 설정 (파이튼 님, 약 5분)
1. https://console.cloud.google.com 접속 → 상단에서 **새 프로젝트** 만들기 (예: `Kyanos-Blogger`)
2. **API 및 서비스 → 라이브러리** → `Blogger API v3` 검색 → **사용**
3. **OAuth 동의 화면** → 사용자 유형 **외부** → 앱 이름·이메일 입력 후 저장
   - **게시 상태를 '프로덕션으로 푸시'** 해 둔다. 테스트 상태로 두면 인증이 **7일마다 만료**된다.
   - 로그인 시 "확인되지 않은 앱" 경고가 나오면 **고급 → (앱 이름)으로 이동**을 누르면 된다. (본인 전용 앱이라 안전)
4. **사용자 인증 정보 → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID** → 애플리케이션 유형 **데스크톱 앱** → 만들기
5. **JSON 다운로드** → 파일 이름을 `client_secret.json`으로 바꿔 `%USERPROFILE%\.kyanos_blogger\` 폴더에 넣는다.
6. 앤트에게 "인증 진행해"라고 말씀하시면 앤트가 `-Init`을 실행 → Edge에서 Google 로그인 후 **허용**만 누르면 끝.

## 사용법 (앤트 실행)
```powershell
.\blogger_upload.ps1 -Init                                   # 최초 인증 1회
.\blogger_upload.ps1 -File "원고.html"                       # 초안 업로드 (기본)
.\blogger_upload.ps1 -File "원고.html" -Publish              # 승인 후 발행
.\blogger_upload.ps1 -File "원고.html" -PostId <글ID>        # 기존 글 수정
.\blogger_upload.ps1 -File "원고.html" -Blog travel          # Ant-Travel Korea 대상
```
- 제목과 라벨은 원고 맨 앞 주석의 `블로거 게시물 제목(...)`, `라벨(...)` 줄에서 자동으로 읽는다.
- 앞쪽 주석은 본문에서 자동 제거되고, HTML 구조(문단·소제목·목록)는 그대로 올라간다.
- 네이버 『파이튼의 문학산책』은 파이튼 님 본인의 글만 싣는 공간으로, **파이튼 님이 직접 업로드**하신다. (이 도구의 대상 아님)
