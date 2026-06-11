# 🤖 AI Daily Report System

AI 뉴스와 트렌드를 자동으로 수집하여 매일 아침 전략담당자에게 제공하는 완전 자동화 시스템입니다.

## 📋 기능

### Phase 1 (현재)
- ✅ 글로벌 AI 뉴스 자동 수집 (HackerNews, ArXiv, RSS)
- ✅ 뉴스 중복 제거 및 필터링
- ✅ 자동 카테고리 분류
- ✅ 중요도 순위 매김
- ✅ 프로페셔널 HTML 리포트 생성
- ✅ 매일 아침 06:00 AM 자동 실행

### Phase 2 (예정)
- 🔄 Claude API를 이용한 LLM 기반 요약
- 🔄 트렌드 분석 및 인사이트 생성
- 🔄 액션 아이템 자동 추출
- 🔄 이메일 발송 기능

### Phase 3 (예정)
- 🔄 웹 스크래핑 (한국 뉴스)
- 🔄 경쟁사 자동 추적
- 🔄 Slack 통합
- 🔄 웹 대시보드

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.11+
- Windows 11 (또는 최신 Windows 10)
- PowerShell 5.1+

### 설치 및 설정

1. **저장소 클론 또는 폴더 생성**
```bash
cd C:\temp\ai-daily-report
```

2. **초기 설정 실행**
```powershell
.\scripts\setup.ps1
```

3. **API 키 설정**
```powershell
# .env 파일 편집
# 이 항목들을 작성하세요:
# - ANTHROPIC_API_KEY (Anthropic Claude API)
# - NEWSAPI_KEY (선택사항, Phase 2부터 필요)
```

4. **테스트 실행 (드라이런)**
```powershell
.\scripts\run.ps1 -DryRun
```

5. **스케줄 등록** (관리자 권한 필요)
```powershell
# 관리자로 PowerShell 실행 후:
.\scripts\install-task.ps1
```

## 📖 사용법

### 수동 실행

```powershell
# 일반 실행
.\scripts\run.ps1

# 테스트 실행 (파일 저장 안 함)
.\scripts\run.ps1 -DryRun

# 로그 저장
.\scripts\run.ps1 -LogOutput "C:\temp\logs\report.log"
```

### 생성된 리포트

- **위치**: `C:\temp\ai-daily-report\reports\`
- **파일명**: `report-YYYY-MM-DD.html`
- **최신**: `latest.html` (항상 최신 보고서)

### 브라우저에서 보기
```powershell
# 최신 리포트 열기
Start-Process "C:\temp\ai-daily-report\reports\latest.html"
```

## ⚙️ 설정

### 주요 설정 파일

**`config/settings.py`**
```python
# 뉴스 소스 활성화/비활성화
NEWS_SOURCES = {
    "hackernews": {"enabled": True, ...},
    "arxiv": {"enabled": True, ...},
    "rss_feeds": {"enabled": True, ...}
}

# 보고서 생성 시간
REPORT_SETTINGS = {
    "timezone": "Asia/Seoul",
    "time": "06:00"
}
```

**`.env`**
```
ANTHROPIC_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here (optional)
LOG_LEVEL=INFO
DRY_RUN=false
```

### RSS 피드 추가/변경

`config/settings.py`에서 `NEWS_SOURCES["rss_feeds"]["feeds"]` 수정:

```python
"feeds": [
    "https://feeds.yoursite.com/feed.xml",
    "https://other-feed.com/rss",
]
```

## 📊 아키텍처

```
뉴스 수집 (병렬)
  ↓
데이터 처리 (중복 제거, 필터링, 분류)
  ↓
순위 매김 (중요도)
  ↓
HTML 생성 (Jinja2 템플릿)
  ↓
파일 저장
```

### 디렉토리 구조

```
C:\temp\ai-daily-report\
├── src/
│   ├── collectors/          # 뉴스 수집 모듈
│   ├── processors/          # 데이터 처리
│   ├── analyzers/           # 분석 (트렌드 등)
│   ├── generators/          # HTML 생성
│   ├── delivery/            # 리포트 전달
│   └── main.py              # 진입점
├── config/
│   └── settings.py          # 설정
├── templates/
│   └── report.html          # HTML 템플릿
├── scripts/
│   ├── run.ps1              # 실행 스크립트
│   ├── install-task.ps1     # 스케줄 등록
│   └── setup.ps1            # 초기 설정
├── reports/                 # 생성된 리포트
├── data/
│   ├── logs/                # 로그
│   └── cache/               # 캐시 (중복 제거)
└── requirements.txt         # Python 의존성
```

## 🔍 문제 해결

### Python 모듈을 찾을 수 없음
```powershell
# 가상환경 활성화 확인
.\venv\Scripts\Activate.ps1

# 의존성 재설치
python -m pip install -r requirements.txt
```

### 스크립트 실행 권한 거부
```powershell
# 실행 정책 변경 (현재 사용자)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Task Scheduler 오류
```powershell
# 관리자 권한으로 실행했는지 확인
# 스크립트 경로가 절대 경로인지 확인
# Event Viewer에서 로그 확인
```

### 뉴스가 수집되지 않음
```powershell
# 로그 확인
Get-Content "C:\temp\ai-daily-report\data\logs\report-YYYY-MM-DD.log"

# 인터넷 연결 확인
Test-NetConnection -ComputerName hacker-news.firebaseio.com -Port 443

# 드라이런으로 테스트
.\scripts\run.ps1 -DryRun
```

## 📈 성능 지표

| 작업 | 예상 시간 |
|------|---------|
| 뉴스 수집 | ~1분 |
| 데이터 처리 | ~15초 |
| HTML 생성 | ~10초 |
| 파일 저장 | ~5초 |
| **총 소요시간** | **~1.5-2분** |

## 🔐 보안

- API 키는 `.env` 파일에 저장 (Git 무시됨)
- HTML 출력에 자동 XSS 방지 (Jinja2)
- 민감 정보는 로그에서 마스킹
- HTTPS만 사용

## 📝 로깅

로그 파일: `C:\temp\ai-daily-report\data\logs\report-YYYY-MM-DD.log`

로그 레벨 변경:
```python
# config/settings.py
LOG_LEVEL = "DEBUG"  # 또는 "INFO", "WARNING", "ERROR"
```

## 🤝 커스터마이징

### 카테고리 추가

`config/settings.py`의 `CATEGORIES`를 수정:

```python
CATEGORIES = {
    "MyCategory": ["keyword1", "keyword2"],
}
```

### 경쟁사 목록 변경

```python
COMPETITORS = [
    "CompanyA", "CompanyB", "CompanyC"
]
```

### HTML 템플릿 수정

`templates/report.html`을 편집하여 디자인 변경 가능.

## 📞 지원

### 로그 수집
문제 발생 시 다음 파일들을 확인하세요:
- `data/logs/` 폴더의 최신 로그
- 생성된 HTML 리포트의 통계 섹션

### 환경 정보
```powershell
# 시스템 정보 확인
$PSVersionTable
python --version
pip list
```

## 📄 라이선스

Internal Use Only

## 🎯 로드맵

- [x] Phase 1: MVP (뉴스 수집 & HTML 리포트)
- [ ] Phase 2: LLM 분석 (요약, 트렌드, 액션)
- [ ] Phase 3: 고급 기능 (웹 스크래핑, Slack, 경쟁사 분석)
- [ ] Phase 4: 웹 대시보드 및 고급 분석

---

**마지막 업데이트**: 2024년 6월
**현재 버전**: 0.1.0 (Phase 1 MVP)
