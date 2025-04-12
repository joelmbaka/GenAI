from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class GoogleNewsResults(BaseModel):
    """Model representing Google News search results from the search tool"""
    class SearchParameters(BaseModel):
        q: str = Field(..., description="The search query used")
        type: str = Field(default="news", description="The type of search")
        engine: str = Field(default="google", description="The search engine used")
    
    class NewsItem(BaseModel):
        title: str = Field(..., description="The title of the news article")
        link: str = Field(..., description="URL link to the news article")
        snippet: str = Field(default="", description="Brief text snippet or summary of the article")
        date: str = Field(default="", description="Publication date of the article")
        source: str = Field(default="", description="Source publication of the article")
        position: int = Field(..., description="Position in search results")
    
    searchParameters: SearchParameters = Field(..., description="Parameters used for the search query")
    news: List[NewsItem] = Field(default_factory=list, description="List of news articles found in the search results")

class GoogleImageResults(BaseModel):
    """Model representing Google Image search results from the search tool"""
    class SearchParameters(BaseModel):
        q: str = Field(..., description="The search query used")
        type: str = Field(default="images", description="The type of search")
        engine: str = Field(default="google", description="The search engine used")
        num: int = Field(default=10, description="Number of image results requested")
    
    class ImageItem(BaseModel):
        title: str = Field(default="", description="The title of the image")
        imageUrl: str = Field(..., description="URL link to the full-size image")
        imageWidth: int = Field(default=0, description="Width of the full-size image in pixels")
        imageHeight: int = Field(default=0, description="Height of the full-size image in pixels")
        thumbnailUrl: str = Field(default="", description="URL link to the thumbnail version of the image")
        thumbnailWidth: int = Field(default=0, description="Width of the thumbnail image in pixels")
        thumbnailHeight: int = Field(default=0, description="Height of the thumbnail image in pixels")
        source: str = Field(default="", description="Source website of the image")
    
    searchParameters: SearchParameters = Field(..., description="Parameters used for the search query")
    images: List[ImageItem] = Field(default_factory=list, description="List of images found in the search results")

class DraftArticle(BaseModel):
    """format for a draft article"""
    title: str = Field(..., description="The headline or main title of the article")
    slug: str = Field(..., description="A URL-friendly version of the article title")
    summary: str = Field(default="", description="A brief summary or abstract of the article's main points in Markdown format")    
    content: str = Field(..., description="The full text content of the article in Markdown format, including proper image embedding using ![alt text](image_url) syntax, approximately 300 words")
    keywords: List[str] = Field(default_factory=list, description="List of relevant keywords or tags associated with the article")
    entities: List[str] = Field(
        default_factory=list,
        description="List of named entities in format 'type:value' extracted from the article, e.g. 'Country:United States', 'Person:William Ruto'"
    )

class FinalArticle(BaseModel):
    """Model for representing news articles"""
    title: str = Field(..., description="The headline or main title of the article")
    slug: str = Field(..., description="A URL-friendly version of the article title")
    content: str = Field(..., description="The full text content of the article in Markdown format, including proper image embedding using ![alt text](image_url) syntax, approximately 300 words")
    category: str = Field(..., description="The category of the article")
    subcategory: str = Field(..., description="The subcategory of the article")
    story: str = Field(
        default="",
        description="The overarching story this article belongs to (e.g., 'RutoMustGo')"
    )
    breaking_news: bool = Field(
        default=False,
        description="Whether the article is a breaking news"
    )
    trending: bool = Field(
        default=False,
        description="Whether the article is a trending news"
    )
    author: str = Field(default="", description="The name of the writer based on the category")
    summary: str = Field(default="", description="A brief summary or abstract of the article's main points in Markdown format")
    keywords: List[str] = Field(default_factory=list, description="List of relevant keywords or tags associated with the article")
    entities: List[str] = Field(
        default_factory=list,
        description="List of named entities in format 'type:value' extracted from the article, e.g. 'Country:United States', 'Person:William Ruto'"
    )
    imageUrl: str = Field(default="", description="URL of the main image associated with the article")
    thumbnailUrl: str = Field(default="", description="URL of the thumbnail version of the image (recommended size: 300x168 pixels)")
    imageSource: str = Field(default="", description="The source/attribution for the featured image")
    imageTitle: str = Field(default="", description="The original title of the featured image")
    publisher: str = Field(
        default="joelmbaka.site",
        description="The publisher of the article"
    )
    breaking_news: bool = Field(
        default=False,
        description="Whether the article is a breaking news"
    )
    trending: bool = Field(
        default=False,
        description="Whether the article is a trending news"
    )

CategorySubcategoryAuthor = {
    "news": {
        "subcategories": {
            "kenya": {"author": "John Kamau"},
            "africa": {"author": "Kwame Nkrumah"},
            "u.s": {"author": "John Smith"},
            "europe": {"author": "James Wilson"},
            "asia": { "authors": ["Li Wei", "Priya Patel"]},
            "middle east": {"author": "David Cohen"}
        }
    },
    "business": {
        "subcategories": {
            "business news": {"author": "Dr. Emily Chebet"},
            "startup ideas": {"author": "Anne Mwangi"},
            "success stories": {"author": "Peter Kipchumba"},
            "technology in business": {"author": "Anne Mwangi"}
        }
    },
    "lifestyle": {
        "subcategories": {
            "technology": {"author": "Anne Mwangi"},
            "agriculture": {"author": "Peter Kipchumba"},
            "health": {"author": "Dr. Emily Chebet"},
            "food": {"author": "Marco Rossi"},
            "travel": {"author": "Peter Kipchumba"},
            "education": {"author": "Dr. Emily Chebet"},
            "opinion": {"author": "Anne Mwangi"},
            "sports": {"author": "James Wilson"},
        }
    },
}
