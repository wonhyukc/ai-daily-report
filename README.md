# 🤖 AI Daily Report System

AI 뉴스와 트렌드를 자동으로 수집하여 매일 아침 전략담당자에게 제공하는 완전 자동화 시스템입니다.

## 🚀 현재 상태

| 항목 | 상태 |
|------|------|
| **Phase** | 1 완료 (MVP) |
| **테스트** | 61/61 통과 ✅ |
| **열린 이슈** | 1개 (#21, 설정 정리 — 사용자 승인 대기) |
| **열린 PR** | 0개 |
| **다음 단계** | Phase 2: LLM 기반 요약/인사이트 |

## 📋 기능

### Phase 1 (현재)
- ✅ 글로벌 AI 뉴스 자동 수집 (HackerNews, ArXiv, RSS)
- ✅ 뉴스 중복 제거 (24시간 TTL 캐시) 및 콘텐츠 필터링
- ✅ 자동 카테고리 분류 (단어 경계 키워드 매칭)
- ✅ 중요도 순위 매김
- ✅ 키워드 트렌드 분석 및 리포트 표시
- ✅ 프로페셔널 HTML 리포트 생성
- ✅ 매일 아침 06:00 AM 자동 실행 (Windows Task Scheduler)
- ✅ pytest 단위 테스트

### Phase 2 (예정)
- 🔄 Claude API를 이용한 LLM 기반 요약
- 🔄 LLM 기반 심층 트렌드 인사이트 생성
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
- macOS / Linux / Windows (자동 스케줄 실행은 Windows Task Scheduler 기준)

### 설치 및 설정

1. **저장소 클론 후 프로젝트 디렉토리로 이동**

2. **초기 설정 실행**
```bash
# macOS / Linux
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```
```powershell
# Windows
.\scripts\setup.ps1
```

3. **API 키 설정** (Phase 2부터 필요)
```bash
# .env 파일 편집
# - ANTHROPIC_API_KEY (Anthropic Claude API)
# - NEWSAPI_KEY (Phase 3 웹 스크래핑용, 선택사항)
```

4. **테스트 실행 (드라이런)**
```bash
DRY_RUN=true ./scripts/run.sh    # macOS / Linux
```
```powershell
.\scripts\run.ps1 -DryRun        # Windows
```

5. **스케줄 등록** (Windows 전용, 관리자 권한 필요)
```powershell
.\scripts\install-task.ps1
```

## 📖 사용법

### 수동 실행

```bash
# macOS / Linux
./scripts/run.sh                 # 일반 실행
DRY_RUN=true ./scripts/run.sh    # 드라이런 (파일 저장 안 함)
```
```powershell
# Windows
.\scripts\run.ps1
.\scripts\run.ps1 -DryRun
```

### 생성된 리포트

- **위치**: `reports/` (프로젝트 루트 기준)
- **파일명**: `report-YYYY-MM-DD.html`
- **최신**: `latest.html` (항상 최신 보고서)

### 테스트 실행

```bash
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/pytest
```

## ⚙️ 설정

### 주요 설정 파일

**`config/settings.py`** — 뉴스 소스, 처리 필터, 보고서 설정

```python
# 뉴스 소스 설정 (활성화/비활성화 및 수집량 제어)
NEWS_SOURCES = {
    "hackernews": {
        "enabled": True,
        "max_stories": 30,        # 수집할 스토리 최대 개수
        "base_url": "https://hacker-news.firebaseio.com/v0"
    },
    "arxiv": {
        "enabled": True,
        "categories": ["cs.AI", "cs.LG", "stat.ML"],  # 검색 카테고리
        "max_results": 50,        # 전체 최대 논문 수 (카테고리별 균등 분배)
    },
    "rss_feeds": {
        "enabled": True,
        "feeds": [...],           # RSS 피드 URL 목록
        "max_items_per_feed": 10  # 피드당 최대 항목 수
    }
}

# 콘텐츠 처리 필터
PROCESSING = {
    "min_word_count": 10,        # 최소 단어 수 (RSS 요약 포함)
    "cache_ttl_hours": 24,       # 중복 제거 캐시 보관 기간
    "exclude_keywords": [...]    # 제외할 키워드
}

# 보고서 설정 (Phase 2 이메일 발송 시 사용)
REPORT_SETTINGS = {
    "timezone": "Asia/Seoul",    # 시간대
    "time": "06:00"              # 보고서 생성 시간
}
```

**`.env`**
```
ANTHROPIC_API_KEY=your_key_here  # Phase 2 이메일 요약 구현 시 필요
LOG_LEVEL=INFO
DRY_RUN=false
REPORT_TIMEZONE=Asia/Seoul       # 보고서 표시 시간대
REPORT_TIME=06:00               # 보고서 생성 시간
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
데이터 처리 (중복 제거 → 콘텐츠 필터링 → 분류 → 중요도 랭킹)
  ↓
트렌드 분석 (키워드/카테고리)
  ↓
HTML 생성 (Jinja2 템플릿, 트렌드 섹션 포함)
  ↓
파일 저장 (성공 시에만 중복 제거 캐시 커밋)
```

### 수집량 (실행당)

| 소스 | 건수 |
|------|------|
| HackerNews | 상위 30건 중 AI 관련 글만 |
| ArXiv | 48건 (cs.AI / cs.LG / stat.ML 각 16건) |
| RSS | 최대 20건 (피드 2개 × 10건) |

### 디렉토리 구조

```
ai-daily-report/
├── src/
│   ├── collectors/          # 뉴스 수집 모듈
│   ├── processors/          # 데이터 처리 (dedup, 필터, 분류, 랭킹)
│   ├── analyzers/           # 분석 (트렌드 등)
│   ├── generators/          # HTML 생성
│   ├── delivery/            # 리포트 전달
│   ├── utils/               # 로거, 텍스트 매칭 유틸
│   └── main.py              # 진입점
├── config/
│   └── settings.py          # 설정
├── templates/
│   └── report.html          # HTML 템플릿
├── scripts/
│   ├── run.sh               # 실행 스크립트 (macOS/Linux)
│   ├── run.ps1              # 실행 스크립트 (Windows)
│   ├── install-task.ps1     # 스케줄 등록 (Windows)
│   └── setup.ps1            # 초기 설정 (Windows)
├── tests/                   # pytest 단위 테스트
├── reports/                 # 생성된 리포트
├── data/
│   ├── logs/                # 로그
│   └── cache/               # 캐시 (중복 제거, 24h TTL)
├── requirements.txt         # Python 의존성
└── requirements-dev.txt     # 개발/테스트 의존성
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
```bash
# 로그 확인 (프로젝트 루트 기준)
cat data/logs/report-YYYY-MM-DD.log

# 드라이런으로 테스트
DRY_RUN=true ./scripts/run.sh    # Windows: .\scripts\run.ps1 -DryRun
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
- HTML 출력에 자동 XSS 방지 (Jinja2 autoescape)
- HTTPS만 사용

## 📝 로깅

로그 파일: `data/logs/report-YYYY-MM-DD.log`

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
```bash
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

**현재 버전**: 0.1.0 (Phase 1 MVP)
