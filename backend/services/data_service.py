"""
Data service for transforming API responses and persisting to JSON.
Handles article normalisation, deduplication, and atomic file writes.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def transform_articles(raw_response: Dict[str, Any], category: str = "Technology") -> List[Dict[str, Any]]:
    """
    Extract and normalise article data from a raw NewsAPI response.

    Args:
        raw_response: The raw JSON dict returned by the NewsAPI.

    Returns:
        A list of cleaned article dicts with consistent field names.
    """
    articles: List[Dict[str, Any]] = raw_response.get("articles", [])
    transformed: List[Dict[str, Any]] = []

    for idx, article in enumerate(articles):
        source: Dict[str, Any] = article.get("source") or {}
        # Generate a slug from title
        title = article.get("title", "")
        slug = title.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("!", "").replace(".", "")[:50]
        
        transformed.append({
            "id": f"api-{idx}-{int(datetime.now().timestamp())}",
            "title": title,
            "slug": slug,
            "excerpt": article.get("description", ""),
            "content": article.get("content", ""),
            "author": article.get("author") or source.get("name", "Unknown"),
            "publishDate": article.get("publishedAt"),
            "coverImageUrl": article.get("urlToImage"),
            "category": category,
            "url": article.get("url", ""),
        })

    logger.info("Transformed %d articles from API response", len(transformed))
    return transformed


def save_to_json(
    articles: List[Dict[str, Any]],
    filepath: Optional[str] = None,
) -> str:
    """
    Persist articles to a JSON file with atomic write and deduplication.

    New articles are merged with existing data; duplicates (by URL) are skipped.

    Args:
        articles:  List of transformed article dicts.
        filepath:  Target file path (defaults to Config.DATA_FILE_PATH).

    Returns:
        The absolute path to the written file.
    """
    filepath = filepath or Config.DATA_FILE_PATH

    # Load existing data for deduplication
    existing = load_from_json(filepath)
    existing_urls: set[str] = {a["url"] for a in existing if a.get("url")}

    new_articles = [a for a in articles if a.get("url") and a["url"] not in existing_urls]
    merged = existing + new_articles

    logger.info(
        "Saving %d articles (%d new, %d existing) to %s",
        len(merged), len(new_articles), len(existing), filepath,
    )

    # Atomic write: write to temp file then rename
    dir_name = os.path.dirname(filepath) or "."
    os.makedirs(dir_name, exist_ok=True)

    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            json.dump(
                {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_articles": len(merged),
                    "articles": merged,
                },
                tmp_file,
                indent=2,
                ensure_ascii=False,
            )
        # On Windows, os.rename fails if dest exists — use os.replace instead
        os.replace(tmp_path, filepath)
        logger.info("JSON file written successfully: %s", filepath)
    except (OSError, IOError) as exc:
        logger.error("Failed to write JSON file: %s", exc)
        # Clean up temp file on failure
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    return os.path.abspath(filepath)


def load_from_json(
    filepath: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Load previously saved articles from a JSON file.

    Args:
        filepath: Path to the JSON file (defaults to Config.DATA_FILE_PATH).

    Returns:
        A list of article dicts, or an empty list if the file doesn't exist.
    """
    filepath = filepath or Config.DATA_FILE_PATH

    if not os.path.exists(filepath):
        logger.debug("No existing data file at %s", filepath)
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        articles: List[Dict[str, Any]] = data.get("articles", [])
        logger.info("Loaded %d existing articles from %s", len(articles), filepath)
        return articles
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read existing data file: %s", exc)
        return []
