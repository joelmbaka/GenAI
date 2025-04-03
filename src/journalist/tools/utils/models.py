from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class UserModel(BaseModel):
    """Model for tweet user information"""
    name: str
    handle: Optional[str] = None


class TimestampModel(BaseModel):
    """Model for tweet timestamp information"""
    datetime: Optional[str] = None
    display: Optional[str] = None


class MetricsModel(BaseModel):
    """Model for tweet engagement metrics"""
    replies: Optional[int] = None
    retweets: Optional[int] = None
    likes: Optional[int] = None


class MediaModel(BaseModel):
    """Model for tweet media information"""
    hasPhotos: bool = False
    hasVideos: bool = False
    mediaCount: int = 0
    photoUrls: List[str] = Field(default_factory=list)
    videoUrls: List[str] = Field(default_factory=list)


class TweetAttributeModel(BaseModel):
    """Model for HTML attribute in tweet structure"""
    name: str
    value: str


class TweetStructureModel(BaseModel):
    """Model for tweet HTML structure"""
    ariaLabel: Optional[str] = None
    attributes: List[TweetAttributeModel] = Field(default_factory=list)
    classList: List[str] = Field(default_factory=list)
    dataTestId: Optional[str] = None
    id: str = ""
    role: Optional[str] = None
    tagName: str
    text: Optional[str] = None
    visible: bool = True


class TweetModel(BaseModel):
    """Model for a complete tweet"""
    content: Optional[str] = None
    media: MediaModel = Field(default_factory=MediaModel)
    metrics: MetricsModel = Field(default_factory=MetricsModel)
    structure: TweetStructureModel
    timestamp: TimestampModel = Field(default_factory=TimestampModel)
    user: UserModel


class TweetCollectionModel(BaseModel):
    """Model for a collection of tweets"""
    status: str
    trend: str
    tweet_count: int
    filename: str = "tweets.json"
    tweets: List[TweetModel] = Field(default_factory=list) 


class ScraperInput(BaseModel):
    """Input schema for Scraper."""
    trend: str = Field(..., description="The trend to navigate to and scrape tweets from")
    is_hashtag: bool = Field(
        default=False, 
        description="Whether the trend is a hashtag"
    )
    headless: bool = Field(
        default=True, 
        description="Whether to run browser in headless mode"
    )
    device_type: str = Field(
        default="tablet", 
        description="Device type to emulate (tablet or desktop)"
    )
    scroll_count: int = Field(
        default=20,
        description="Number of times to scroll down the page"
    )
    scroll_delay: float = Field(
        default=5.0,
        description="Delay in seconds between scrolls"
    )
    max_tweets: int = Field(
        default=50,
        description="Maximum number of tweets to collect"
    )

class ScraperOutput(BaseModel):
    """Output schema for Scraper."""
    status: str = Field(..., description="Status of the scraping operation (success or error)")
    message: str = Field(..., description="Descriptive message about the operation result")
    tweet_count: int = Field(default=0, description="Number of tweets collected")
    filename: str = Field(default="", description="Name of the file where tweets were saved (if any)")
    error: str = Field(default="", description="Error details if status is 'error'") 
    


# Define main categories
class MainCategory(str, Enum):
    News = "News"
    Business = "Business"
    Lifestyle = "Lifestyle"
    Sports = "Sports"
    Environment = "Environment"
    SpecialFeatures = "Special Features"

class SubCategory(str, Enum):
    LocalNews = "Local News"
    WorldNews = "World News"
    Enterprise = "Enterprise"
    Finance = "Finance"
    Technology = "Technology"
    Agriculture = "Agriculture"
    Health = "Health"
    Food = "Food"
    Travel = "Travel"
    Education = "Education"
    Opinion = "Opinion"


class ArticleModel(BaseModel):
    """Model for representing news articles"""
    title: str = Field(..., description="The headline or main title of the article")
    content: str = Field(..., description="The full text content of the article")
    category: MainCategory = Field(..., description="Main category of the article")
    subcategory: SubCategory = Field(..., description="Specific subcategory of the article")
    story: Optional[str] = Field(
        None,
        description="The overarching story this article belongs to (e.g., 'US Strikes Yemen')"
    )
    breaking_news: bool = Field(
        default=False,
        description="Whether the article is a breaking news"
    )
    trending: bool = Field(
        default=False,
        description="Whether the article is a trending news"
    )
    author: Optional[str] = Field(None, description="The name of the writer based on the category")
    summary: Optional[str] = Field(None, description="A brief summary or abstract of the article's main points")
    keywords: List[str] = Field(default_factory=list, description="List of relevant keywords or tags associated with the article")
    featured_image: Optional[str] = Field(None, description="URL of the main image associated with the article")
    entities: List[str] = Field(
        default_factory=list,
        description="List of named entities in format 'type:value' extracted from the article, e.g. 'Country:United States', 'Person:William Ruto'"
    )
    metadata: str = Field(
        default="",
        description="Additional metadata about the article as a JSON string, such as word count, reading time, or publication section"
    )
    publisher: Literal["Kenya24"] = Field(
        default="Kenya24",
        description="The publisher of the article"
    )

    def to_markdown(self) -> str:
        """Convert article to markdown format"""
        markdown = f"# {self.title}\n\n"
        if self.story:
            markdown += f"**Story:** {self.story}\n\n"
        if self.featured_image:
            markdown += f"![Featured Image]({self.featured_image})\n\n"
        if self.author:
            markdown += f"**By {self.author}**\n\n"
        if self.summary:
            markdown += f"**Summary:** {self.summary}\n\n"
        if self.keywords:
            markdown += f"**Keywords:** {', '.join(self.keywords)}\n\n"
        markdown += f"{self.content}\n\n"
        if self.publisher:
            markdown += f"**Publisher:** {self.publisher}\n\n"
        if self.entities:
            markdown += f"**Entities:** {', '.join(self.entities)}\n\n"
        if self.metadata:
            markdown += f"**Metadata:** {self.metadata}\n\n"
        if self.category:
            markdown += f"**Category:** {self.category}\n\n"
        if self.subcategory:
            markdown += f"**Subcategory:** {self.subcategory}\n\n"
        return markdown
