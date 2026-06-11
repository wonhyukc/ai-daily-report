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

    def test_original_fields_are_preserved(self, make_item):
        items = [make_item(title="ChatGPT update", url="https://example.com/x")]
        result = Classifier().classify_items(items)
        assert result[0]["title"] == "ChatGPT update"
        assert result[0]["url"] == "https://example.com/x"
