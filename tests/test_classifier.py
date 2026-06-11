from src.processors.classifier import Classifier


class TestClassifier:
    def test_single_category_match(self, make_item):
        items = [make_item(title="ChatGPT releases new version", description="")]
        result = Classifier().classify_items(items)
        assert "GenerativeAI" in result[0]["categories"]

    def test_multiple_categories(self, make_item):
        items = [
            make_item(
                title="ChatGPT security flaw discovered",
                description="adversarial prompt issue",
            )
        ]
        result = Classifier().classify_items(items)
        assert "GenerativeAI" in result[0]["categories"]
        assert "Security" in result[0]["categories"]

    def test_unmatched_item_goes_to_other(self, make_item):
        items = [make_item(title="Weekly cooking recipes", description="pasta dishes")]
        result = Classifier().classify_items(items)
        assert result[0]["categories"] == ["Other"]

    def test_substring_does_not_trigger_category(self, make_item):
        # 이슈 #6: "paper" ⊂ "Newspaper"가 Research로 분류되면 안 됨
        items = [make_item(title="Newspaper industry digitization", description="")]
        result = Classifier().classify_items(items)
        assert result[0]["categories"] == ["Other"]

    def test_plural_keyword_still_matches(self, make_item):
        # "GPU" 키워드가 "GPUs"에도 매칭되어야 함
        items = [make_item(title="New GPUs for datacenters", description="")]
        result = Classifier().classify_items(items)
        assert "Infrastructure" in result[0]["categories"]

    def test_original_fields_are_preserved(self, make_item):
        items = [make_item(title="ChatGPT update", url="https://example.com/x")]
        result = Classifier().classify_items(items)
        assert result[0]["title"] == "ChatGPT update"
        assert result[0]["url"] == "https://example.com/x"
