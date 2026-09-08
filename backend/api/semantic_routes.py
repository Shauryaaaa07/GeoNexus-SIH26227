from fastapi import APIRouter, Query

from services.semantic_service import (
    semantic_search,
    search_real_satellite_data
)


router = APIRouter(
    prefix="/api/search",
    tags=["Semantic Search"]
)


@router.get("/semantic")
def search_satellite_data(
    query: str = Query(
        ...,
        description="Natural language satellite search query"
    ),
    top_k: int = Query(
        5,
        description="Number of results"
    )
):

    results = semantic_search(
        query=query,
        top_k=top_k
    )

    return {
        "status": "success",
        "query": query,
        "count": len(results),
        "results": results
    }


@router.get("/real")
def search_real_satellite(
    query: str = Query(
        ...,
        description="Natural language query, e.g. Delhi satellite image 2025"
    )
):

    return search_real_satellite_data(query)