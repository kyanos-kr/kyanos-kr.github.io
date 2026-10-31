import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

# Base template
TEMPLATE_PATH = r'D:\DATA CENTER\RPT DB\보도 기사 정보\AI 에이전트 통제 불능 위험\AI 에이전트 통제 불능 위험.hwpx'
BASE_OUT_DIR = r'D:\DATA CENTER\편집 기사\오늘편집'

articles = [
    {
        'folder_name': 'PHP 치명적 취약점 PHP2Shell 경보',
        'file_name': 'PHP 치명적 취약점 PHP2Shell 경보',
        'headline': '글로벌 웹 강타한 PHP 원격코드 취약점 비상',
        'sub1': 'CVE 최고위험도 9.2 기록… 웹 서버 70% 영향권',
        'sub2': '오픈AI 모델 활용 첫 탐지… 민관 긴급 패치 권고',
        'byline': '[2026.10.29 | 앤트뉴스 과학·SI부]',
        'category': '앤트뉴스 과학·SI부 | CYBER SECURITY',
        'theme_color': (0, 210, 255), # Cyan
        'bg_top': (10, 25, 45),
        'bg_bottom': (5, 12, 25),
        'paragraphs': [
            "전 세계 인터넷 웹사이트의 70% 이상을 구동하는 핵심 서버 사이드 언어인 PHP에서 인증 없이 시스템 전체를 장악할 수 있는 치명적인 원격 코드 실행(RCE) 취약점이 발견돼 글로벌 사이버 보안 생태계에 초비상이 걸렸다.",
            "보안 전문가 그룹에 의해 'PHP2Shell'로 명명된 이번 보안 결함은 특정 CMS나 웹 프레임워크가 아닌 PHP 코어 엔진 자체에 내재된 근본적인 취약점으로 식별됐다. 이에 따라 워드프레스(WordPress), 드루팔(Drupal), 줌라(Joomla) 등 PHP 기반으로 구축된 수억 개의 웹사이트와 글로벌 기업, 정부 공공기관 인프라가 일제히 직접적인 위협에 노출됐다.",
            "이번에 공개된 취약점은 공식 보안 식별 번호 CVE-2026-109618과 CVE-2026-109619로 지정됐다. 취약점의 파괴력과 위험도를 평가하는 공통 취약점 점수 시스템(CVSS)에서 두 항목 모두 최고 위험 등급에 해당하는 9.2점을 기록했다. 공격자가 대상 서버에 대한 사전 로그인 권한이나 별도의 인증 절차를 거치지 않고도 임의의 셸 명령어를 주입하여 서버 제어권을 완전히 탈취할 수 있다는 점에서 사이버 보안 역사상 가장 위험한 위협 중 하나로 꼽힌다.",
            "특히 이번 취약점은 아파치(Apache) 웹 서버의 'mod_php' 모듈 환경에서 작동하는 레거시 시스템일수록 방어벽이 취약한 것으로 확인됐다. 원격 공격자가 조작된 HTTP 요청 패킷을 전송하는 것만으로 메모리 버퍼 오버플로를 유발하고 관리자 루트(Root) 권한을 획득할 수 있어, 악성코드 유포나 데이터베이스 탈취, 랜섬웨어 감염 등 연쇄 피해가 우려된다.",
            "이번 위협의 발견 경위 역시 인공지능(AI) 기반 보안 기술의 획기적인 전환점으로 주목받고 있다. 미국 사이버 보안 전문 기업 캘리프(Calif)와 오픈AI 연구진이 공동으로 추진한 글로벌 오픈소스 보안 강화 프로젝트 '패치 더 플래닛(Patch the Planet)'의 정밀 분석 과정에서 최초 포착됐다. 오픈AI의 첨단 추론 모델이 복잡한 코드베이스의 비정상 흐름을 역추적하여 인간 연구원이 놓치기 쉬운 심층 보안 결함을 선제적으로 도출해 낸 것이다.",
            "이후 위즈(Wiz), 클라우드플레어(Cloudflare) 등 세계적인 인프라 보안 기업들이 긴급 투입되어 신속한 패치 개발과 차단 룰셋 구축에 협력했다. 오픈AI 측은 \"공격자가 취약점을 악용해 무기화하기 전에 초지능 모델이 선제적으로 결함을 규명하고 방어자에게 골든타임을 확보해 준 대표적인 방어적 AI 협업 사례\"라고 평가했다.",
            "취약점 정보가 공개되자마자 전 세계 주요 보안 기관들은 일제히 최고 수준의 경보를 발령했다. 미국 사이버안보·인프라보안국(CISA)과 국가안보국(NSA)은 연방 기관 및 주요 민간 인프라에 대해 즉각적인 버전 업그레이드를 지시하고, 패치가 불가능한 시스템은 즉시 외부 네트워크로부터 격리하거나 오프라인으로 전환할 것을 강력 권고했다. 영국 정부 역시 수십 개 대민 공공 서비스를 예방 차원에서 일시 중단하는 긴급 조치를 단행했다.",
            "국내에서도 과학기술정보통신부와 한국인터넷진흥원(KISA)이 민간 부문 사이버 위기 경보를 상향하고, 공공 및 민간 부문의 모든 PHP 서버 관리자들에게 긴급 패치를 타전했다. 국내 전자상거래와 금융, 교육 포털 중 상당수가 PHP 기반 시스템을 운영하고 있는 만큼 침해사고 예방에 총력을 기울이고 있다.",
            "글로벌 보안 당국은 모든 웹 관리자들에게 현재 운용 중인 시스템의 취약 여부를 즉각 점검하고 최신 보안 업데이트 버전(PHP 8.5.12, 8.4.27, 8.3.36, 8.2.35)으로 신속히 갱신할 것을 당부했다. 아울러 웹 애플리케이션 방화벽(WAF)의 시그니처 정책을 최고 강도로 격상하고, 비정상 셸 실행 및 외부 비인가 통신 로그를 24시간 실시간 모니터링해야 한다고 강조했다."
        ]
    },
    {
        'folder_name': '메타 테슬라 실적 호조에도 AI 투자 부담 주가 급락',
        'file_name': '메타 테슬라 실적 호조에도 AI 투자 부담 주가 급락',
        'headline': '실적 호조에도 주가 급락… 빅테크 AI 투자 역풍',
        'sub1': '메타 현금흐름 적자 전환… 테슬라 로보택시 불확실성',
        'sub2': '월가 시각 급변… 막대한 지출보다 실질 수익 입증 요구',
        'byline': '[2026.10.29 | 앤트뉴스 경제부]',
        'category': '앤트뉴스 경제부 | TECH & MARKET',
        'theme_color': (255, 140, 40), # Orange
        'bg_top': (35, 20, 40),
        'bg_bottom': (15, 8, 20),
        'paragraphs': [
            "글로벌 테크 산업을 대표하는 메타(Meta)와 테슬라(Tesla)가 시장의 기대치를 웃도는 견조한 분기 실적을 발표했음에도 불구하고 주가가 일제히 급락하는 이례적인 충격파가 월가를 뒤흔들었다. 시장의 초점이 단순한 매출 성장세나 당기순이익에서 인공지능(AI) 인프라 구축을 위해 쏟아붓는 천문학적 자본지출(CapEx)의 지속 가능성과 투자수익률(ROI)의 불확실성으로 전격 이동했기 때문이다.",
            "메타는 최근 발표한 3분기 실적에서 약 646억 달러의 매출을 달성하며 월가 컨센서스를 여유 있게 상회했다. 핵심 수익원인 디지털 광고 사업 역시 전방위적인 AI 추천 알고리즘 고도화에 힘입어 탄탄한 성장세를 과시했다. 하지만 실적 발표 직후 메타의 주가는 정규장과 시간외 거래에서 7% 가까이 곤두박질쳤다.",
            "시장의 매도세를 촉발한 뇌관은 통제 범위를 넘어서는 천문학적 자본지출 가이던스와 그에 따른 재무 건전성 악화였다. 메타 경영진은 올해 연간 자본지출 전망치 하단을 종전보다 상향한 1,350억~1,450억 달러로 올려잡았으며, 내년에도 독자 AI 데이터센터 증설, 차세대 엔비디아 GPU 확보, 초고압 전력망 인프라 계약을 위해 지출을 더욱 확대하겠다고 공언했다.",
            "특히 월가에 가장 뼈아픈 충격을 안긴 지표는 자유현금흐름(FCF)의 충격적인 적자 반전이었다. 수년간 막강한 현금 창출력을 자랑하던 메타의 분기 자유현금흐름은 AI 인프라 대금 지급이 집중되면서 마이너스 21억 달러로 급전직하했다. 미래 성장 동력을 확보하기 위한 투자라는 회사 측 설명에도 불구하고, 과도한 지출이 기업의 기본 체력인 현금 흐름마저 갉아먹고 있다는 시장의 공포가 주가 폭락을 견인했다.",
            "테슬라 역시 비슷한 구조적 딜레마에 직면했다. 분기 조정 주당순이익(EPS)과 차량 인도량 지표가 시장 예상치를 소폭 웃돌았으나, 실적 발표 컨퍼런스 콜 이후 주가는 하향 곡선을 그렸다. 현재 테슬라의 주가 밸류에이션은 단순 전기차 제조사가 아니라 자율주행 로보택시(Cybercab), 완전자율주행(FSD) 구독 생태계, 옵티머스 휴머노이드 로봇 등 '피지컬 AI 기업'이라는 막대한 프리미엄에 기반하고 있다.",
            "그러나 투자자들은 이러한 장기 청사진이 과연 언제 구체적인 매출과 영업이익으로 전환될 것인가에 대해 경영진으로부터 설득력 있는 답변을 듣지 못했다. 오히려 로보택시의 규제 승인 지연 가능성과 AI 슈퍼컴퓨팅 도조(Dojo) 클러스터 유지 비용의 증가, 자본지출 우선순위의 잦은 조정 등이 불확실성을 키웠다는 비판이 쏟아졌다.",
            "이는 2023년부터 2024년까지 월가를 지배했던 '지출 규모가 곧 미래 지배력'이라는 장밋빛 환상이 종언을 고했음을 여실히 보여준다. 초기 AI 랠리 당시에는 GPU를 얼마나 많이 확보하고 데이터센터를 얼마나 크게 짓는가가 주가 상승의 핵심 재료로 작용했다. 그러나 이제 시장은 '얼마나 쓰는가'가 아니라 '얼마를 벌고 있는가'를 가혹하게 검증하는 심판대에 빅테크들을 올려세우고 있다.",
            "금융시장 전문가들은 생성형 AI와 피지컬 AI가 궁극적으로 인류의 산업 생산성을 획기적으로 견인할 혁신 동력이라는 점에는 이견이 없다고 입을 모은다. 그러나 자본의 인내심은 무한하지 않으며, 투자 속도가 상용화 수익 속도를 지나치게 앞지를 경우 닷컴 버블과 유사한 고통스러운 밸류에이션 디레버리징을 피할 수 없다고 경고한다. 이제 빅테크 기업들은 막대한 지출 경쟁을 멈추고 현금 흐름을 안정화하며 실제 상업적 효용을 입증해야 하는 중대한 시험대에 섰다."
        ]
    },
    {
        'folder_name': '북한 권력승계 시나리오 김여정 섭정과 김주애 세습',
        'file_name': '북한 권력승계 시나리오 김여정 섭정과 김주애 세습',
        'headline': '김정은 이후 북한 권력… 김여정 섭정과 김주애 세습',
        'sub1': '실질적 2인자 국정 장악력 대 백두혈통 직계 정통성 충돌',
        'sub2': '군부 가부장제 한계 속 과도기 섭정 후 직계 승계 유력',
        'byline': '[2026.10.29 | 앤트뉴스 국제부]',
        'category': '앤트뉴스 국제부 | GEOPOLITICS',
        'theme_color': (255, 75, 75), # Crimson Red
        'bg_top': (40, 15, 20),
        'bg_bottom': (18, 6, 8),
        'paragraphs': [
            "김정은 북한 국무위원장의 건강 이상설과 불투명한 신변 변수가 주기적으로 불거질 때마다 한반도와 국제사회의 안보 시선은 '포스트 김정은' 체제의 권력 승계 시나리오로 급속히 집중되고 있다. 비록 최근 북한 관영 매체들이 공개 활동 보도를 통해 건재를 과시하며 일시적 소문을 잠재우고 있으나, 1인 수령 절대 독재라는 체제적 취약성으로 인해 후계 구도를 둘러싼 권력 지형 분석은 초미의 관심사로 남아 있다.",
            "현재 북한 권력 지형의 최상층부에서 유력한 승계 후보로 압축되는 인물은 김정은의 여동생이자 노동당 부부장인 김여정과 그의 어린 딸 김주애 두 사람이다. 국내외 정보당국과 한반도 전문가들은 이 둘의 관계를 단순한 경쟁 구도로 보기보다, 정권의 생존 본능과 정통성 원칙이 교차하는 복합적 승계 역학으로 진단하고 있다.",
            "김여정은 명실상부한 현 체제의 실질적 2인자로서 독보적인 정치적 입지를 확보하고 있다. 노동당 핵심 요직을 장악하고 대남·대미 외교 담화를 직접 진두지휘하며 대외적 대표성을 굳혔다. 김정은의 심복이자 국정 전반을 조율하는 최고 실세로서 비상사태 발생 시 당과 군의 혼란을 수습하고 즉각적인 국가 통제력을 행사할 수 있는 유일한 노련한 지도자라는 평가를 받는다.",
            "그러나 김여정이 1인 최고권력자로 온전히 등극하기에는 넘기 힘든 구조적 장벽이 존재한다. 우선 북한 체제는 헌법과 당규 위에 '백두혈통의 직계 세습'이라는 절대적 봉건 원칙이 지배한다. 김일성에서 김정일, 김정은으로 이어진 권력 이양은 언제나 '장자 혹은 직계 자녀' 승계였으며, 형제자매에게 권력이 수평 이동한 전례가 없다.",
            "더욱이 북한은 군부 고위 장령들과 노동당 원로들이 지배하는 극도로 폐쇄적이고 가부장적인 유교적 군사 체제다. 군 최고사령관이자 무오류의 수령이라는 신격화된 자리에 여성이자 방계 혈통인 김여정이 절대적 충성을 이끌어내기에는 군부 기득권의 저항과 심리적 반발이 극심할 것이라는 분석이 지배적이다.",
            "반면 최근 수년간 북한 매체의 중심에 선 김주애는 '직계 혈통의 정통성'을 온몸에 두르고 있다. 대륙간탄도미사일(ICBM) 발사 현장, 주요 군 열병식, 대규모 경제 시찰 등 국가 최고 권력의 상징적 현장마다 김정은과 나란히 주석단에 등장하며 국가 지도자급의 극진한 의전을 받고 있다. 군 장성들이 김주애 앞에서 무릎을 꿇고 경의를 표하는 장면은 그녀가 단순한 '사랑하는 자제'를 넘어 체계적인 후계 수업 단계에 있음을 극명하게 시사한다.",
            "대한민국 국가정보원 역시 초기 \"단순한 동행 및 친근한 이미지 연출\"이라는 조심스러운 평가에서 한 걸음 나아가, \"김주애가 사실상 내정된 후계자 단계에 진입했다\"고 판단을 상향 조정한 바 있다.",
            "이러한 대내외적 역학을 종합할 때 한반도 안보 전문가들이 꼽는 가장 현실적인 시나리오는 '김여정 과도 섭정 체제와 김주애 직계 권력 승계의 결합'이다. 만약 조기에 김정은 유고 사태가 발생할 경우, 아직 미성년인 김주애가 단독으로 거친 군부와 정국을 통제하기는 불가능하다. 따라서 노련한 김여정이 섭정위원장 또는 과도 비상지도부 수반을 맡아 체제를 안정시키고, 김주애가 성인이 되어 최고지도자로 안착할 때까지 권력을 관리하는 단계적 권력 이양 모델이 유력하게 제기된다.",
            "그러나 역사적으로 섭정자가 어린 군주에게 온전히 권력을 이양한 사례가 드물고, 군부 파벌 간의 충성 경쟁과 권력 암투가 폭발할 가능성도 상존한다. 북한의 권력 승계 문제는 단순한 내부 정권의 바통 터치를 넘어 핵무기 통제권, 한반도 급변 사태, 동북아 안보 질서의 전면 재편과 직결된 초대형 화약고인 만큼, 우리 안보 당국의 정밀한 다각도 비상 대응 플랜 수립이 그 어느 때보다 절실하다."
        ]
    },
    {
        'folder_name': '일론 머스크의 혁신 비전과 제조 주권 철학 분석',
        'file_name': '일론 머스크의 혁신 비전과 제조 주권 철학 분석',
        'headline': '일론 머스크의 파격 혁신… 무한 맵 확장과 기술 주권',
        'sub1': '미 아동 스페이스X 주식 지급과 냉가스 플라잉카 도전',
        'sub2': '시간 자원 극대화·장비 내재화로 글로벌 패권 재정의',
        'byline': '[2026.10.29 | 앤트뉴스 과학·SI부]',
        'category': '앤트뉴스 과학·SI부 | INNOVATION LEADERSHIP',
        'theme_color': (180, 100, 255), # Purple
        'bg_top': (30, 15, 45),
        'bg_bottom': (12, 6, 22),
        'paragraphs': [
            "테슬라와 스페이스X를 이끄는 일론 머스크가 기존의 상식과 제도적 경계를 산산이 부수는 파격적인 비전과 독창적인 공학 철학을 연이어 제시하며 글로벌 산업 패권을 전면 재편하고 있다. 실패를 두려워하지 않는 급진적 실행력과 생산 수단의 완벽한 내재화를 축으로, 인류 문명의 지평을 '유한 맵'에서 '무한 맵'으로 확장하려는 그의 행보는 전 세계에 거대한 충격과 성찰을 안겨주고 있다.",
            "최근 머스크는 내년부터 미국의 모든 어린이에게 스페이스X의 주식을 1주씩 직접 지급하겠다는 전대미문의 자산 이전 계획을 공식 선언했다. 어린이 개별 명의 계좌에 비상장 우주항공 거함의 주식을 직접 분배하는 이 프로젝트는 총 100억 달러(약 13조 5,000억 원) 이상의 천문학적 자본이 투입되는 국가적 규모의 구상이다. 이에 도널드 트럼프 전 대통령이 즉각 \"빅 땡큐(Big thank you)\"라는 공개 지지 성명을 내놓으며 미 정가와 산업계의 비상한 관심을 집중시켰다.",
            "이러한 머스크의 파격 행보를 대하는 각국의 반응은 극명한 대조를 이룬다. 한국 사회 일각에서는 그의 구상을 허황된 과대망상이나 단기 주가 부양용 쇼로 폄하하며, 실패 리스크만을 강조하는 이른바 '안전지대 편향(Safe-zone Bias)'에 갇혀 기술 패러다임의 거시적 전환을 보지 못하는 우를 범하고 있다. 반면 중국은 머스크를 현대 산업의 살아있는 이정표로 설정하고, 공학 엘리트와 당 지도부가 그의 비전을 아자일(Agile)하게 벤치마킹하여 우주 항공, 전기차, 휴머노이드 로봇 생태계를 무섭게 흡수·추격하는 실용적 대응을 보이고 있다.",
            "머스크의 공학적 상상력은 이동 수단의 근본적 개념마저 뒤흔들고 있다. 2018년 첫 언급 당시 대중의 조롱과 회의론에 부딪혔던 테슬라 차세대 로드스터의 '플라잉카' 구상은 현재 구체적인 기술 사양으로 현실화되고 있다. 전통적인 화석연료 연소 방식 대신 고성능 전기 펌프를 활용해 공기를 약 10,000 PSI(파운드/제곱인치)에 달하는 초고압으로 압축한 뒤 고속 분사하는 '초고압 냉가스 추진기 시스템(Cold Gas Thruster System)'을 탑재함으로써, 기존 내연기관과 전동화 파워트레인의 한계를 뛰어넘는 비행 제어와 압도적인 제로백 가속을 실현하겠다는 전략이다.",
            "이러한 공학적 파괴력의 밑바탕에는 머스크만의 독창적인 '시간 자원 중심의 리스크 관리 철학'이 자리 잡고 있다. 그는 자본의 손실이나 평판의 훼손은 재도전을 통해 얼마든지 복구할 수 있지만, 한번 흘러간 시간은 결코 회복할 수 없는 유일무이한 불가역적 자원이라고 정의한다. 따라서 완벽을 기하느라 시간을 허비하기보다 '빛의 속도로 빠르게 실패(Fast Failure)'하고, 즉각 오류를 수정하여 다음 버전으로 전진하는 급진적 진화 방식을 프로젝트 전반에 관철하고 있다. 심지어 그는 노년층의 고정관념 고착화로 인한 '사회적 질식'을 막기 위해 인간의 무리한 수명 연장 기술 개발을 거부한다는 확고한 철학적 소신까지 견지한다.",
            "아울러 머스크 혁신의 가장 강력한 무기는 '제1원리 사고방식(First-Principles Thinking)'에 기반한 제조 설비의 완전한 수직계열화(Vertical Integration)다. 인텔, 삼성전자, TSMC 등 기존 반도체 및 제조 거함들이 외부 특수 장비사(ASML 등)의 공급망에 종속되어 파괴적 혁신에 구조적 제약을 겪는 것과 달리, 머스크는 공장 자체를 하나의 제품('기계를 만드는 기계')으로 정의하고 핵심 제조 설비를 100% 자체 설계·내재화함으로써 완벽한 제조 자립성과 기술 주권을 거머쥐었다.",
            "머스크는 안보와 주권의 영역에서도 외세의 정보전 및 여론 조작을 차단하기 위해 소셜 플랫폼 X에서 20만 개 이상의 악성 봇과 가짜 계정을 영구 퇴출하고, 비시민권자 투표권 부여를 '유권자 수입'으로 규정하며 민주주의 본질 수호를 역설하고 있다. 안주와 냉소에 머물러 있는 사회에는 미래가 없다. 타인이 규정한 한계를 지우고 인류의 지평을 '무한 맵'으로 넓혀가는 머스크의 집념은, 대전환의 시대를 맞이한 우리 산업과 국가 전략에 무엇을 혁신하고 무엇을 내재화해야 하는지 묵직한 화두를 던지고 있다."
        ]
    },
    {
        'folder_name': '일론 머스크 7대 미래 예측과 문명사적 실현 가능성 진단',
        'file_name': '일론 머스크 7대 미래 예측과 문명사적 실현 가능성 진단',
        'headline': '머스크 7대 미래 예측 심층 해부… 냉철한 현실 진단',
        'sub1': '초지능 조기 도래·휴머노이드 보급… 전력·소재 병목 직면',
        'sub2': '환원주의 마케팅 넘어선 물리적 한계와 제도적 장벽 조명',
        'byline': '[2026.10.29 | 앤트뉴스 미래전략부]',
        'category': '앤트뉴스 미래전략부 | FUTURE FORECAST',
        'theme_color': (70, 160, 255), # Royal Blue
        'bg_top': (20, 25, 50),
        'bg_bottom': (8, 10, 25),
        'paragraphs': [
            "인류 문명의 진화 방향을 재정의하며 글로벌 자본과 인재를 빨아들이고 있는 일론 머스크의 7대 미래 예측에 대해, 과학계와 산업계가 장밋빛 유토피아의 환상을 걷어내고 냉철한 실현 가능성과 물리적 병목을 짚어보는 심층 해부에 착수했다. 극단적인 마감 시한을 제시해 혁신의 속도를 압축하는 특유의 '머스크 타임'이 기술 발전을 견인하는 것은 분명하지만, 물리학의 법칙과 정치경제학적 제도를 무시한 환원주의적 주장은 철저히 검증되어야 한다는 지적이다.",
            "머스크가 공언한 첫 번째 예측인 '10~20년 내 노동의 종말과 보편적 고소득(UHI) 사회'는 실현 가능성이 30% 수준으로 평가됐다. 정형화된 육체 및 사무 노동은 AI와 로봇에 의해 급속히 대체되겠으나, 배관이나 복합 현장 수리와 같은 비정형 물리 환경과 인간 고유의 정서·책임 영역은 단기간 내 대체가 불가능하다. 더욱이 노동이 사라질 경우 부의 원천이 로봇 인프라를 독점한 극소수 테크 과두제로 집중될 위험이 크며, 이를 로봇세로 환수해 전 인류에게 재분배할 초국가적 조세 제도의 수립은 극심한 정치적 이해관계로 인해 현실화되기 어렵다.",
            "두 번째 화두인 '인간 지능 총합을 능가하는 초지능(AGI/ASI)의 조기 도래'는 50%의 실현 가능성을 보였다. 특정 소프트웨어 연산, 코딩, 복합 패턴 분석은 이미 인간을 초월하고 있으나, 환각(Hallucination) 현상의 완전한 통제 실패와 더불어 AI 데이터센터를 지탱할 글로벌 전력망·변압기·냉각수 부족이라는 거대한 '물리적 한계의 벽(Wall of Physics)'이 2029년 완전 초지능 도달의 최대 복병으로 지목된다.",
            "세 번째, '3~5년 내 최고 외과 의사를 능가하는 완전 자율 로봇 수술'은 실현 가능성이 15%로 가장 비관적인 평가를 받았다. 인체 장기와 연부 조직(Soft tissue)은 수술 중 시시각각 비선형 변형을 일으키고 환자마다 혈관 구조가 완전히 상이하다. 현재의 비전 기반 AI로는 예측 불가능한 돌발 출혈이나 조직 유착에 유연하게 대응하기 어렵고, 보수적인 보건 당국의 임상 승인 절차와 의료 사고 발생 시의 법적 책임(Liability) 귀속 문제가 거대한 제도적 장벽으로 가로막혀 있다.",
            "네 번째, '전 세계 100억~200억 대 휴머노이드 로봇 보급'은 40%로 분석됐다. 방향성은 부합하나 시점의 대폭 지연이 불가피하다. 현재 2~4시간에 불과한 배터리 지속 시간, 수십 개 정밀 관절 모터의 발열과 기계적 마모, 핵심 희토류 공급망의 병목으로 인해 2030년대 중반까지는 전면 보급보다 통제된 스마트 공장과 물류 거점에 수십만~수백만 대 수준으로 배치되는 것이 현실적 궤도다.",
            "다섯 번째, '초디플레이션으로 인한 저축 및 은퇴 자금의 무의미화'는 기술 환원주의가 범한 경제학적 오류로 20%의 실현 가능성을 기록했다. 로봇 생산으로 공산품 제조 원가가 0에 수렴하더라도, 인간의 근원적 소유욕이 투사되는 핵심 입지 부동산, 청정 에너지, 고성능 연산 자원 등 '복제 불가능한 물리적 희소 자산'은 오히려 천문학적인 초인플레이션을 겪게 된다. 화폐 가치가 무력화된 채 생산 수단을 독점한 자와 배급에 의존하는 자 사이의 자산 극단화가 초래될 공산이 크다.",
            "여섯 번째와 일곱 번째인 '20~30년 내 화성 100만 명 자립 도시 건설'과 '뉴럴링크(BCI)를 통한 초지능 공생'은 각각 25%와 55%로 평가됐다. 화성 무인 착륙과 소규모 연구 기지는 70% 이상의 높은 성공 가능성을 가지나, 치명적인 우주 방사선과 중력 결핍(지구의 38%)에 따른 인체 골밀도 파괴, 100% 폐쇄형 생태계 구축의 기술적 난제로 100만 도시 건설은 금세기 내 달성이 희박하다. 반면 뉴럴링크는 사지 마비 환자의 신경 제어와 시각 복원 등 의료 재활 분야에서 85%의 눈부신 성공을 거두고 있으나, 860억 개 뇌 뉴런의 복합적 의식을 디지털로 온전히 전송하는 전뇌 융합은 현대 뇌과학의 한계를 넘어서는 장기 과제로 남았다.",
            "종합적으로 머스크의 미래학은 물리학적 가능성에 기반한 원대한 도전이자 자본과 인재를 견인하는 강력한 '자기실현적 동력'으로 기능하고 있다. 인류는 그의 예언을 맹목적으로 추종하거나 허황된 환상으로 치부하는 양극단을 경계해야 한다. 피지컬 AI와 초지능이 가져올 문명사적 대격변의 본질을 직시하고, 물리적 제약을 돌파할 기술 주권을 확보하는 동시에 사회적 양극화를 완화할 제도적 안전망을 치밀하게 구축해야 할 시점이다."
        ]
    }
]

