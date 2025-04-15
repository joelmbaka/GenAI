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