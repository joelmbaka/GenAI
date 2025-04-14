from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class TweetsModel(BaseModel):
    """Model representing scraped tweets from the Twitter Scraper tool."""
    class TweetItem(BaseModel):
        id: str = Field(..., description="The unique identifier of the tweet")
        content: str = Field(..., description="The text content of the tweet")
        user: str = Field(..., description="The handle of the user who posted the tweet")
        timestamp: str = Field(..., description="The timestamp of the tweet in ISO format")
        likes: int = Field(..., description="The number of likes the tweet has received")
        retweets: int = Field(..., description="The number of retweets the tweet has received")
        has_photos: bool = Field(..., description="Whether the tweet contains photos")
        photo_urls: List[str] = Field(default_factory=list, description="List of URLs of the photos in the tweet")

    trend: str = Field(..., description="The trend or hashtag that was searched")
    count: int = Field(..., description="The number of tweets collected")
    tweets: List[TweetItem] = Field(default_factory=list, description="List of tweets collected")

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

class SerperWebSearchResults(BaseModel):
    """Model representing Serper API web search results."""
    
    class SearchParameters(BaseModel):
        q: str = Field(..., description="The search query used")
        type: str = Field(default="search", description="The type of search")
        engine: str = Field(default="google", description="The search engine used")
    
    class KnowledgeGraph(BaseModel):
        class KnowledgeGraphAttributes(BaseModel):
            Customer_service: Optional[str] = Field(default=None, description="Customer service contact information")
            Founders: Optional[str] = Field(default=None, description="Founders of the company")
            Founded: Optional[str] = Field(default=None, description="Date and location of founding")
            CEO: Optional[str] = Field(default=None, description="Current CEO of the company")
            Headquarters: Optional[str] = Field(default=None, description="Headquarters location")
        
        title: Optional[str] = Field(default=None, description="Title of the knowledge graph entry")
        type: Optional[str] = Field(default=None, description="Type of the entity")
        website: Optional[str] = Field(default=None, description="Official website URL")
        imageUrl: Optional[str] = Field(default=None, description="URL of the image")
        description: Optional[str] = Field(default=None, description="Description of the entity")
        descriptionSource: Optional[str] = Field(default=None, description="Source of the description")
        descriptionLink: Optional[str] = Field(default=None, description="Link to the description source")
        attributes: Optional[KnowledgeGraphAttributes] = Field(default=None, description="Additional attributes")
    
    class OrganicResult(BaseModel):
        class OrganicSitelink(BaseModel):
            title: str = Field(..., description="Title of the sitelink")
            link: str = Field(..., description="URL of the sitelink")
        
        title: str = Field(..., description="Title of the search result")
        link: str = Field(..., description="URL of the search result")
        snippet: str = Field(..., description="Brief snippet or summary of the result")
        sitelinks: List[OrganicSitelink] = Field(default_factory=list, description="List of sitelinks")
        position: int = Field(..., description="Position in search results")
        date: Optional[str] = Field(default=None, description="Publication date of the result")
    
    class PeopleAlsoAsk(BaseModel):
        question: str = Field(..., description="Question asked")
        snippet: str = Field(..., description="Brief snippet or summary of the answer")
        title: str = Field(..., description="Title of the source")
        link: str = Field(..., description="URL of the source")
    
    class RelatedSearch(BaseModel):
        query: str = Field(..., description="Related search query")
    
    searchParameters: SearchParameters = Field(..., description="Parameters used for the search query")
    knowledgeGraph: Optional[KnowledgeGraph] = Field(default=None, description="Knowledge graph information")
    organic: List[OrganicResult] = Field(default_factory=list, description="List of organic search results")
    peopleAlsoAsk: List[PeopleAlsoAsk] = Field(default_factory=list, description="List of 'People Also Ask' questions")
    relatedSearches: List[RelatedSearch] = Field(default_factory=list, description="List of related searches")
    credits: int = Field(..., description="Credits used for the search")