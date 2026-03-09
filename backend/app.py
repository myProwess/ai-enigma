"""
Flask application entry point for the NewsAPI aggregation backend.
"""

from flask import Flask, Response, jsonify
from flask_cors import CORS
from typing import Tuple

from routes.news_routes import news_bp
from utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(news_bp)

    # ── Global error handlers ────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error: Exception) -> Tuple[Response, int]:
        return jsonify({
            "status": "error",
            "code": "not_found",
            "message": "The requested resource was not found.",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error: Exception) -> Tuple[Response, int]:
        return jsonify({
            "status": "error",
            "code": "method_not_allowed",
            "message": "The HTTP method is not allowed for this endpoint.",
        }), 405

    @app.errorhandler(500)
    def internal_error(error: Exception) -> Tuple[Response, int]:
        logger.exception("Unhandled server error")
        return jsonify({
            "status": "error",
            "code": "internal_error",
            "message": "An unexpected internal server error occurred.",
        }), 500

    # ── Root route ───────────────────────────────────────────────────
    @app.route("/")
    def index() -> Tuple[Response, int]:
        return jsonify({
            "service": "NewsAPI Aggregation Backend",
            "version": "1.0.0",
            "endpoints": {
                "top_headlines": "/api/news/top-headlines",
                "category": "/api/news/category/<category>",
                "search": "/api/news/search?q=<query>",
                "saved": "/api/news/saved",
                "status": "/api/news/status",
            },
        }), 200

    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
