# 🚀 빠른 시작 가이드

## 1️⃣ 설치 (첫 실행만)

### macOS / Linux

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
.\scripts\setup.ps1
```

## 2️⃣ 실행

### macOS / Linux

```bash
./scripts/run.sh                # 일반 실행
DRY_RUN=true ./scripts/run.sh   # 드라이런 (파일 저장 안 함)
```

### Windows (PowerShell)

```powershell
.\scripts\run.ps1
.\scripts\run.ps1 -DryRun
```

### 자동 실행 (Windows 전용, 관리자 권한)

```powershell
.\scripts\install-task.ps1   # 매일 06:00 자동 실행 등록
```

## 3️⃣ 리포트 보기

```bash
open reports/latest.html        # macOS
# Windows: Start-Process .\reports\latest.html
```

## 🔧 API 키 설정 (Phase 2부터 필요, 선택사항)

`.env` 파일 편집:
```
ANTHROPIC_API_KEY=your_key
```

## 📁 파일 위치 (프로젝트 루트 기준)

- 리포트: `reports/latest.html`
- 로그: `data/logs/`
- 설정: `config/settings.py`

## ✨ 기능

- ✅ 자동 뉴스 수집 — 실행당 최대 약 108건 (HackerNews 30건 중 AI 관련 필터링 + ArXiv 48건 + RSS 30건)
- ✅ 중복 제거(24시간 TTL 캐시)·콘텐츠 필터링·카테고리 분류·중요도 랭킹
- ✅ 키워드 트렌드 분석 포함 HTML 리포트 생성
- ✅ 매일 06:00 자동 실행 (Windows Task Scheduler)

## 🧪 테스트

```bash
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/pytest
```

---

**완성!** 🎉 시스템이 작동 중입니다.
