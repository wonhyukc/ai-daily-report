from src.utils import contains_word


class TestContainsWord:
    def test_whole_word_matches(self):
        assert contains_word("New AI model released", "AI")

    def test_substring_inside_word_does_not_match(self):
        assert not contains_word("he said hello", "ai")
        assert not contains_word("fresh air today", "ai")
        assert not contains_word("they paid for it", "ai")

    def test_case_insensitive(self):
        assert contains_word("sponsored content", "Sponsored")

    def test_word_at_boundary_with_punctuation(self):
        assert contains_word("Is this an ad?", "ad")
        assert not contains_word("please read this", "ad")
        assert not contains_word("new adapter design", "ad")

    def test_multi_word_keyword(self):
        assert contains_word("advances in machine learning today", "machine learning")
        assert not contains_word("machine translation learning curve", "machine learning")
