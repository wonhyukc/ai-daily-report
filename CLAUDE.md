# AI Daily Report — 개발 가이드

**먼저 [SOUL.md](SOUL.md)를 읽으십시오.** 이 파일은 이 프로젝트만의 개발 규칙입니다.

## 프로젝트 구조

```
src/
  collectors/        # 뉴스 수집 (HackerNews, ArXiv, RSS)
  processors/        # 중복제거, 필터링, 분류, 순위 매김
  analyzers/         # 트렌드 분석
  generators/        # HTML 리포트 생성
  delivery/          # 파일 저장
  utils/             # 로깅, 텍스트 유틸

config/
  settings.py        # 모든 설정의 중심 (환경변수 + 기본값)

tests/               # pytest 기반, 60개 테스트
templates/           # HTML 템플릿

scripts/
  run.sh / run.ps1   # 파이프라인 실행 스크립트
  install-task.ps1   # Windows Task Scheduler 등록
```

## 핵심 가이드

### 1. 파이프라인 단계 수정 시

파이프라인은 이 순서로 실행됩니다:
1. **collectors**: 뉴스 수집 → list[NewsItem]
2. **processors**: 중복제거 → 필터링 → 분류 → 순위 → list[ProcessedItem]
3. **analyzers**: 트렌드 분석 → Trends
4. **generators**: HTML 생성 → str
5. **delivery**: 파일 저장

각 단계 사이의 타입은:
- `NewsItem`: base.py에 정의된 기본 뉴스 항목 (url, title, source, published_at 등)
- `ProcessedItem`: NewsItem + categories, importance_score (models.py에서 확장)
- `Trends`: trend_detector.py의 TrendResult namedtuple

**새 필드를 추가할 때는 항상 타입을 먼저 업데이트합니다.**
```python
# 나쁜 예: dict로 무한히 확장
item['new_field'] = value

# 좋은 예: 타입을 먼저 정의
class ProcessedItem(NewsItem):
    categories: List[str]
    importance_score: float
    new_field: str  # <- 여기 추가
```

### 2. 새 기능 추가할 때 (Phase 2 등)

단계별로:

1. **테스트 먼저 작성** (`tests/test_your_feature.py`)
   ```python
   def test_summarizer_generates_valid_text():
       item = NewsItem(url="...", title="...", ...)
       summary = generate_summary(item)
       assert len(summary.split()) > 0
       assert len(summary) < 500
   ```

2. **타입 정의** (`src/processors/models.py` 또는 새 파일)
   ```python
   class ProcessedItem(NewsItem):
       summary: str = ""  # 추가
   ```

3. **구현** (collectors, processors, generators 중 적절한 곳)

4. **테스트 실행해서 통과 확인**
   ```bash
   pytest tests/test_your_feature.py -v
   ```

5. **통합 테스트도 돌려서 다른 것이 안 깨졌는지 확인**
   ```bash
   pytest
   ```

### 3. 설정과 환경변수

모든 설정은 `config/settings.py`에서 관리합니다.

**환경변수 추가 시**:
```python
# .env 파일에 추가
NEW_API_KEY=value

# config/settings.py에서
NEW_API_KEY = os.getenv("NEW_API_KEY", "default_value")
```

**NEWS_SOURCES와 PROCESSING는 사용자가 런타임에 조정 가능하도록 설계되었습니다:**
```python
# DRY_RUN으로 파일 저장 없이 테스트
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# 특정 뉴스 소스만 끄기
NEWS_SOURCES["hackernews"]["enabled"] = False

# 필터링 강도 조정
PROCESSING["min_word_count"] = 100
```

### 4. 테스트 전략

**60개 테스트 모두 통과 상태 유지**:
- 새 기능: 테스트 추가
- 버그 수정: 회귀 테스트 추가
- 리팩토링: 기존 테스트로 충분한지 검토

```bash
# 테스트 실행
pytest                          # 전체
pytest tests/test_processor_*.py # 특정 모듈
pytest -k "dedup"              # 키워드로 필터

# 커버리지 확인 (선택사항)
pytest --cov=src tests/
```

### 5. Windows Task Scheduler 통합

이 프로젝트는 매일 06:00 AM에 자동 실행됩니다 (`install-task.ps1`로 등록).

**로컬에서 테스트할 때의 유의사항**:
- `DRY_RUN=true ./scripts/run.sh` 로 파일 저장 없이 테스트
- Windows라면 `.\scripts\run.ps1 -DryRun`
- 실제 파일을 만들 때는 환경변수 없이 실행

### 6. 커밋과 PR

**커밋 메시지는 다음 형식**:
```
feat: Phase 2 LLM 기반 요약 기능 추가

- ProcessedItem에 summary 필드 추가
- 새 processors/summarizer.py 추가 (Claude API 활용)
- 10개 테스트 추가

(PR #N) 또는 (GH-N) 형태로 이슈 참조
```

**PR을 나누는 기준**:
- 같은 파이프라인 단계 수정: 1 PR
- 여러 단계에 걸친 기능: 여러 PR로 분리
  - PR 1: 타입 정의 + 테스트
  - PR 2: 구현
  - PR 3: 통합 + 문서

### 7. 문서 동기화

README.md의 다음 섹션을 코드와 일치시킵니다:
- **Phase 1 / Phase 2 / Phase 3** 목록 (완료되면 ✅ 체크)
- **필수 요구사항** (Python 버전 등)
- **기능 목록** (새 기능 추가 시 반영)

[참고: 최근 #12 PR에서 문서 동기화 작업을 진행함]

## 디버깅 팁

### 뉴스가 수집되지 않음
```bash
# 1. 각 수집기 개별 테스트
python -c "from src.collectors.hackernews_collector import HackerNewsCollector; print(HackerNewsCollector().collect())"

# 2. 네트워크 문제 확인
curl -I https://hacker-news.firebaseio.com/v0/topstories.json

# 3. 캐시 초기화
rm -rf data/cache/
```

### 중복 제거가 안 됨
```python
# dedup 캐시 상태 확인
from src.processors.deduplicator import DeduplicatorWithCache
d = DeduplicatorWithCache()
# 캐시 파일: data/cache/dedup_cache.json
```

### 테스트 실패
```bash
# 하나씩 실행해서 오류 확인
pytest tests/test_failing_module.py::test_specific -vv

# 최근 변경사항 확인
git log --oneline tests/test_failing_module.py
```

## Phase 2 준비

Phase 2 구현 시 이 체크리스트를 따릅니다:

- [ ] SOUL.md의 "다음 단계 (Phase 2)" 섹션 검토
- [ ] Anthropic API KEY가 .env에 있는지 확인
- [ ] 새 processors/summarizer.py 또는 generators/action_extractor.py 작성
- [ ] ProcessedItem 타입 확장 (새 필드 추가)
- [ ] 테스트 10개 이상 추가
- [ ] 기존 60개 테스트 모두 통과 확인
- [ ] README 업데이트 (Phase 2 기능 ✅ 체크)
- [ ] PR 생성 및 리뷰

---

**문제가 발생했거나 더 자세한 설명이 필요하면:**
- `SOUL.md` — 프로젝트의 큰 그림
- `README.md` — 사용자 입장의 가이드
- Git history — 과거 결정의 맥락 (`git log --oneline -20`, `git blame src/...`)