def create_hwpx(output_path, headline, sub1, sub2, byline, paragraphs):
    temp_dir = os.path.join(os.path.dirname(output_path), '_temp_build_' + os.path.basename(output_path))
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        z.extractall(temp_dir)

    # 1. Update header.xml
    hdr_path = os.path.join(temp_dir, 'Contents', 'header.xml')
    tree_hdr = ET.parse(hdr_path)
    root_hdr = tree_hdr.getroot()

    ns_hh = 'http://www.hancom.co.kr/hwpml/2011/head'
    ns_hp = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
    ns_core = 'http://www.hancom.co.kr/hwpml/2011/core'
    ns_hs = 'http://www.hancom.co.kr/hwpml/2011/section'

    # Font check: Ensure '한컴 윤고딕 740'
    for ff in root_hdr.iter(f'{{{ns_hh}}}fontface'):
        for font in ff.iter(f'{{{ns_hh}}}font'):
            font.attrib['face'] = '한컴 윤고딕 740'

    # Ensure lineSpacing 160%
    for p in root_hdr.iter(f'{{{ns_hh}}}paraPr'):
        found_ls = False
        for ls in p.iter(f'{{{ns_hh}}}lineSpacing'):
            ls.attrib['type'] = 'PERCENT'
            ls.attrib['value'] = '160'
            found_ls = True
        if not found_ls:
            new_ls = ET.Element(f'{{{ns_hh}}}lineSpacing', {'type': 'PERCENT', 'value': '160', 'unit': 'PERCENT'})
            p.append(new_ls)

    ET.register_namespace('hh', ns_hh)
    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hc', ns_core)
    tree_hdr.write(hdr_path, encoding='utf-8', xml_declaration=True)

    # 2. Update section0.xml
    sec_path = os.path.join(temp_dir, 'Contents', 'section0.xml')
    tree_sec = ET.parse(sec_path)
    root_sec = tree_sec.getroot()

    first_p = root_sec.find(f'{{{ns_hp}}}p')
    sec_pr = None
    ctrl = None
    if first_p is not None:
        run0 = first_p.find(f'{{{ns_hp}}}run')
        if run0 is not None:
            sec_pr = run0.find(f'{{{ns_hp}}}secPr')
            ctrl = run0.find(f'{{{ns_hp}}}ctrl')

    for child in list(root_sec):
        root_sec.remove(child)

    p_id_counter = 1000000000

    def make_p(paraPrIDRef="0", styleIDRef="0"):
        nonlocal p_id_counter
        p = ET.Element(f'{{{ns_hp}}}p', {
            'id': str(p_id_counter),
            'paraPrIDRef': str(paraPrIDRef),
            'styleIDRef': str(styleIDRef),
            'pageBreak': '0',
            'columnBreak': '0',
            'merged': '0'
        })
        p_id_counter += 1
        return p

    def make_run(charPrIDRef="9", text=None):
        r = ET.Element(f'{{{ns_hp}}}run', {'charPrIDRef': str(charPrIDRef)})
        if text is not None:
            t = ET.SubElement(r, f'{{{ns_hp}}}t')
            t.text = text
        return r

    # P0: Main Headline (charPr 7: 11pt, bold)
    p0 = make_p("0", "0")
    run_sec = ET.SubElement(p0, f'{{{ns_hp}}}run', {'charPrIDRef': '7'})
    if sec_pr is not None:
        run_sec.append(sec_pr)
    if ctrl is not None:
        run_sec.append(ctrl)
    t0 = ET.SubElement(run_sec, f'{{{ns_hp}}}t')
    t0.text = headline
    root_sec.append(p0)

    # Blank line
    p_sp1 = make_p("0", "0")
    p_sp1.append(make_run("7"))
    root_sec.append(p_sp1)

    # Subheadline 1 (charPr 7: 11pt, bold)
    p_sub1 = make_p("0", "0")
    p_sub1.append(make_run("7", sub1))
    root_sec.append(p_sub1)

    # Subheadline 2 (charPr 7: 11pt, bold)
    p_sub2 = make_p("0", "0")
    p_sub2.append(make_run("7", sub2))
    root_sec.append(p_sub2)

    # Blank line
    p_sp2 = make_p("0", "0")
    p_sp2.append(make_run("9"))
    root_sec.append(p_sp2)

    # Body paragraphs (charPr 9: 11pt, normal)
    preview_paras = []
    for para_text in paragraphs:
        if not para_text.strip():
            continue
        p_body = make_p("0", "0")
        p_body.append(make_run("9", para_text.strip()))
        root_sec.append(p_body)

        # Blank line between paragraphs
        p_empty = make_p("0", "0")
        p_empty.append(make_run("9"))
        root_sec.append(p_empty)
        preview_paras.append(para_text.strip())

    # Byline (paraPr 20: right-aligned, charPr 8: 9.5pt)
    p_by = make_p("20", "0")
    p_by.append(make_run("8", byline))
    root_sec.append(p_by)

    # Final empty line
    p_end = make_p("0", "0")
    p_end.append(make_run("9"))
    root_sec.append(p_end)

    ET.register_namespace('hp', ns_hp)
    ET.register_namespace('hs', ns_hs)
    ET.register_namespace('hc', ns_core)
    ET.register_namespace('hh', ns_hh)
    tree_sec.write(sec_path, encoding='utf-8', xml_declaration=True)

    # PrvText.txt
    prv_text_path = os.path.join(temp_dir, 'Preview', 'PrvText.txt')
    if os.path.exists(prv_text_path):
        preview_content = f"{headline}\n\n{sub1}\n{sub2}\n\n" + "\n\n".join(preview_paras) + f"\n\n{byline}\n"
        with open(prv_text_path, 'w', encoding='utf-8') as pf:
            pf.write(preview_content)

    if os.path.exists(output_path):
        os.remove(output_path)

    with zipfile.ZipFile(output_path, 'w') as zout:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zout.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root_dir, dirs, files in os.walk(temp_dir):
            for file in files:
                full_p = os.path.join(root_dir, file)
                rel_p = os.path.relpath(full_p, temp_dir)
                if rel_p == 'mimetype':
                    continue
                zout.write(full_p, rel_p, compress_type=zipfile.ZIP_DEFLATED)

    shutil.rmtree(temp_dir)
    print(f"HWPX generated: {output_path}")

