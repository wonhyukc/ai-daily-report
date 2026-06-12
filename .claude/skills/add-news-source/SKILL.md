---
name: add-news-source
description: 새 뉴스 소스(수집기)를 추가하는 정형 절차. 새 수집기 추가, RSS 피드 추가, 뉴스 소스 확장 요청 시 사용. 타입 정의 → 설정 → 구현 → 테스트 순서를 보장한다.
argument-hint: [source-name]
---

# 새 뉴스 소스 추가 절차

대상 소스: $ARGUMENTS

## 사전 판단

- **단순 RSS 피드 추가**라면 코드 작성 불필요: `config/settings.py`의 `NEWS_SOURCES["rss_feeds"]["feeds"]`에 URL만 추가하고, 피드가 살아있는지 확인(`curl -sI <url>`) 후 종료.
- **새 수집기 클래스**가 필요한 경우(전용 API 등)에만 아래 절차 진행.

## 절차 (Red-Green-Refactor)

1. **설정 정의** — `config/settings.py`의 `NEWS_SOURCES`에 새 소스 블록 추가:
   ```python
   "newsource": {
       "enabled": True,
       "max_items": 30,
       # 소스별 세부 설정 (하드코딩 금지 — 수집기는 이 설정을 읽어야 함)
   },
   ```

2. **테스트 먼저 (RED)** — `tests/test_<source>_collector.py` 작성. tdd-test-writer 에이전트에 위임 가능.
   - 네트워크 mock 필수 (전체 스위트 0.2초 유지)
   - 검증 항목: NewsItem 반환 타입, published_at UTC aware, 빈 응답 시 빈 리스트(크래시 금지), 설정값 반영

3. **구현 (GREEN)** — `src/collectors/<source>_collector.py`:
   - `BaseCollector` 상속 (src/collectors/base.py), `collect() -> List[NewsItem]` 구현
   - 예외는 잡아서 logger.error 후 빈 리스트 반환 (CollectorManager가 병렬 실행하므로 한 소스 실패가 전체를 죽이면 안 됨)
   - dead source 감지 시 logger.warning (silent failure 금지 — #14 교훈)

4. **등록** — `src/collectors/collector_manager.py`의 `_init_collectors()`에 enabled 분기 추가.

5. **검증**:
   ```bash
   ./venv/bin/pytest                      # 기존 + 신규 모두 통과
   DRY_RUN=true ./scripts/run.sh          # 실제 수집 드라이런
   ```

6. **문서 동기화** — README의 수집량 표와 기능 목록에 새 소스 반영 (수치-설정 불일치가 반복된 문서 부패 지점).

7. **랭킹 가중치** — `src/processors/ranker.py`의 `source_weights`에 새 소스 가중치 추가 (없으면 기본 1.0).
