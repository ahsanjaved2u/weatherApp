import streamlit as st
import os
import time
from langchain.chains import GraphCypherQAChain
from langchain_groq import ChatGroq
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
import os


# Neo4j Credentials
try:
    # GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    # NEO4J_URI = st.secrets["NEO4J_URI"]
    # NEO4J_USERNAME = st.secrets["NEO4J_USERNAME"]
    # NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]

    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
except Exception as e:
    st.write(f"An error occurred during getting credentials: {e}")
    raise


# INITIALIZING neo4j INSTANCE
try:
    graph = Neo4jGraph(url =NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
    st.write("NEO4j REMOTE INSTANCE INITIALISED SUCCESSFULLY")
except Exception as e:
    st.write(f"An error occurred during Neo4jGraph initialization: {e}")
    raise


# PROMPT
examples = [
    {
        "question": "Get all weather data for a specific year",
        "query": """MATCH (y:Year {{year:1963}})-[:HAS_MONTH]->(m:Month) 
        RETURN m.name AS Month, m.Tmax AS MaxTemperature, m.Tmin AS MinTemperature,
        m.Rain AS Rainfall, m.Sun AS Sunlight, m.Tmean AS MeanTemperature
        ORDER BY m.month""",
    },
    {
        "question": "what was average temperature in between 1980 and 1990",
        "query": """MATCH (y:Year)-[:HAS_MONTH]->(m:Month)
                    WHERE y.year >= 1980 AND y.year <= 1990
                    RETURN AVG(m.Rain) AS average_rainfall""",
    },
     {
        "question": "what was the most rainy year?",
        "query": """MATCH (y:Year)-[:HAS_MONTH]->(m:Month)
        WITH y.year AS year, AVG(m.Rain) AS avg_rain
        RETURN year, avg_rain
        ORDER BY avg_rain DESC
        LIMIT 1""",
    },
    {
        "question": "In which year we had maximum temperature in may?",
        "query": """MATCH (y:Year)-[:HAS_MONTH]->(m:Month)
        WHERE m.month = 5
        WITH y.year AS year, MAX(m.Tmax) AS max_temp
        RETURN year, max_temp
        ORDER BY max_temp DESC
        LIMIT 1""",
    },

]



example_prompt = PromptTemplate.from_template(
    "User input: {question}\nquery: {query}"
)

prompt = FewShotPromptTemplate(
    examples=examples[:5],
    example_prompt=example_prompt,
    prefix=
    """
    You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.Here is the schema information \nn{schema}.
  
    
    Task:
        You are provided with a natural language query. Your goal is to:
        Understand the user's intent: Identify what the user is asking for, such as retrieving data, finding averages, or comparing values, average between to given dates or months or years
        Generate an appropriate Cypher query: Based on the graph structure and properties provided above, translate the user's natural language query into a Cypher query.
        Return the Cypher query: Ensure the query is correctly formatted and accounts for all relevant properties.

        Use logical operators like >= and <= for filtering node for between specific years, months or dtaes.DO NOT use range() for this
        WHERE clauses should be used for property value comparisons

        
        Given a natural language query, generate a Cypher query that accurately reflects the user's request,
        ensuring that any specific year mentioned in the query is directly translated into the Cypher query. For instance, 
        if the user asks for data from 1991 or in 1991, the Cypher query should explicitly reference the year 1991 in the `MATCH` statement.
        if the user asks for data from january or in january or any other month, the Cypher query should explicitly reference the month anuary or month 1 in the `MATCH` statement.
        ALways give answer obtained from data and never give any suggestion or interpretation  

        Below are a number of examples of questions and their corresponding Cypher queries.",
    """,
    suffix="User input: {question}\nquery: ",
    input_variables=["question", "schema"],
)



# MODEL
llm = ChatGroq(
    api_key=GROQ_API_KEY,  # Replace with actual API key
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=2000
)


# CHAIN
chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, verbose=False, cypher_prompt=prompt)

# Streamlit 
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
