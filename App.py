import streamlit as st
import os
import time
from langchain.chains import GraphCypherQAChain
from langchain_groq import ChatGroq
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from neo4j import GraphDatabase

# Accessing environment variables
# neo4j_url = os.getenv('NEO4J_URI')
# neo4j_user = os.getenv('NEO4J_USER')
# neo4j_password = os.getenv('NEO4J_PASSWORD')
# groq_api_key = os.getenv('GROQ_API_KEY')



try:
    # Initialize the Neo4jGraph object with direct parameters
    # neo4j_url = st.secrets["NEO4J_URI"]
    # neo4j_user = st.secrets["NEO4J_USER"]
    # neo4j_password = st.secrets["NEO4J_PASSWORD"]
    # groq_api_key = st.secrets["GROQ_API_KEY"]

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USERNAME = st.secrets["NEO4J_USERNAME"]
    NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]

    print("Neo4jGraph initialized successfully.")
except Exception as e:
    st.write(f"An error occurred during getting credentials: {e}")
    raise

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Test connection
try:
    with driver.session() as session:
        result = session.run("RETURN 1")
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")



# Debug: Print the environment variables to ensure they're correctly loaded
st.write("Neo4j URL:", NEO4J_URI)
st.write("Neo4j User:", NEO4J_USERNAME)
st.write("Neo4j Password:", NEO4J_PASSWORD)
st.write("GROQ API Key:", GROQ_API_KEY)


try:
    # Initialize the Neo4jGraph object with direct parameters
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
    print("Neo4jGraph initialized successfully.")
except Exception as e:
    st.write(f"An error occurred during Neo4jGraph initialization: {e}")
    raise

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
    api_key=GROQ_API_KEY,  # Replace with actual API key
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=2000
)

chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, verbose=False, cypher_prompt=prompt)

# Streamlit input and processing
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
