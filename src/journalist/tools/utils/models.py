from pydantic import BaseModel, Field
from typing import List, Optional


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

class TweetSchema(BaseModel):
    id: str
    content: str
    user: str
    timestamp: str
    likes: int
    retweets: int
    #url: str
    has_photos: bool = False
    #has_videos: bool = False
    #photo_urls: List[str] = Field(default_factory=list)
    #video_urls: List[str] = Field(default_factory=list)

class TweetsOutput(BaseModel):
    tweets: List[TweetSchema]


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