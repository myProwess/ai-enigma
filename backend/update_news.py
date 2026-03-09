"""
Script to trigger news aggregation and data persistence without a running Flask server.
Used by GitHub Actions to update news_data.json.

Priority order:
  1. Google News India  (source-based)
  2. TechCrunch         (source-based)
  3. The Verge          (source-based)
  4. Category headlines  (business, technology, sports, science)
  5. Politics           (/everything)

Total articles are capped at MAX_ARTICLES (100).
"""

from services.news_client import NewsAPIClient
from services import data_service
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_ARTICLES = 100


def update_news():
    client = NewsAPIClient()
    all_transformed_articles: list = []

    def _remaining() -> int:
        return max(0, MAX_ARTICLES - len(all_transformed_articles))

    # ── Priority 1: Source-based feeds (ordered by importance) ─────────
    #    `sources` cannot be mixed with `country`/`category` params
    source_feeds = [
        {"sources": "google-news-in", "label": "Technology", "size": 25},
        {"sources": "techcrunch",     "label": "Technology", "size": 20},
        {"sources": "the-verge",      "label": "Technology", "size": 10},
    ]

    for feed in source_feeds:
        if _remaining() <= 0:
            break
        page_size = min(feed["size"], _remaining())
        logger.info(f"[Priority] Fetching {page_size} headlines from: {feed['sources']}")
        try:
            data = client.get_top_headlines(sources=feed["sources"], page_size=page_size)
            articles = data_service.transform_articles(data, category=feed["label"])
            all_transformed_articles.extend(articles[:_remaining()])
        except Exception as e:
            logger.error(f"Failed to fetch source {feed['sources']}: {e}")

    # ── Priority 2: Category-based headlines (country=us) ─────────────
    categories = ["business", "technology", "sports", "science"]

    for cat in categories:
        if _remaining() <= 0:
            break
        page_size = min(10, _remaining())
        logger.info(f"Fetching {page_size} headlines for category: {cat}")
        try:
            data = client.get_top_headlines(category=cat, page_size=page_size)
            articles = data_service.transform_articles(data, category=cat.capitalize())
            all_transformed_articles.extend(articles[:_remaining()])
        except Exception as e:
            logger.error(f"Failed to fetch {cat}: {e}")

    # ── Priority 3: Politics via /everything ──────────────────────────
    if _remaining() > 0:
        logger.info(f"Fetching {_remaining()} politics articles via /everything")
        try:
            data = client.get_everything(
                query="politics OR government OR election",
                language="en",
                sort_by="publishedAt",
                page_size=min(10, _remaining()),
            )
            articles = data_service.transform_articles(data, category="Politics")
            all_transformed_articles.extend(articles[:_remaining()])
        except Exception as e:
            logger.error(f"Failed to fetch politics: {e}")

    # ── Persist (hard cap at MAX_ARTICLES) ────────────────────────────
    final_articles = all_transformed_articles[:MAX_ARTICLES]
    if final_articles:
        logger.info(f"Saving {len(final_articles)} articles (cap: {MAX_ARTICLES}).")
        data_service.save_to_json(final_articles)
        logger.info("Update complete.")
    else:
        logger.warning("No articles were fetched.")


if __name__ == "__main__":
    update_news()
