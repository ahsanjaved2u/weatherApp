import streamlit as st
from langchain.chains import GraphCypherQAChain
from langchain_groq import ChatGroq
from langchain.chains import GraphCypherQAChain
from langchain_groq import ChatGroq
from langchain_community.graphs import Neo4jGraph
import io
import re
from contextlib import redirect_stdout
import time  # Import the time module
import os
from langchain_core.prompts import ChatPromptTemplate



neo4j_url = os.getenv('NEO4J_URI')
neo4j_user = os.getenv('NEO4J_USERNAME')
neo4j_password = os.getenv('NEO4J_PASSWORD')
GROQ_API = os.getenv('GROQ_API_KEY')

print(neo4j_url,neo4j_user ,neo4j_password,GROQ_API)

graph = Neo4jGraph(url=neo4j_url, username=neo4j_user, password=neo4j_password)

# graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="Pakistan@123456")


system_message = """

You are interacting with a Neo4j graph database containing weather data structured as follows:

Graph Structure:
        Year Node (Year)
        Properties:
        year (Integer): 

        Month Node (Month)
        Properties:
        month (Integer): The numeric representation of the month (1 = January, 2 = February, ..., 12 = December).
        name (String): The name of the month (e.g., "January", "February").
        Tmax (Float): Maximum temperature recorded in the month.
        Tmin (Float): Minimum temperature recorded in the month.
        AF (Float): Number of air frosts in the month.
        Rain (Float): Rainfall recorded in millimeters.
        Sun (Float): Sunlight recorded in hours.
        Tmean (Float): Mean temperature in the month.
        Date (Date): Date representation (e.g., "1963-01-01").

        Relationships:
        HAS_MONTH: Connects Year nodes to their respective Month nodes.

    Task:
            You are provided with a natural language query. Your goal is to:
                Understand the user's intent: Identify what the user is asking for, such as retrieving data, finding averages, or comparing values.
                Generate an appropriate Cypher query: Based on the graph structure and properties provided above, translate the user's natural language query into a Cypher query.
                Return the Cypher query: Ensure the query is correctly formatted and accounts for all relevant properties.

    Examples of Natural Language Queries:
            "What was the average temperature in a given year on month?"
            "Show me the month with the most rainfall in given year."
            "Get all the weather data for January across all years."
            "Which year had the highest average temperature in July?"

    Given a natural language query, generate a Cypher query that accurately reflects the user's request,
    ensuring that any specific year mentioned in the query is directly translated into the Cypher query. For instance, 
    if the user asks for data from 1991 or in 1991, the Cypher query should explicitly reference the year 1991 in the `MATCH` statement.
    if the user asks for data from january or in january or any other month, the Cypher query should explicitly reference the month anuary or month 1 in the `MATCH` statement.
    ALwas gice answer obtained from data and never give any suggestion or interpretation

    User question: {query}


"""

prompt = ChatPromptTemplate.from_template(system_message)
llm = ChatGroq(
    api_key=GROQ_API,
    model = "llama-3.1-70b-versatile",
    temperature = 0,
    max_tokens = 2000
)

chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, verbose=False,  cypher_prompt = prompt)


question = st.text_input("Question") 
if st.button("Submit"):
    if question:
        try:
            start_time = time.time()

            response = chain.invoke({"query": question})
            st.write(response['result'])
            
            end_time = time.time() 
            elapsed_time = end_time - start_time
            st.write(f"{elapsed_time:.2f}")

        except Exception as e:
            st.write(f"An error occurred: {e}")
