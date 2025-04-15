from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class SerperWebSearchResults(BaseModel):
    """Model representing Serper API web search results for a single query."""
    class SearchParameters(BaseModel):
        q: str = Field(..., description="The search query used")  # Single query string
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

class BatchSerperWebSearchResults(BaseModel):
    """Model representing a batch of Serper API web search results, one for each query."""
    results: List[SerperWebSearchResults] = Field(..., description="List of search results, one for each query")

class TweetsModel(BaseModel):
    """Model representing scraped tweets using twitter search."""
    class TweetItem(BaseModel):
        id: str = Field(..., description="The unique identifier of the tweet")
        content: str = Field(..., description="The text content of the tweet")
        user: str = Field(..., description="The handle of the user who posted the tweet")
        timestamp: str = Field(..., description="The timestamp of the tweet in ISO format")
        likes: int = Field(..., description="The number of likes the tweet has received")
        retweets: int = Field(..., description="The number of retweets the tweet has received")
        replies: int = Field(..., description="The number of replies the tweet has received")
        has_photos: bool = Field(..., description="Whether the tweet contains photos")
        photo_urls: List[str] = Field(default_factory=list, description="List of URLs of the photos in the tweet")

    trend: str = Field(..., description="The trend or hashtag that was searched")
    count: int = Field(..., description="The number of tweets collected")
    tweets: List[TweetItem] = Field(default_factory=list, description="List of tweets collected")

class BatchTweetsModel(BaseModel):
    """Model representing a batch of twitter search results, one for each trend."""
    results: List[TweetsModel] = Field(..., description="List of twitter search results, one for each query")

class SerperGoogleNewsResults(BaseModel):
    """Model representing Serper API News search results for a single query."""
    class SearchParameters(BaseModel):
        q: str = Field(..., description="The search query used")  # Single query string
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

class BatchSerperGoogleNewsResults(BaseModel):
    """Model representing a batch of Google News search results, one for each query."""
    results: List[SerperGoogleNewsResults] = Field(..., description="List of search results, one for each query")

class CombinedBatchSearchResults(BaseModel):
    """Model representing combined search results from web, news, and Twitter."""
    summary: str = Field(..., description="A catchy title and a one-paragraph summary of the findings.")
    results: Dict[str, List[Dict[str, Any]]] = Field(..., description="Combined results containing web_results, news_results, and tweets")

class WebScrapeResults(BaseModel):
    """Model representing scraped website content from multiple URLs."""
    class WebsiteContent(BaseModel):
        url: str = Field(..., description="The URL of the scraped website")
        content: str = Field(..., description="The text content of the website or error message if scraping failed")
    
    websites: List[WebsiteContent] = Field(default_factory=list, description="List of website contents scraped")
    count: int = Field(..., description="The number of websites successfully scraped")
    success_rate: float = Field(..., description="Percentage of URLs that were successfully scraped")
    timing_stats: Dict[str, Any] = Field(default_factory=dict, description="Statistics about scraping performance")

class ImageAnalysisResults(BaseModel):
    """Model representing the results of image analysis."""
    class ImageAnalysisItem(BaseModel):
        image_url: str = Field(..., description="The URL of the analyzed image")
        description: str = Field(..., description="The detailed description of the image content")
        title: str = Field(default="", description="The title of the image")
        imageWidth: int = Field(default=0, description="Width of the full-size image in pixels")
        imageHeight: int = Field(default=0, description="Height of the full-size image in pixels")
        source: str = Field(default="", description="Source website of the image")

    images: List[ImageAnalysisItem] = Field(default_factory=list, description="List of analyzed images and their descriptions")

class CombinedScrapingResults(BaseModel):
    """Model representing combined scraping results from websites and tweets."""
    summary: str = Field(..., description="A catchy title and a one-paragraph summary of the findings from both web scraping and tweets.")
    web_scrape_results: Optional[WebScrapeResults] = Field(default=None, description="Results from web scraping")
    image_analysis_results: Optional[ImageAnalysisResults] = Field(default=None, description="Results from image analysis")

class FinalArticle(BaseModel):
    """Model for representing a final article."""
    title: str = Field(..., description="The headline or main title of the article")
    slug: str = Field(..., description="A URL-friendly version of the article title")
    summary: str = Field(..., description="A brief summary or abstract of the article's main points in Markdown format")
    content: str = Field(..., description="The full text content of the article in Markdown format, including proper image embedding using ![alt text](image_url) syntax, approximately 2500 words")
    author: str = Field(default="", description="The name of the writer based on the category")
    category: str = Field(..., description="The category of the article")
    subcategory: str = Field(..., description="The subcategory of the article")
    story: str = Field(default="", description="The overarching story this article belongs to (e.g., 'RutoMustGo')")
    breaking_news: bool = Field(default=False, description="Whether the article is a breaking news")
    trending: bool = Field(default=False, description="Whether the article is a trending news")
    keywords: List[str] = Field(..., description="List of relevant keywords or tags associated with the article")
    entities: List[str] = Field(default_factory=list, description="List of named entities in format 'type:value' extracted from the article, e.g. 'Country:United States', 'Politician, Kenya President:William Ruto'")
    thumbnailUrl: str = Field(..., description="URL of the thumbnail version of the image (recommended size: 300x168 pixels)")
    publisher: str = Field(default="joelmbaka.site", description="The media house publisher of the article")
    further_reading: List[str] = Field(default_factory=list, description="A list of 1-3 new BlogPost topics that need to be researched and written to complement this articlee", max_items=3)

