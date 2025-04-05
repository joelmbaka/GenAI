from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from journalist.tools.utils.models import ArticleModel
from neo4j import GraphDatabase
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jArticleInput(BaseModel):
    """Input schema for Neo4j Article Tool."""
    article: dict = Field(..., description="The article data to store in Neo4j")

class Neo4jArticleTool(BaseTool):
    name: str = "Neo4j Article Storage"
    description: str = (
        "Stores articles in Neo4j graph database with proper relationships to categories and authors, including content embeddings."
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

    def _run(self, article: dict) -> str:
        # Validate and convert dictionary to ArticleModel
        try:
            article_model = ArticleModel(**article)
        except Exception as e:
            return f"Error converting dictionary to ArticleModel: {str(e)}"

        # Ensure publisher is always 254 News
        article_dict = article_model.model_dump()
        article_dict['publisher'] = "254 News"

        # Generate embedding for the article content using Llama model
        embedding = self.create_embedding(article_dict['content'])

        # Neo4j connection details (should be moved to environment variables)
        uri = os.getenv("NEO4J_URI", "neo4j+s://f3a8bf56.databases.neo4j.io")
        username = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "h316Qd4uC5CsfdLSDj7dsVsMmC9HbwFwgsnWjPtFacA")

        # Cypher query
        query = """
        // Create or find the category and subcategory nodes
        MERGE (c:Category {name: $category})
        MERGE (s:SubCategory {name: $subcategory})

        // Create relationship between category and subcategory
        MERGE (c)-[:HAS_SUBCATEGORY]->(s)

        // Create or find the author node
        MERGE (a:Author {name: $author})

        // Create or find the article node
        CREATE (art:Article {title: $title, content: $content, publisher: $publisher})

        // Set the publication timestamp (published_at) at the time of creation
        SET art.publishedAt = datetime({timezone: '+03:00'})

        // Set any additional properties
        SET art.imageUrl = $imageUrl,
            art.thumbnailUrl = $thumbnailUrl,
            art.imageSource = $imageSource,
            art.imageTitle = $imageTitle,
            art.summary = $summary,
            art.keywords = $keywords,
            art.entities = $entities,
            art.metadata = $metadata,
            art.story = $story,
            art.embedding = $embedding

        // Create relationships
        MERGE (art)-[:BELONGS_TO]->(c)
        MERGE (art)-[:STORY_BY]->(a)

        RETURN art, c, a
        """

        # Connect to Neo4j and execute query
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                result = session.run(query, {
                    "category": article_dict['category'],
                    "subcategory": article_dict['subcategory'],
                    "author": article_dict['author'],
                    "title": article_dict['title'],
                    "content": article_dict['content'],
                    "publisher": article_dict['publisher'],
                    "imageUrl": article_dict.get('imageUrl', ''),
                    "thumbnailUrl": article_dict.get('thumbnailUrl', ''),
                    "imageSource": article_dict.get('imageSource', ''),
                    "imageTitle": article_dict.get('imageTitle', ''),
                    "summary": article_dict['summary'],
                    "keywords": article_dict['keywords'],
                    "entities": article_dict['entities'],
                    "metadata": article_dict['metadata'],
                    "story": article_dict['story'],
                    "embedding": embedding
                })
                
                # Return the created nodes
                created_nodes = [record for record in result]
                return f"Successfully stored article with {len(created_nodes)} related nodes"

    def _arun(self, article: dict) -> str:
        """Asynchronous version not implemented"""
        raise NotImplementedError("Neo4jArticleTool does not support async") 