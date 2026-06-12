import importlib
from datetime import datetime

from config.settings import LOGS_DIR

# src.utils.__init__이 loguru 객체 `logger`를 노출해 서브모듈 이름을 가리므로
# importlib로 모듈 자체를 가져온다
logger_module = importlib.import_module("src.utils.logger")


class TestStripEmoji:
    """이슈 #2: Windows 콘솔(cp949)에서 깨지는 이모지를 ASCII로 치환"""

    def test_known_emoji_replaced_with_ascii(self):
        assert logger_module._strip_emoji("✓ saved") == "[OK] saved"
        assert logger_module._strip_emoji("✗ failed") == "[FAIL] failed"

    def test_plain_text_unchanged(self):
        assert logger_module._strip_emoji("plain message") == "plain message"

    def test_korean_text_preserved(self):
        # cp949는 한글을 지원하므로 한글은 건드리지 않아야 함
        assert logger_module._strip_emoji("리포트 저장 완료 ✓") == "리포트 저장 완료 [OK]"


class TestPytestDoesNotPolluteDailyLog:
    """이슈 #20: pytest 환경에서는 파일 핸들러가 등록되지 않아야 한다.

    logger.py는 import 시점에 운영 일일 로그(data/logs/report-YYYY-MM-DD.log)
    파일 핸들러를 무조건 등록한다. 그 결과 pytest가 src 모듈을 import하기만
    해도 테스트 로그가 운영 로그 파일에 기록되어 오염된다.

    기대 동작: "pytest" in sys.modules 이면 파일 핸들러를 등록하지 않는다
    (콘솔 핸들러는 유지). 따라서 pytest 안에서 logger로 로그를 찍어도
    일일 로그 파일의 크기가 증가하지 않아야 한다.
    """

    def test_logging_in_pytest_does_not_write_to_daily_log_file(self):
        # loguru의 file sink는 쓰기 시점의 로컬 시간으로 파일명을 결정한다
        log_file = LOGS_DIR / f"report-{datetime.now():%Y-%m-%d}.log"
        size_before = log_file.stat().st_size if log_file.exists() else 0

        logger_module.logger.info("issue #20 — pytest log pollution probe")

        size_after = log_file.stat().st_size if log_file.exists() else 0
        assert size_after == size_before, (
            f"pytest에서 찍은 로그가 운영 일일 로그 파일에 기록됨: "
            f"{log_file} 크기 {size_before} -> {size_after} "
            f"(+{size_after - size_before} bytes)"
        )


class TestConsoleFormat:
    def test_windows_console_message_is_stripped(self, monkeypatch):
        monkeypatch.setattr(logger_module, "IS_WINDOWS", True)
        record = {"message": "✓ saved", "extra": {}}
        logger_module._console_format(record)
        assert record["extra"]["console_message"] == "[OK] saved"

    def test_non_windows_console_message_unchanged(self, monkeypatch):
        monkeypatch.setattr(logger_module, "IS_WINDOWS", False)
        record = {"message": "✓ saved", "extra": {}}
        logger_module._console_format(record)
        assert record["extra"]["console_message"] == "✓ saved"
