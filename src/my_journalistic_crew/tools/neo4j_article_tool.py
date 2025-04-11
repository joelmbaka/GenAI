from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from my_journalistic_crew.models.ArticleModel import FinalArticle
from neo4j import GraphDatabase
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jArticleInput(BaseModel):
    """Input schema for Neo4j Article Tool."""
    title: str = Field(..., description="The headline or main title of the article")
    slug: str = Field(..., description="A URL-friendly version of the article title")
    content: str = Field(..., description="The full text content of the article")
    category: str = Field(..., description="The category of the article")
    subcategory: str = Field(..., description="The subcategory of the article")
    story: str = Field(default="", description="The overarching story this article belongs to")
    breaking_news: bool = Field(default=False, description="Whether the article is a breaking news")
    trending: bool = Field(default=False, description="Whether the article is a trending news")
    author: str = Field(default="", description="The name of the writer based on the category")
    summary: str = Field(default="", description="A brief summary or abstract of the article's main points")
    keywords: List[str] = Field(default_factory=list, description="List of relevant keywords or tags associated with the article")
    entities: List[str] = Field(default_factory=list, description="List of named entities in format 'type:value' extracted from the article")
    imageUrl: Optional[str] = Field(default="", description="URL of the main image associated with the article")
    thumbnailUrl: Optional[str] = Field(default="", description="URL of the thumbnail version of the image")
    imageSource: Optional[str] = Field(default="", description="The source/attribution for the featured image")
    imageTitle: Optional[str] = Field(default="", description="The original title of the featured image")
    publisher: str = Field(default="Joelmbaka", description="The publisher of the article")


class Neo4jArticleTool(BaseTool):
    name: str = "Neo4j Article Storage"
    description: str = (
        "Stores articles in Neo4j graph database with properties for categories, subcategories, and authors, including content embeddings."
    )
    args_schema: Type[BaseModel] = Neo4jArticleInput

    def create_embedding(self, content: str) -> list:
        """
        Use NVIDIA Llama model to create embedding for article content.
        """
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )

        response = client.embeddings.create(
            input=[content],
            model="nvidia/llama-3.2-nv-embedqa-1b-v2",
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "NONE"}
        )

        return response.data[0].embedding

    def _run(self, title: str, slug: str, content: str, category: str, subcategory: str, 
            story: str = "", breaking_news: bool = False, trending: bool = False, 
            author: str = "", summary: str = "", keywords: List[str] = None, 
            entities: List[str] = None, imageUrl: str = "", thumbnailUrl: str = "", 
            imageSource: str = "", imageTitle: str = "", publisher: str = "Joelmbaka") -> str:
        """Store article in Neo4j database with all its properties."""
        # Create a dictionary with all the article properties
        article_dict = {
            "title": title,
            "slug": slug,
            "content": content,
            "category": category,
            "subcategory": subcategory,
            "story": story,
            "breaking_news": breaking_news,
            "trending": trending,
            "author": author,
            "summary": summary,
            "keywords": keywords or [],
            "entities": entities or [],
            "imageUrl": imageUrl,
            "thumbnailUrl": thumbnailUrl,
            "imageSource": imageSource,
            "imageTitle": imageTitle,
            "publisher": publisher,
        }
        
        # Validate the article data
        try:
            FinalArticle(**article_dict)
        except Exception as e:
            return f"Error validating article data: {str(e)}"

        # Generate embedding for the article content using Llama model
        embedding = self.create_embedding(content)

        # Neo4j connection details (should be moved to environment variables)
        uri = os.getenv("NEO4J_URI", "neo4j+s://f3a8bf56.databases.neo4j.io")
        username = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "h316Qd4uC5CsfdLSDj7dsVsMmC9HbwFwgsnWjPtFacA")

        # Cypher query
        query = """
        // Merge the article node with properties (using slug as unique identifier)
        MERGE (art:Article {slug: $slug})
        ON CREATE SET
            art.title = $title,
            art.content = $content,
            art.category = $category,
            art.subcategory = $subcategory,
            art.story = $story,
            art.breaking_news = $breaking_news,
            art.trending = $trending,
            art.author = $author,
            art.summary = $summary,
            art.keywords = $keywords,
            art.imageUrl = $imageUrl,
            art.thumbnailUrl = $thumbnailUrl,
            art.imageSource = $imageSource,
            art.imageTitle = $imageTitle,
            art.entities = $entities,
            art.publisher = $publisher,
            art.embedding = $embedding,
            art.publishedAt = datetime({timezone: '+03:00'})

        RETURN art.title, art.slug, art.publishedAt
        """

        # Connect to Neo4j and execute query
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                result = session.run(query, {
                    "title": title,
                    "slug": slug,
                    "content": content,
                    "category": category,
                    "subcategory": subcategory,
                    "story": story,
                    "breaking_news": breaking_news,
                    "trending": trending,
                    "author": author,
                    "summary": summary,
                    "keywords": keywords or [],
                    "imageUrl": imageUrl,
                    "thumbnailUrl": thumbnailUrl,
                    "imageSource": imageSource,
                    "imageTitle": imageTitle,
                    "entities": entities or [],
                    "publisher": publisher,
                    "embedding": embedding
                })
                
                # Return the created node
                created_node = [record for record in result]
                return f"Successfully stored article with title: '{created_node[0]['art.title']}', slug: '{created_node[0]['art.slug']}', published at: {created_node[0]['art.publishedAt']}"

    def _arun(self, title: str, slug: str, content: str, category: str, subcategory: str, 
            story: str = "", breaking_news: bool = False, trending: bool = False, 
            author: str = "", summary: str = "", keywords: List[str] = None, 
            entities: List[str] = None, imageUrl: str = "", thumbnailUrl: str = "", 
            imageSource: str = "", imageTitle: str = "", publisher: str = "Joelmbaka") -> str:
        """Asynchronous version not implemented"""
        raise NotImplementedError("Neo4jArticleTool does not support async") 