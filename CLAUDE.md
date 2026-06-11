# CLAUDE.md — 개발 가이드

**이 프로젝트의 정체성**: 전략담당자가 AI 업계의 중요한 신호를 매일 빠르게 파악할 수 있게 해주는 완전 자동화 시스템.

## 아키텍처 원칙

**파이프라인의 각 단계가 명확한 책임을 갖고 독립적으로 테스트 가능하도록 설계**

```
수집 → 처리 → 분석 → 생성 → 전달
(collectors → processors → analyzers → generators → delivery)
```

- **타입 안정성**: NewsItem → ProcessedItem → HTML (dict 변환 금지)
- **설정 중심**: PROCESSING, NEWS_SOURCES로 동작을 제어 (하드코딩 금지)
- **테스트 우선**: 60개 테스트 유지, 새 기능은 테스트부터

## 개발 규칙

### 파이프라인 단계 수정 시

```python
# ❌ 나쁜 예: dict로 무한히 확장
item['new_field'] = value

# ✅ 좋은 예: 타입을 먼저 정의
class ProcessedItem(NewsItem):
    categories: List[str]
    importance_score: float
    new_field: str  # <- 여기 추가
```

**각 단계 사이 타입**:
- `NewsItem` (base.py): url, title, source, published_at
- `ProcessedItem` (models.py): NewsItem + categories, importance_score
- `Trends` (trend_detector.py): TrendResult namedtuple

### 새 기능 추가 순서 (Red-Green-Refactor)

1. **Red**: 테스트 먼저 작성 → 실패 확인
   ```bash
   pytest tests/test_your_feature.py
   ```

2. **Green**: 타입 정의 → 구현 → 통과 확인
   ```bash
   pytest  # 전체 60개 통과해야 함
   ```

3. **Refactor**: 정리 후 PR

### 설정과 환경변수

**모든 설정은 `config/settings.py`에서 관리**

```python
# 런타임 제어 가능한 설정
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
NEWS_SOURCES["hackernews"]["enabled"] = False  # 특정 소스만 끔
PROCESSING["min_word_count"] = 100  # 필터링 강도 조정
```

### 테스트 전략

```bash
pytest                          # 전체 (60개)
pytest tests/test_processor*.py # 특정 모듈
pytest -k "dedup"              # 키워드 필터
```

**규칙**: 기능 추가 시 테스트도 추가, 60개 유지.

## 주요 파일

| 파일 | 역할 |
|------|------|
| `config/settings.py` | 모든 설정 중심 |
| `src/processors/models.py` | ProcessedItem 타입 정의 |
| `src/main.py` | 파이프라인 실행 (5단계) |
| `tests/` | 60개 pytest 케이스 |

## Phase 1에서 적용된 주요 설계 결정

### 1. Deduplicator 안전성 (이슈 #3, #5)

**캐시 커밋 타이밍**
```python
# ❌ 나쁜 예: 수집 후 바로 캐시 저장
items = collect()
dedup_cache.add(items)  # DRY_RUN도 캐시에 남음

# ✅ 좋은 예: 파이프라인 성공 후에만
items = collect()
items = process(items)
items = generate_html(items)
save_report(items)
dedup_cache.commit()  # 파이프라인 성공 시에만
```

**URL 없는 항목 처리**
```python
# src/processors/deduplicator.py:65
hash_source = item.url or f"{item.source}:{item.title}"
# HackerNews의 URL 없는 항목도 제목과 소스로 고유하게 해싱
```

### 2. CollectorManager 강건성 (이슈 #7)

```python
# src/collectors/collector_manager.py:35~37
if not self.collectors:
    logger.warning("No news sources are enabled. Nothing to collect.")
    return []
# 모든 소스 비활성화 시 max_workers=0 크래시 방지
```

### 3. 타임스탐프 일관성 (이슈 #1)

```python
# src/collectors/rss_collector.py, hackernews_collector.py
from datetime import timezone
published_at = datetime.now(timezone.utc)
published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
# 모든 타임스탐프를 UTC aware로 통일 (naive/aware 혼동 방지)
```

### 4. 인코딩 호환성 (이슈 #2)

```python
# src/utils/logger.py
import io
utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Windows 콘솔에서도 이모지 출력 가능

# src/processors/deduplicator.py
with open(cache_file, 'r', encoding='utf-8') as f:
```

### 5. 필터링 정확성 (이슈 #6)

```python
# config/settings.py
"exclude_keywords": ["advertisement", "sponsored", "ad"]
# 키워드는 단어 경계로 매칭 (부분문자열 오탐 방지)
```

### 6. ProcessedItem 타입 안정성 (이슈 #11)

```python
# src/processors/models.py
class ProcessedItem(NewsItem):
    categories: List[str]
    importance_score: float
# dict로 변환하지 않고 타입을 파이프라인 끝까지 유지
# 새 필드는 항상 타입에 먼저 추가
```

### 7. 설정 중심 아키텍처 (이슈 #8)

```python
# config/settings.py
PROCESSING = {
    "min_word_count": 50,        # 콘텐츠 필터링
    "cache_ttl_hours": 24,       # 중복 제거 캐시 보관기간
    "exclude_keywords": [...],   # 필터 제외 키워드
}
# 동작을 하드코딩하지 않고 설정으로 제어
```

## Phase 2 체크리스트

Phase 2 (LLM 기반 요약, 트렌드, 액션 아이템, 이메일):

- [ ] Anthropic API KEY를 .env에 추가
- [ ] 새 파일 생성 (예: `src/processors/summarizer.py`)
- [ ] ProcessedItem 타입 확장 (새 필드 추가)
- [ ] 테스트 10개 이상 추가
- [ ] `pytest` 실행 → 60개 + N개 모두 통과
- [ ] README 업데이트 (Phase 2 기능 ✅ 체크)
- [ ] 커밋 & PR

## 커밋 메시지 형식

```
feat: 기능 설명

- 타입 변경사항
- 구현 내용
- 테스트 추가 개수

(#이슈번호)
```

## 디버깅 팁

**뉴스가 수집되지 않음**
```bash
# 캐시 초기화
rm -rf data/cache/

# 드라이런으로 테스트
DRY_RUN=true ./scripts/run.sh
```

**테스트 실패**
```bash
pytest tests/failing_test.py::test_name -vv
git log --oneline tests/failing_test.py  # 최근 변경 확인
```

## 참고

- **README.md** — 사용자 관점 (설치, 실행, 설정)
- **`git log --oneline -20`** — 과거 결정의 맥락
- **`git blame src/file.py`** — 특정 라인의 이유

---

**핵심**: 파이프라인 단계별 책임을 명확히 유지하고, 타입으로 데이터 흐름을 보호하고, 테스트 우선으로 개발한다.
