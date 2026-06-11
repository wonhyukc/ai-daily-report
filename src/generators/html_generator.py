from typing import List
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from src.processors.models import ProcessedItem
from src.utils import logger
from config.settings import TEMPLATES_DIR


class HTMLGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        self.env.autoescape = True

    def generate(self, items: List[ProcessedItem], trends: dict = None, report_date: datetime = None) -> str:
        """Generate HTML report from processed items and trend analysis"""
        # Issue #4: Trend analysis computed but never included in the HTML report
        # trends 파라미터로 트렌드 분석 결과를 HTML 템플릿에 포함
        if report_date is None:
            report_date = datetime.now()

        logger.info("Generating HTML report...")

        try:
            template = self.env.get_template("report.html")

            # Group items by category
            items_by_category = self._group_items(items)

            # Take top N items per category (safe sorting with None check)
            # published_at은 UTC aware — fallback도 aware로 맞춰 비교 오류 방지
            def get_published_date(x):
                return x.published_at or datetime.now(timezone.utc)

            breaking_news = sorted(items[:10], key=get_published_date, reverse=True)

            context = {
                'report_date': report_date,
                'total_items': len(items),
                'breaking_news': breaking_news,
                'items_by_category': items_by_category,
                'all_items': items,
                'trends': trends,
            }

            html_content = template.render(**context)
            logger.info("HTML generation complete")
            return html_content

        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            raise

    def _group_items(self, items: List[ProcessedItem]) -> dict:
        """Group items by category"""
        grouped = {}
        for item in items:
            for category in (item.categories or ['Other']):
                if category not in grouped:
                    grouped[category] = []
                grouped[category].append(item)

        # Sort by importance within each category
        for category in grouped:
            grouped[category].sort(
                key=lambda x: x.importance_score,
                reverse=True
            )

        return grouped
