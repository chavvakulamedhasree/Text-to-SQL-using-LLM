import streamlit as st
import sqlite3
import google.generativeai as genai

def get_gemini_response(question, prompt, schema):
   
    model = genai.GenerativeModel('gemini-1.5-flash') 
    try:
        prompt_with_schema = prompt + [f"Schema: {schema}"]
        response = model.generate_text(prompt=[question] + prompt_with_schema) 
        return response.text 
    except Exception as e: 
        print(f"Error generating response: {e}")
        return "Error generating response."

def read_sql_query(sql, db_path):
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            return [dict(zip(column_names, row)) for row in rows]
    except Exception as e:
        return {"error": str(e)}

def get_table_schema(db_path, table_name):
   
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_desc = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
            return f"Table: {table_name}\n    Columns: {column_desc}"
    except Exception as e:
        return f"Error retrieving schema for {table_name}: {e}"
prompt=[
    """
    You are an expert SQL assistant. 
    Given the following database schema: 

    Convert the following natural language query into a valid SQL query: 
    """
]
# Streamlit App
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question = st.text_input("Input: ", key="input")
db_files = st.file_uploader("Select Database Files", type="db", accept_multiple_files=True) 
table_name = st.text_input("Table Name:") 

submit = st.button("Ask the question")

if submit and db_files and table_name:
    for db_file in db_files:
        st.subheader(f"Processing Database: {db_file.name}")
        try:
            schema = get_table_schema(db_file.name, table_name)
            response = get_gemini_response(question, prompt, schema)
            st.subheader("Generated SQL Query:")
            st.code(response)

            if response:
                try:
                    results = read_sql_query(response, db_file.name) 
                    st.subheader("Query Results:")
                    st.table(results) 
                except Exception as e:
                    st.error(f"Error executing query on {db_file.name}: {e}") 
            else:
                st.warning("No SQL query generated.")
        except Exception as e:
            st.error(f"Error processing schema for {db_file.name}: {e}")
else:
    st.warning("Please select one or more database files and specify the table name.")