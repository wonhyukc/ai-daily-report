import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = DATA_DIR / "logs"

# Ensure directories exist
for d in [CACHE_DIR, LOGS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# News Sources Configuration
NEWS_SOURCES = {
    "hackernews": {
        "enabled": True,
        "max_stories": 30,
        "base_url": "https://hacker-news.firebaseio.com/v0"
    },
    "arxiv": {
        "enabled": True,
        "categories": ["cs.AI", "cs.LG", "stat.ML"],
        "max_results": 50,
    },
    "rss_feeds": {
        "enabled": True,
        "feeds": [
            "https://feeds.bloomberg.com/news/tech.rss",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://feeds.techcrunch.com/techcrunch/",
        ]
    },
}

# Processing Settings
PROCESSING = {
    "min_word_count": 50,        # 설명이 있는 항목의 최소 단어 수
    "cache_ttl_hours": 24,       # dedup 캐시 보관 기간
    "exclude_keywords": ["advertisement", "sponsored", "ad"],
}

# LLM Settings (Claude) — Phase 2 예정
LLM_CONFIG = {
    "model": "claude-opus-4-8",
    "max_tokens": 500,
    "timeout": 30,
}

# Report Settings
REPORT_SETTINGS = {
    "timezone": os.getenv("REPORT_TIMEZONE", "Asia/Seoul"),
    "time": os.getenv("REPORT_TIME", "06:00"),
    "include_sections": [
        "breaking_news",
        "trend_analysis",
        "action_items",
        "competitor_analysis"
    ]
}

# Email Settings (for Phase 2)
EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": os.getenv("SMTP_SERVER", ""),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "from_address": os.getenv("SMTP_USERNAME", ""),
    # 빈 문자열일 때 [""]가 되지 않도록 공백 항목 제거
    "to_addresses": [
        addr.strip()
        for addr in os.getenv("EMAIL_RECIPIENTS", "").split(",")
        if addr.strip()
    ],
    "subject_template": "📊 AI Daily Report - {date}"
}

# Slack Settings (for Phase 3)
SLACK_CONFIG = {
    "enabled": False,
    "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
}

# Logging (파일 경로는 src/utils/logger.py에서 관리)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Application
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Category Definitions
CATEGORIES = {
    "GenerativeAI": ["GPT", "ChatGPT", "DALL-E", "generative", "text-to-image"],
    "LLM": ["LLM", "language model", "transformer", "neural network", "embedding"],
    "Enterprise": ["enterprise", "business", "corporate", "B2B", "SaaS"],
    "Security": ["security", "safety", "privacy", "adversarial", "attack"],
    "Infrastructure": ["GPU", "TPU", "infrastructure", "compute", "cloud", "edge"],
    "Application": ["application", "product", "tool", "platform", "service"],
    "Research": ["paper", "research", "study", "arxiv", "benchmark"],
    "Regulation": ["regulation", "policy", "law", "compliance", "governance"],
}

# Competitor List
COMPETITORS = [
    "OpenAI", "Google", "Microsoft", "Amazon",
    "Meta", "Anthropic", "Cohere", "Hugging Face",
    "Mistral", "Apple", "NVIDIA", "Tesla"
]
