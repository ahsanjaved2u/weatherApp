        # f = io.StringIO() # create a place to capture output
        # with redirect_stdout(f):  # ouput(response) is redirected and sotored in f 
        #     response = chain.invoke({"query": question})
        # verbose_output = f.getvalue()
        # if verbose_output:
        #     clean_output = re.sub(r'\x1b\[[0-9;]*m', '', verbose_output)
        #     print(clean_output)
        # else:
        #      st.write("Could not extract Cypher query.")


# http://139.135.34.112:7474/browser/

# NEO4J_URI = "bolt://139.135.34.112:7687"


#  # Debug: Print the environment variables to ensure they're correctly loaded
#     st.write("Neo4j URL:", NEO4J_URI)
#     st.write("Neo4j User:", NEO4J_USERNAME)
#     st.write("Neo4j Password:", NEO4J_PASSWORD)
#     st.write("GROQ API Key:", GROQ_API_KEY)