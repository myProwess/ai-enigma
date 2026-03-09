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


def _clean_content(raw_content: str | None, description: str | None) -> str | None:
    """
    Build the best possible content from NewsAPI fields.

    The free-tier /top-headlines truncates `content` to ~200 chars with a
    '[+NNNN chars]' suffix.  We strip that marker, and if the remaining text
    is shorter than the `description`, prefer the description instead.
    """
    import re

    cleaned = None
    if raw_content:
        # Remove the truncation marker e.g. "... [+1234 chars]"
        cleaned = re.sub(r"\s*\[\+\d+ chars\]\s*$", "", raw_content).strip()

    desc = (description or "").strip()

    # Pick whichever is longer / more informative
    if cleaned and desc:
        return cleaned if len(cleaned) >= len(desc) else desc
    return cleaned or desc or None


def _slugify(text: str, max_length: int = 80) -> str:
    """Convert a title into a URL- and filesystem-safe slug."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)   # strip non-alphanumerics
    slug = re.sub(r"[\s]+", "-", slug)           # spaces → hyphens
    slug = re.sub(r"-{2,}", "-", slug)           # collapse multiple hyphens
    slug = slug.strip("-")                        # trim leading/trailing hyphens
    return slug[:max_length]


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
        if not title or title == "[Removed]":
            continue  # skip removed / empty articles

        slug = _slugify(title)

        description = article.get("description")
        raw_content = article.get("content")
        content = _clean_content(raw_content, description)

        transformed.append({
            "id": f"api-{idx}-{int(datetime.now().timestamp())}",
            "title": title,
            "slug": slug,
            "excerpt": description or (content[:200] + "..." if content and len(content) > 200 else content),
            "content": content,
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
    Persist articles to a JSON file with atomic write.

    Replaces the entire file with the supplied articles (deduped by URL
    within the batch).  The caller is responsible for capping the count.

    Args:
        articles:  List of transformed article dicts.
        filepath:  Target file path (defaults to Config.DATA_FILE_PATH).

    Returns:
        The absolute path to the written file.
    """
    filepath = filepath or Config.DATA_FILE_PATH

    # Deduplicate within the incoming batch by URL
    seen_urls: set[str] = set()
    unique_articles: List[Dict[str, Any]] = []
    for a in articles:
        url = a.get("url", "")
        if url and url in seen_urls:
            continue
        seen_urls.add(url)
        unique_articles.append(a)

    logger.info(
        "Saving %d articles (%d deduplicated) to %s",
        len(unique_articles), len(articles) - len(unique_articles), filepath,
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
                    "total_articles": len(unique_articles),
                    "articles": unique_articles,
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
