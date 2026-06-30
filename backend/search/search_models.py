from pydantic import BaseModel

class SearchResult(BaseModel):
    """
    Data model representing a single formatted search result.
    """
    title: str
    url: str
    snippet: str
    source_domain: str