def render_image(output_path, cat, title, sub1, sub2, bg_top, bg_bottom, theme_color):
    width = 640
    height = 360
    im = Image.new('RGB', (width, height), bg_bottom)
    draw = ImageDraw.Draw(im)

    # 1. Gradient background
    for y in range(height):
        ratio = y / height
        r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
        g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
        b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Subtle grid lines
    grid_color = (255, 255, 255, 15)
    for x in range(40, width, 60):
        draw.line([(x, 0), (x, height)], fill=(40, 50, 70))
    for y in range(40, height, 60):
        draw.line([(0, y), (width, y)], fill=(40, 50, 70))

    # 3. Fonts
    font_bold = "C:/Windows/Fonts/malgunbd.ttf"
    font_reg = "C:/Windows/Fonts/malgun.ttf"
    
    font_cat = ImageFont.truetype(font_bold, 13)
    font_brand = ImageFont.truetype(font_bold, 11)
    font_title = ImageFont.truetype(font_bold, 21)
    font_sub = ImageFont.truetype(font_reg, 13)
    font_foot = ImageFont.truetype(font_bold, 11)

    # 4. Accent category bar & text
    draw.rectangle([(36, 32), (42, 54)], fill=theme_color)
    draw.text((50, 34), cat, font=font_cat, fill=theme_color)
    draw.text((390, 36), "KYANOS ANTNEWS INTELLIGENCE", font=font_brand, fill=(160, 185, 210))

    # 5. Title
    draw.text((36, 85), title, font=font_title, fill=(255, 255, 255))

    # 6. Subheadlines
    sub_combined = f"• {sub1}\n• {sub2}"
    draw.multiline_text((36, 175), sub_combined, font=font_sub, fill=(215, 225, 235), spacing=10)

    # 7. Bottom accent divider & footer
    draw.line([(36, 305), (604, 305)], fill=theme_color, width=2)
    draw.text((36, 320), "2026.10.29 | ANTNEWS EDITORIAL REPORT", font=font_foot, fill=(140, 160, 185))
    draw.text((475, 320), "STANDARD 640PX IMAGE", font=font_foot, fill=(140, 160, 185))

    im.save(output_path, 'JPEG', quality=95)
    print(f"Image generated: {output_path}")

def main():
    for item in articles:
        target_dir = os.path.join(BASE_OUT_DIR, item['folder_name'])
        os.makedirs(target_dir, exist_ok=True)

        hwpx_path = os.path.join(target_dir, f"{item['file_name']}.hwpx")
        jpg_path = os.path.join(target_dir, f"{item['file_name']}.jpg")

        create_hwpx(
            hwpx_path,
            item['headline'],
            item['sub1'],
            item['sub2'],
            item['byline'],
            item['paragraphs']
        )

        render_image(
            jpg_path,
            item['category'],
            item['headline'],
            item['sub1'],
            item['sub2'],
            item['bg_top'],
            item['bg_bottom'],
            item['theme_color']
        )

if __name__ == '__main__':
    main()
