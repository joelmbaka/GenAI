from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

class QueryArticleInput(BaseModel):
    """Input schema for Querying Similar Articles Tool."""
    query: str = Field(..., description="The search query to find similar articles for.")

class QueryArticleTool(BaseTool):
    name: str = "Query Article Vector Index"
    description: str = (
        "Queries a vector index to find articles similar to the search query using embeddings."
    )
    args_schema: Type[BaseModel] = QueryArticleInput

    def create_embedding(self, query: str) -> List[float]:
        """
        Use OpenAI model to create embedding for the search query.
        """
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )

        response = client.embeddings.create(
            input=[query],
            model="nvidia/llama-3.2-nv-embedqa-1b-v2",
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "NONE"}
        )

        return response.data[0].embedding

    def query_vector_index(self, embedding: List[float]) -> List[Dict[str, str]]:
        """
        Query the vector index to find the most similar articles.
        """
        # Neo4j connection details
        uri = os.getenv("NEO4J_URI", "neo4j+s://f3a8bf56.databases.neo4j.io")
        username = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "h316Qd4uC5CsfdLSDj7dsVsMmC9HbwFwgsnWjPtFacA")

        # Helper function to calculate cosine similarity
        def cosine_similarity(vec1, vec2):
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm_a = sum(a * a for a in vec1) ** 0.5
            norm_b = sum(b * b for b in vec2) ** 0.5
            return dot_product / (norm_a * norm_b)

        # Cypher query to get all articles with their embeddings
        query = """
        MATCH (a:Article)
        RETURN a.title AS title, a.summary AS summary, a.source AS source, a.embedding AS embedding
        """

        # Connect to Neo4j and execute the query
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                result = session.run(query)
                
                # Calculate similarity for each article
                similar_articles = []
                for record in result:
                    article_embedding = record["embedding"]
                    if article_embedding:  # Ensure embedding exists
                        similarity = cosine_similarity(embedding, article_embedding)
                        if similarity > 0.7:
                            similar_articles.append({
                                "title": record["title"],
                                "summary": record["summary"],
                                "source": record["source"],
                                "score": similarity
                            })
                
                # Sort by similarity and limit results
                similar_articles.sort(key=lambda x: x["score"], reverse=True)
                return similar_articles[:5]

    def _run(self, query_input: QueryArticleInput) -> str:
        try:
            # Generate the embedding for the search query
            embedding = self.create_embedding(query_input.query)

            # Query the vector index to find similar articles
            similar_articles = self.query_vector_index(embedding)

            # Format the results as a string to return
            if similar_articles:
                formatted_results = []
                for i, article in enumerate(similar_articles, 1):
                    formatted_results.append(
                        f"{i}. Title: {article['title']}\n"
                        f"   Summary: {article['summary']}\n"
                        f"   Source: {article['source']}\n"
                        f"   Similarity Score: {article['score']:.2f}\n"
                    )
                return "\n".join(formatted_results)
            else:
                return "No similar articles found."
        except Exception as e:
            return f"Error querying the vector index: {str(e)}"

    def _arun(self, query_input: QueryArticleInput) -> str:
        """Asynchronous version not implemented"""
        raise NotImplementedError("QueryArticleTool does not support async") 