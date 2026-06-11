#!/usr/bin/env python3
"""
AI Daily Report - Main Entry Point
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors import CollectorManager
from src.processors import ProcessorPipeline
from src.generators import HTMLGenerator
from src.delivery import FileStorage
from src.analyzers import TrendDetector
from src.utils import logger
from config.settings import DRY_RUN


def main():
    """Main execution pipeline"""
    logger.info("=" * 60)
    logger.info("AI Daily Report - Starting pipeline")
    logger.info("=" * 60)

    try:
        # Step 1: Collect news
        logger.info("\n[Step 1/5] Collecting news from sources...")
        collector_manager = CollectorManager()
        raw_items = collector_manager.collect_all()

        if not raw_items:
            logger.warning("No items collected!")
            return False

        # Step 2: Process items
        logger.info("\n[Step 2/5] Processing items...")
        processor = ProcessorPipeline()
        processed_items = processor.process(raw_items)

        if not processed_items:
            logger.warning("No items after processing!")
            return False

        # Step 3: Detect trends
        logger.info("\n[Step 3/5] Analyzing trends...")
        trend_detector = TrendDetector()
        trends = trend_detector.detect_trends(processed_items)

        # Step 4: Generate HTML
        logger.info("\n[Step 4/5] Generating HTML report...")
        html_generator = HTMLGenerator()
        html_content = html_generator.generate(processed_items)

        # Step 5: Save/Deliver
        logger.info("\n[Step 5/5] Saving report...")
        if not DRY_RUN:
            file_storage = FileStorage()
            report_path = file_storage.save(html_content)
            # 저장 성공 후에만 dedup 캐시 커밋 (실패/드라이런 시 기사 유실 방지)
            processor.commit_cache()
            logger.info(f"\n✓ Report successfully generated: {report_path}")
        else:
            logger.info("\n[DRY RUN] Would save report and commit dedup cache (DRY_RUN=true)")

        logger.info("=" * 60)
        logger.info(f"Pipeline completed successfully!")
        logger.info(f"Total items processed: {len(processed_items)}")
        logger.info(f"Top keywords: {[k['keyword'] for k in trends['top_keywords'][:5]]}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
