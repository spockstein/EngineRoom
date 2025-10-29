from fastapi import APIRouter, HTTPException, Query
import arxiv
import logging
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the router with tags and prefix
router = APIRouter(
    prefix="/arxiv",
    tags=["arxiv"],
    responses={404: {"description": "Not found"}}
)

class Author(BaseModel):
    name: str

class Article(BaseModel):
    title: str
    authors: List[Author]
    submitted: str
    updated: str
    arxiv_id: str
    abstract_url: str
    pdf_url: str
    primary_category: str
    summary: Optional[str] = None

@router.get("/recent", 
    response_model=List[Article],
    summary="Get Recent ArXiv Articles",
    description="Retrieve the most recent articles from ArXiv for a given category")
async def get_recent_articles(
    category: str = Query("cs.AI", description="ArXiv category (e.g., cs.AI, cs.CL)"),
    limit: int = Query(10, description="Number of articles to return", le=50)
):
    try:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=limit,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        articles = []
        # Remove async_results and directly use search.results()
        for result in search.results():
            article = Article(
                title=result.title,
                authors=[Author(name=author.name) for author in result.authors],
                submitted=result.published.strftime('%Y-%m-%d %H:%M:%S UTC'),
                updated=result.updated.strftime('%Y-%m-%d %H:%M:%S UTC'),
                arxiv_id=result.get_short_id(),
                abstract_url=result.entry_id,
                pdf_url=result.pdf_url,
                primary_category=result.primary_category,
                summary=result.summary[:500] if result.summary else None
            )
            articles.append(article)

        if not articles:
            raise HTTPException(
                status_code=404,
                detail=f"No articles found for category: {category}"
            )

        return articles

    except Exception as e:
        logger.error(f"Error fetching arXiv articles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch articles from arXiv. Please try again later."
        )

@router.get("/categories",
    summary="Get Available Categories",
    description="Return a list of common ArXiv categories")
async def get_available_categories():
    return {
        "categories": [
            {"id": "cs.AI", "name": "Artificial Intelligence"},
            {"id": "cs.CL", "name": "Computation and Language"},
            {"id": "cs.LG", "name": "Machine Learning"},
            {"id": "cs.CV", "name": "Computer Vision"},
            {"id": "cs.NE", "name": "Neural and Evolutionary Computing"},
            {"id": "cs.RO", "name": "Robotics"},
            {"id": "cs.SE", "name": "Software Engineering"}
        ]
    }
