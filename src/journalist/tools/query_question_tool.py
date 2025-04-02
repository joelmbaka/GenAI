from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

class QueryQuestionInput(BaseModel):
    """Input schema for Querying Question and Answer Tool."""
    question: str = Field(..., description="The user-submitted question to find similar answers for.")

class QueryQuestionAnswerTool(BaseTool):
    name: str = "Query Question Answer Vector Index"
    description: str = (
        "Queries a vector index to find answers to a new user-submitted question using embeddings."
    )
    args_schema: Type[BaseModel] = QueryQuestionInput

    def create_embedding(self, question: str) -> List[float]:
        """
        Use OpenAI model to create embedding for the user's question.
        """
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )

        response = client.embeddings.create(
            input=[question],
            model="nvidia/llama-3.2-nv-embedqa-1b-v2",
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "NONE"}
        )

        return response.data[0].embedding

    def query_vector_index(self, embedding: List[float]) -> List[Dict[str, str]]:
        """
        Query the vector index to find the most similar questions and their answers.
        """
        # Neo4j connection details
        uri = os.getenv("NEO4J_URI", "neo4j+s://f3a8bf56.databases.neo4j.io")
        username = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "h316Qd4uC5CsfdLSDj7dsVsMmC9HbwFwgsnWjPtFacA")

        # Cypher query to find similar questions and their answers
        query = """
        MATCH (q:Question)-[:ANSWERED_BY]->(a:Answer)
        WITH q, a, gds.similarity.cosine(q.embedding, $embedding) AS similarity
        WHERE similarity > 0.7
        RETURN q.text AS question_text, a.text AS answer_text, similarity
        ORDER BY similarity DESC
        LIMIT 5
        """

        # Connect to Neo4j and execute the query
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                result = session.run(query, {"embedding": embedding})

                # Return the results of similar questions and their corresponding answers
                similar_results = [{
                    "question": record["question_text"],
                    "answer": record["answer_text"],
                    "score": record["similarity"]
                } for record in result]

                return similar_results

    def _run(self, query_input: QueryQuestionInput) -> str:
        try:
            # Generate the embedding for the user-submitted question
            embedding = self.create_embedding(query_input.question)

            # Query the vector index to find similar questions and answers
            similar_results = self.query_vector_index(embedding)

            # Format the results as a string to return
            if similar_results:
                formatted_results = []
                for i, result in enumerate(similar_results, 1):
                    formatted_results.append(
                        f"{i}. Question: {result['question']}\n"
                        f"   Answer: {result['answer']}\n"
                        f"   Similarity Score: {result['score']:.2f}\n"
                    )
                return "\n".join(formatted_results)
            else:
                return "No similar questions and answers found."
        except Exception as e:
            return f"Error querying the vector index: {str(e)}"

    def _arun(self, query_input: QueryQuestionInput) -> str:
        """Asynchronous version not implemented"""
        raise NotImplementedError("QueryQuestionAnswerTool does not support async") 