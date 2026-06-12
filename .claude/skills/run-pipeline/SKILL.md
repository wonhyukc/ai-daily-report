---
name: run-pipeline
description: AI Daily Report 파이프라인을 실행하고 결과를 검증합니다. 리포트 생성, 파이프라인 동작 확인, 드라이런 테스트 요청 시 사용.
argument-hint: [--dry]
disable-model-invocation: true
---

# 파이프라인 실행 & 검증

## 현재 환경 상태

### dedup 캐시
!`ls -la data/cache/ 2>/dev/null && wc -l data/cache/url_hashes.txt 2>/dev/null || echo "캐시 없음 (첫 실행)"`

### 최근 리포트
!`ls -t reports/*.html 2>/dev/null | head -3 || echo "리포트 없음"`

## 실행 절차

1. **실행 모드 결정**: 인자가 `--dry`이면 드라이런(파일 저장·캐시 커밋 없음), 없으면 실제 실행.
   ```bash
   # 드라이런
   DRY_RUN=true ./scripts/run.sh
   # 실제 실행 (캐시가 커밋되므로 같은 기사는 24h 내 재수집 안 됨에 유의)
   ./scripts/run.sh
   ```
   인자: $ARGUMENTS

2. **결과 검증** (실행 후 반드시 확인):
   - 종료 코드 0인지
   - 로그에서 단계별 count: `Total collected` → `After deduplication` → `After filtering` → `Final item count`
   - 어느 단계에서 count가 0으로 떨어지면 **pipeline-debugger 에이전트로 진단 위임**
   - 실제 실행이면 `reports/report-YYYY-MM-DD.html` 생성 + `latest.html` 갱신 확인

3. **보고**: 단계별 item count 표와 리포트 경로(또는 드라이런 결과)를 사용자에게 보고.

## 주의

- 실제 실행은 dedup 캐시를 커밋하는 부수효과가 있다. 테스트 목적이면 반드시 `--dry`를 권할 것.
- 수집 결과가 평소(수십 건)보다 현저히 적으면 dead feed 가능성 — 경고 로그 확인.
