import sys
import io
from pathlib import Path
from loguru import logger
from config.settings import LOG_LEVEL, LOGS_DIR

# Remove default handler
logger.remove()

# Create UTF-8 wrapper for stdout
utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add console handler (without emoji to avoid encoding issues)
logger.add(
    utf8_stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL
)

# Add file handler
log_file = LOGS_DIR / "report-{time:YYYY-MM-DD}.log"
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=LOG_LEVEL,
    rotation="daily"
)

__all__ = ["logger"]
