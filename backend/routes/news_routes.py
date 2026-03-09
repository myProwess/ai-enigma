"""
Flask Blueprint defining all news-related API routes.
"""

from __future__ import annotations

from flask import Blueprint, Response, jsonify, request
from typing import Any, Dict, Tuple

from services.news_client import NewsAPIClient, NewsAPIError, RateLimitExceeded
from services import data_service
from utils.logger import get_logger

logger = get_logger(__name__)

news_bp = Blueprint("news", __name__, url_prefix="/api/news")


# ── Helper ───────────────────────────────────────────────────────────
def _error_response(
    message: str, status: int = 500, code: str = "error"
) -> Tuple[Response, int]:
    """Return a consistently structured JSON error."""
    return jsonify({"status": "error", "code": code, "message": message}), status


def _parse_pagination() -> Tuple[int, int]:
    """Extract page & page_size from query string with safe defaults."""
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = max(1, min(100, int(request.args.get("page_size", 20))))
    except (ValueError, TypeError):
        page_size = 20
    return page, page_size


# ── Routes ───────────────────────────────────────────────────────────
@news_bp.route("/top-headlines", methods=["GET"])
def top_headlines() -> Tuple[Response, int]:
    """
    GET /api/news/top-headlines
    Query params: country, category, sources, q, page, page_size
    """
    try:
        page, page_size = _parse_pagination()
        client = NewsAPIClient()

        data: Dict[str, Any] = client.get_top_headlines(
            country=request.args.get("country"),
            category=request.args.get("category"),
            sources=request.args.get("sources"),
            query=request.args.get("q"),
            page=page,
            page_size=page_size,
        )

        # Transform and persist
        category = request.args.get("category", "General").capitalize()
        articles = data_service.transform_articles(data, category=category)
        saved_path = data_service.save_to_json(articles)

        return jsonify({
            "status": "ok",
            "totalResults": data.get("totalResults", 0),
            "page": page,
            "page_size": page_size,
            "articles": articles,
            "saved_to": saved_path,
            "remaining_requests": client.remaining_requests,
        }), 200

    except RateLimitExceeded as exc:
        logger.warning("Rate limit hit: %s", exc)
        return _error_response(str(exc), status=429, code="rateLimited")
    except NewsAPIError as exc:
        return _error_response(str(exc), status=exc.status, code=exc.code)
    except Exception as exc:
        logger.exception("Unexpected error in /top-headlines")
        return _error_response(f"Internal server error: {exc}", status=500)


@news_bp.route("/category/<string:category>", methods=["GET"])
def category_headlines(category: str) -> Tuple[Response, int]:
    """
    GET /api/news/category/<category>
    Shortcut for top-headlines filtered by category.
    Valid categories: business, entertainment, general, health, science, sports, technology
    """
    valid_categories = {
        "business", "entertainment", "general",
        "health", "science", "sports", "technology",
    }
    if category.lower() not in valid_categories:
        return _error_response(
            f"Invalid category '{category}'. Must be one of: {', '.join(sorted(valid_categories))}",
            status=400,
            code="invalid_category",
        )

    try:
        page, page_size = _parse_pagination()
        client = NewsAPIClient()

        data: Dict[str, Any] = client.get_top_headlines(
            country=request.args.get("country"),
            category=category.lower(),
            page=page,
            page_size=page_size,
        )

        articles = data_service.transform_articles(data, category=category.capitalize())
        data_service.save_to_json(articles)

        return jsonify({
            "status": "ok",
            "category": category.lower(),
            "totalResults": data.get("totalResults", 0),
            "page": page,
            "page_size": page_size,
            "articles": articles,
            "remaining_requests": client.remaining_requests,
        }), 200

    except RateLimitExceeded as exc:
        logger.warning("Rate limit hit: %s", exc)
        return _error_response(str(exc), status=429, code="rateLimited")
    except NewsAPIError as exc:
        return _error_response(str(exc), status=exc.status, code=exc.code)
    except Exception as exc:
        logger.exception("Unexpected error in /category/%s", category)
        return _error_response(f"Internal server error: {exc}", status=500)


@news_bp.route("/search", methods=["GET"])
def search_everything() -> Tuple[Response, int]:
    """
    GET /api/news/search
    Query params: q, sources, domains, from_date, to_date, language, sort_by, page, page_size
    """
    query = request.args.get("q")
    if not query:
        return _error_response(
            "Query parameter 'q' is required for search", status=400, code="missing_query"
        )

    try:
        page, page_size = _parse_pagination()
        client = NewsAPIClient()

        data: Dict[str, Any] = client.get_everything(
            query=query,
            sources=request.args.get("sources"),
            domains=request.args.get("domains"),
            from_date=request.args.get("from_date"),
            to_date=request.args.get("to_date"),
            language=request.args.get("language"),
            sort_by=request.args.get("sort_by"),
            page=page,
            page_size=page_size,
        )

        articles = data_service.transform_articles(data)
        data_service.save_to_json(articles)

        return jsonify({
            "status": "ok",
            "query": query,
            "totalResults": data.get("totalResults", 0),
            "page": page,
            "page_size": page_size,
            "articles": articles,
            "remaining_requests": client.remaining_requests,
        }), 200

    except RateLimitExceeded as exc:
        logger.warning("Rate limit hit: %s", exc)
        return _error_response(str(exc), status=429, code="rateLimited")
    except NewsAPIError as exc:
        return _error_response(str(exc), status=exc.status, code=exc.code)
    except Exception as exc:
        logger.exception("Unexpected error in /search")
        return _error_response(f"Internal server error: {exc}", status=500)


@news_bp.route("/saved", methods=["GET"])
def saved_articles() -> Tuple[Response, int]:
    """
    GET /api/news/saved
    Returns all articles previously saved to news_data.json.
    """
    try:
        articles = data_service.load_from_json()
        return jsonify({
            "status": "ok",
            "totalResults": len(articles),
            "articles": articles,
        }), 200
    except Exception as exc:
        logger.exception("Unexpected error in /saved")
        return _error_response(f"Internal server error: {exc}", status=500)


@news_bp.route("/status", methods=["GET"])
def api_status() -> Tuple[Response, int]:
    """
    GET /api/news/status
    Health-check endpoint showing remaining API quota.
    """
    try:
        client = NewsAPIClient()
        return jsonify({
            "status": "ok",
            "remaining_requests": client.remaining_requests,
            "daily_limit": client._daily_limit,
        }), 200
    except Exception as exc:
        return _error_response(str(exc), status=500)
