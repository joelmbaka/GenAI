from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from my_journalistic_crew.models.outputs import FinalArticle
from neo4j import GraphDatabase
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jArticleInput(BaseModel):
    """Input schema for Neo4j Article Tool."""
    article: FinalArticle = Field(..., description="Final article to be stored in Neo4j")


class Neo4jArticleTool(BaseTool):
    name: str = "Neo4j Article Storage"
    description: str = (
        "Stores an article in Neo4j Aura database after it has been written. It creates a Cypher Merge Query that checks if slug exists before creating a new slug with necessary properties such as topic, slug, content, content embeddings, author, category, keywords, subcategory, publisher, and timestamps the article. This is the final step of an article generation pipeline. You can lay down your tools! XOXO."
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

    def _run(self, article: FinalArticle) -> str:
        """Store a single article in Neo4j database with all its properties."""
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
            art.thumbnailUrl = $thumbnailUrl,
            art.entities = $entities,
            art.publisher = $publisher,
            art.embedding = $embedding,
            art.publishedAt = datetime({timezone: '+03:00'})

        RETURN art.title, art.slug, art.publishedAt
        """

        # Connect to Neo4j and execute query
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                # Generate embedding for the article content using Llama model
                embedding = self.create_embedding(article.content)

                # Execute the query
                result = session.run(query, {
                    "title": article.title,
                    "slug": article.slug,
                    "content": article.content,
                    "category": article.category,
                    "subcategory": article.subcategory,
                    "story": article.story,
                    "breaking_news": article.breaking_news,
                    "trending": article.trending,
                    "author": article.author,
                    "summary": article.summary,
                    "keywords": article.keywords,
                    "thumbnailUrl": article.thumbnailUrl,
                    "entities": article.entities,
                    "publisher": article.publisher,
                    "embedding": embedding
                })
                
                # Log the created node
                created_node = [record for record in result]
                print(f"Successfully stored article with title: '{created_node[0]['art.title']}', slug: '{created_node[0]['art.slug']}', published at: {created_node[0]['art.publishedAt']}")

        return f"Successfully stored article in Neo4j with slug: '{article.slug}' at {created_node[0]['art.publishedAt']}"

    def _arun(self, title: str, slug: str, content: str, category: str, subcategory: str, 
            story: str = "", breaking_news: bool = False, trending: bool = False, 
            author: str = "", summary: str = "", keywords: List[str] = None, 
            entities: List[str] = None, thumbnailUrl: str = "", 
            imageTitle: str = "", publisher: str = "joelmbaka.site") -> str:
        """Asynchronous version not implemented"""
        raise NotImplementedError("Neo4jArticleTool does not support async") 