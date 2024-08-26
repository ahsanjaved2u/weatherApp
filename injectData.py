from langchain_community.graphs import Neo4jGraph
import os
# https://github.com/alanjones2/uk-historical-weather/blob/main/data/Leuchars.csv

def populateDb():

    weather_query = """
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/alanjones2/uk-historical-weather/main/data/Leuchars.csv' AS row
    WITH row,
    toInteger(coalesce(trim(row.Year), '0')) AS year,
    toInteger(coalesce(trim(row.Month), '0')) AS month,
    toFloat(coalesce(trim(row.Tmax), '0')) AS tmax,
    toFloat(coalesce(trim(row.Tmin), '0')) AS tmin,
    toFloat(coalesce(trim(row.AF), '0')) AS af,
    toFloat(coalesce(trim(row.Rain), '0')) AS rain,
    toFloat(coalesce(trim(row.Sun), '0')) AS sun,
    toInteger(coalesce(trim(row.status), '0')) AS status,
    date(coalesce(row.Date, '01/01/1970')) AS date,
    toFloat(coalesce(trim(row.Tmean), '0')) AS tmean

MERGE (y:Year {year:year})
MERGE (m:Month {month: month, name: CASE month
    WHEN 1 THEN 'January' 
    WHEN 2 THEN 'February' 
    WHEN 3 THEN 'March' 
    WHEN 4 THEN 'April' 
    WHEN 5 THEN 'May' 
    WHEN 6 THEN 'June' 
    WHEN 7 THEN 'July' 
    WHEN 8 THEN 'August' 
    WHEN 9 THEN 'September' 
    WHEN 10 THEN 'October' 
    WHEN 11 THEN 'November' 
    WHEN 12 THEN 'December' 
    END,

    Tmax: tmax,
    Tmin: tmin,
    AF: af,
    Rain: rain,
    Sun: sun,
    Tmean: tmean,
    Date: date

    })

MERGE (y)-[:HAS_MONTH]->(m)

"""



    try:

        NEO4J_URI = os.getenv('NEO4J_URI')
        NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
        NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

        print('credentials', NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
        graph = Neo4jGraph(url =NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
        graph.query(weather_query)
        print("Data injected successfully.")
    except Exception as e:
        print(f"An error occurred during uploading data: {e}")
        raise


populateDb()