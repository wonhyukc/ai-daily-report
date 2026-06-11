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

## 📋 프로젝트 스킬

### project-enhancement-cycle
코드베이스 감시 → 이슈 해결 → 문서 정리의 순환을 반복하여 프로젝트를 지속적으로 개선합니다.

**자동 활성화:**
```
"프로젝트 개선 사이클"
"지속적 개선 해줘"
"완전 점검 후 정리"
```

**작동 방식:**
1. audit-to-issues: 코드베이스 감시 → 이슈 발견
2. issues-plan-and-resolve: 이슈 해결 (있을 때만)
3. docs-audit: 문서 정리
4. 반복: 새 이슈가 없을 때까지

**자세히:** `.claude/skills/project-enhancement-cycle/README.md`

### docs-audit
문서가 현재 상태만 정확히 표현하도록 점검하고 최적화합니다.

**자동 활성화:**
```
"현황 문서화 점검"
"문서 상태 점검"
"문서 최적화"
```

**3가지 원칙:**
1. 현재 상태만 표현 (과거 제거)
2. 문서 양 최소화 (중복 제거)
3. 역할별 분리 (README ≠ CLAUDE ≠ 코드)

**자세히:** `.claude/skills/docs-audit/README.md`

---

## 참고

- **README.md** — 사용자 관점 (설치, 실행, 설정)
- **`git log --oneline -20`** — 과거 결정의 맥락
- **`git blame src/file.py`** — 특정 라인의 이유
- **.claude/skills/docs-audit/** — 문서 감사 & 최적화 스킬

---

**핵심**: 파이프라인 단계별 책임을 명확히 유지하고, 타입으로 데이터 흐름을 보호하고, 테스트 우선으로 개발한다.
