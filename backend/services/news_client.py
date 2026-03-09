"""
Singleton NewsAPI client service.
Handles API communication, rate-limit tracking, and pagination.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsAPIClient:
    """
    Thread-safe Singleton client for the NewsAPI.

    Usage:
        client = NewsAPIClient()
        response = client.get_top_headlines(country="us", category="technology")
    """

    _instance: Optional[NewsAPIClient] = None
    _lock: threading.Lock = threading.Lock()

    # ── Singleton ────────────────────────────────────────────────────
    def __new__(cls) -> NewsAPIClient:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized: bool = True

        Config.validate()

        self._session: requests.Session = requests.Session()
        self._session.headers.update({
            "X-Api-Key": Config.NEWS_API_KEY,
            "Accept": "application/json",
        })
        self._base_url: str = Config.NEWS_API_BASE_URL
        self._daily_limit: int = Config.DAILY_REQUEST_LIMIT
        self._request_count: int = 0
        self._count_reset_date: str = self._today()

        logger.info("NewsAPIClient initialised (daily limit: %d)", self._daily_limit)

    # ── Rate-limit helpers ───────────────────────────────────────────
    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _check_and_increment(self) -> None:
        """Reset counter at midnight UTC and enforce daily limit."""
        today = self._today()
        if today != self._count_reset_date:
            logger.info("Daily counter reset (new day: %s)", today)
            self._request_count = 0
            self._count_reset_date = today

        if self._request_count >= self._daily_limit:
            remaining = self._daily_limit - self._request_count
            raise RateLimitExceeded(
                f"Daily request limit reached ({self._daily_limit}). "
                f"Remaining: {remaining}. Resets at midnight UTC."
            )
        self._request_count += 1
        logger.debug(
            "Request %d / %d for %s",
            self._request_count, self._daily_limit, self._count_reset_date,
        )

    @property
    def remaining_requests(self) -> int:
        today = self._today()
        if today != self._count_reset_date:
            return self._daily_limit
        return max(0, self._daily_limit - self._request_count)

    # ── Core request ─────────────────────────────────────────────────
    def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GET request against the NewsAPI."""
        self._check_and_increment()
        url = f"{self._base_url}/{endpoint}"

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        logger.info("GET %s params=%s", url, params)

        try:
            response = self._session.get(url, params=params, timeout=15)
            data: Dict[str, Any] = response.json()

            if response.status_code == 429:
                raise RateLimitExceeded("NewsAPI returned 429 Too Many Requests")

            if response.status_code != 200 or data.get("status") != "ok":
                error_msg = data.get("message", response.text)
                error_code = data.get("code", "unknown")
                logger.error("API error [%s]: %s", error_code, error_msg)
                raise NewsAPIError(
                    message=error_msg,
                    code=error_code,
                    status=response.status_code,
                )

            logger.info(
                "Success — totalResults: %s", data.get("totalResults", "N/A")
            )
            return data

        except requests.exceptions.Timeout:
            logger.error("Request to %s timed out", url)
            raise NewsAPIError("Request timed out", code="timeout", status=408)
        except requests.exceptions.ConnectionError:
            logger.error("Connection error reaching %s", url)
            raise NewsAPIError("Connection error", code="connection_error", status=503)
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error: %s", exc)
            raise NewsAPIError(str(exc), code="request_error", status=500)

    # ── Public endpoints ─────────────────────────────────────────────
    def get_top_headlines(
        self,
        country: Optional[str] = None,
        category: Optional[str] = None,
        sources: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Fetch top headlines from NewsAPI.

        Args:
            country:   2-letter ISO 3166-1 country code (default from config).
            category:  One of business, entertainment, general, health, science, sports, technology.
            sources:   Comma-separated source identifiers (cannot mix with country/category).
            query:     Keywords to filter headlines.
            page:      Page number (1-indexed).
            page_size: Results per page (max 100).

        Returns:
            Raw API response dict with status, totalResults, and articles.
        """
        if not sources and not country:
            country = Config.DEFAULT_COUNTRY

        params: Dict[str, Any] = {
            "country": country if not sources else None,
            "category": category if not sources else None,
            "sources": sources,
            "q": query,
            "page": page,
            "pageSize": min(page_size or Config.DEFAULT_PAGE_SIZE, Config.MAX_PAGE_SIZE),
        }
        return self._get("top-headlines", params)

    def get_everything(
        self,
        query: Optional[str] = None,
        sources: Optional[str] = None,
        domains: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search through all articles via the /everything endpoint.

        Args:
            query:      Keywords or phrase to search.
            sources:    Comma-separated source identifiers.
            domains:    Comma-separated domains to restrict search.
            from_date:  Oldest article date (ISO 8601).
            to_date:    Newest article date (ISO 8601).
            language:   2-letter ISO-639-1 language code.
            sort_by:    One of relevancy, popularity, publishedAt.
            page:       Page number (1-indexed).
            page_size:  Results per page (max 100).

        Returns:
            Raw API response dict.
        """
        params: Dict[str, Any] = {
            "q": query,
            "sources": sources,
            "domains": domains,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sort_by,
            "page": page,
            "pageSize": min(page_size or Config.DEFAULT_PAGE_SIZE, Config.MAX_PAGE_SIZE),
        }
        return self._get("everything", params)

    def fetch_all_pages(
        self,
        endpoint_method: str,
        max_pages: int = 5,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Auto-paginate through results up to max_pages.

        Args:
            endpoint_method: Either 'top_headlines' or 'everything'.
            max_pages:       Maximum number of pages to fetch.
            **kwargs:        Parameters forwarded to the endpoint method.

        Returns:
            Aggregated list of article dicts.
        """
        method = getattr(self, f"get_{endpoint_method}")
        all_articles: List[Dict[str, Any]] = []

        for page_num in range(1, max_pages + 1):
            kwargs["page"] = page_num
            data = method(**kwargs)
            articles = data.get("articles", [])
            all_articles.extend(articles)

            total = data.get("totalResults", 0)
            page_size = kwargs.get("page_size") or Config.DEFAULT_PAGE_SIZE
            if page_num * page_size >= total:
                logger.info("All pages fetched (%d articles)", len(all_articles))
                break

        return all_articles


# ── Custom exceptions ────────────────────────────────────────────────
class NewsAPIError(Exception):
    """Raised when the NewsAPI returns an error response."""

    def __init__(
        self, message: str, code: str = "unknown", status: int = 500
    ) -> None:
        super().__init__(message)
        self.code: str = code
        self.status: int = status


class RateLimitExceeded(NewsAPIError):
    """Raised when the daily request quota is exhausted."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, code="rateLimited", status=429)