class GoogleImageResults(BaseModel):
    """Model representing Serper API Google Image search results for a single query."""
    class SearchParameters(BaseModel):
        q: str = Field(..., description="The search query used")  # Single query string
        type: str = Field(default="images", description="The type of search")
        engine: str = Field(default="google", description="The search engine used")
        num: int = Field(default=10, description="Number of image results requested")
    
    class ImageItem(BaseModel):
        title: str = Field(default="", description="The title of the image")
        imageUrl: str = Field(..., description="URL link to the full-size image")
        imageWidth: int = Field(default=0, description="Width of the full-size image in pixels")
        imageHeight: int = Field(default=0, description="Height of the full-size image in pixels")
        source: str = Field(default="", description="Source website of the image")
    
    searchParameters: SearchParameters = Field(..., description="Parameters used for the search query")
    images: List[ImageItem] = Field(default_factory=list, description="List of images found in the search results")

class DownloadedImage(BaseModel):
    """Model representing a single downloaded and processed image."""
    local_path: str = Field(..., description="The local path where the image was saved")
    message: str = Field(..., description="Message describing the result of the download operation")
    success: bool = Field(..., description="Whether the download was successful")
    image_analysis: Optional[ImageAnalysisResults] = Field(default=None, description="Results from image analysis")

class DownloadImageResults(BaseModel):
    """Model representing results from downloading multiple images."""
    images: List[DownloadedImage] = Field(default_factory=list, description="List of downloaded images")
    success_count: int = Field(..., description="Number of images successfully downloaded")
    failure_count: int = Field(..., description="Number of images that failed to download")

class DownloadedThumbnail(BaseModel):
    """Model representing a single downloaded and processed thumbnail image."""
    local_path: str = Field(..., description="The local path where the thumbnail was saved")
    message: str = Field(..., description="Message describing the result of the download operation")
    success: bool = Field(..., description="Whether the download was successful")
    image_analysis: Optional[ImageAnalysisResults] = Field(default=None, description="Results from image analysis")

class BlobStorageUpload(BaseModel):
    """Model representing a single file uploaded to Vercel Blob storage."""
    blob_url: str = Field(..., description="The URL of the file in Vercel Blob storage")
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Message describing the result of the upload operation")
    image_analysis: Optional[ImageAnalysisResults] = Field(default=None, description="Results from image analysis")
    
class BlobStorageResults(BaseModel):
    """Model representing results from uploading files to Vercel Blob storage."""
    uploads: List[BlobStorageUpload] = Field(default_factory=list, description="List of uploaded files")
    success_count: int = Field(..., description="Number of files successfully uploaded")
    failure_count: int = Field(..., description="Number of files that failed to upload")

class ImageProcessingResults(BaseModel):
    """Model representing combined results from image downloading and blob storage operations."""
    downloaded_images: Optional[DownloadImageResults] = Field(default=None, description="Results from downloading regular images")
    downloaded_thumbnail: Optional[DownloadedThumbnail] = Field(default=None, description="Result from downloading a thumbnail image")
    blob_storage_results: Optional[BlobStorageResults] = Field(default=None, description="Results from uploading images to blob storage")
    summary: str = Field(..., description="A brief summary of the image processing operations")

class DraftArticle(BaseModel):
    """Model for representing a draft article with structured sections and sources."""
    title: str = Field(..., description="The headline or main title of the draft article")
    summary: str = Field(..., description="A brief summary or abstract of the article's main points")
    
    class Section(BaseModel):
        """Model for representing a section of the draft article with content and supporting URLs."""
        heading: str = Field(..., description="The heading or title of this section")
        content: str = Field(..., description="The text content of this section in Markdown format")
        urls: List[str] = Field(default_factory=list, description="List of URLs supporting this section's content, inclusing tweets in the form https://x.com/user/status/tweetID")
    
    sections: List[Section] = Field(default_factory=list, description="The sections that make up the body of the article")
    conclusion: str = Field(..., description="The concluding paragraph(s) of the article in Markdown format")
    further_reading: List[str] = Field(default_factory=list, description="A list of 1-3 new topic ideas for further reading", max_items=3)
    image_urls: List[str] = Field(default_factory=list, description="List of image URLs from tweets")
