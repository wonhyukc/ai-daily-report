from pathlib import Path
from datetime import datetime
from src.utils import logger
from config.settings import REPORTS_DIR


class FileStorage:
    def __init__(self):
        self.reports_dir = REPORTS_DIR

    def save(self, html_content: str, report_date: datetime = None) -> Path:
        """Save HTML report to file"""
        if report_date is None:
            report_date = datetime.now()

        logger.info("Saving HTML report to file...")

        try:
            # Create filename with date
            filename = f"report-{report_date.strftime('%Y-%m-%d')}.html"
            filepath = self.reports_dir / filename

            # Write HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Report saved to: {filepath}")

            # Update latest.html symlink (Windows compatible)
            latest_path = self.reports_dir / "latest.html"
            if latest_path.exists():
                latest_path.unlink()

            # For Windows, we'll just copy instead of symlink
            with open(latest_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Latest report updated: {latest_path}")

            return filepath

        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise
