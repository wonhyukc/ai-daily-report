import importlib

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
