"""
Script to trigger news aggregation and data persistence without a running Flask server.
Used by GitHub Actions to update news_data.json.
"""

from services.news_client import NewsAPIClient
from services import data_service
from utils.logger import get_logger

logger = get_logger(__name__)

def update_news():
    client = NewsAPIClient()
    categories = ["business", "technology", "sports", "science"]
    
    all_transformed_articles = []
    
    for cat in categories:
        logger.info(f"Fetching headlines for category: {cat}")
        try:
            data = client.get_top_headlines(category=cat, page_size=20)
            articles = data_service.transform_articles(data, category=cat.capitalize())
            all_transformed_articles.extend(articles)
        except Exception as e:
            logger.error(f"Failed to fetch {cat}: {e}")

    if all_transformed_articles:
        logger.info(f"Saving {len(all_transformed_articles)} total articles.")
        data_service.save_to_json(all_transformed_articles)
        logger.info("Update complete.")
    else:
        logger.warning("No articles were fetched.")

if __name__ == "__main__":
    update_news()
