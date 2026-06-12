import sys
import io
import platform
from pathlib import Path
from loguru import logger
from config.settings import LOG_LEVEL, LOGS_DIR

IS_WINDOWS = platform.system() == "Windows"

# Windows 콘솔(cp949)에서 인코딩 불가한 이모지의 ASCII 대체 매핑.
# 파일 로그는 UTF-8이므로 콘솔 출력에만 적용한다.
EMOJI_FALLBACKS = {
    "✓": "[OK]",
    "✗": "[FAIL]",
    "⭐": "*",
    "📊": "",
    "🔥": "",
}


def _strip_emoji(message: str) -> str:
    """이모지를 ASCII 대체 문자로 치환 (한글 등 cp949 지원 문자는 유지)"""
    for emoji, fallback in EMOJI_FALLBACKS.items():
        message = message.replace(emoji, fallback)
    return message


def _console_format(record) -> str:
    """콘솔 전용 포맷 — Windows에서만 이모지를 치환한 메시지를 사용"""
    message = record["message"]
    if IS_WINDOWS:
        message = _strip_emoji(message)
    record["extra"]["console_message"] = message
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{extra[console_message]}</level>\n"
    )


# Remove default handler
logger.remove()

# Issue #2: Windows console encoding issue with emoji in logs
# Windows 콘솔은 기본 cp949 인코딩으로 UTF-8 이모지를 출력할 수 없음
# → stdout.buffer를 UTF-8로 래핑하여 해결
utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add console handler (Windows에서는 이모지를 ASCII로 치환)
logger.add(
    utf8_stdout,
    format=_console_format,
    level=LOG_LEVEL
)

# Add file handler (UTF-8 파일은 이모지 유지)
# pytest 환경에서는 등록하지 않는다 — 테스트 로그가 운영 일일 로그를 오염시켜
# pipeline-debugger의 진단 근거(단계별 count 라인)를 흐리기 때문 (#20)
if "pytest" not in sys.modules:
    log_file = LOGS_DIR / "report-{time:YYYY-MM-DD}.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=LOG_LEVEL,
        rotation="daily"
    )

__all__ = ["logger"]
