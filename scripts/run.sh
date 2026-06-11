#!/usr/bin/env bash
# AI Daily Report 실행 스크립트 (macOS/Linux)
#
# 사용법:
#   ./scripts/run.sh              # 일반 실행
#   DRY_RUN=true ./scripts/run.sh # 드라이런 (파일 저장/캐시 커밋 안 함)
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    PYTHON="python3"
fi

exec "$PYTHON" src/main.py "$@"
