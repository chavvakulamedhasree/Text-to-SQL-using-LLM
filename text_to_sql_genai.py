import sqlite3
import streamlit as st
import google.generativeai as genai

# --- Configure Gemini API ---
genai.configure(api_key="YOUR_API_KEY")  # 🔁 Replace with your Gemini API key

# --- Gemini Query Generator ---
def get_sql_from_question(question, schema):
    prompt = f"""
    You are an expert in SQL.
    Given the schema:
    {schema}

    Generate a SQL query for this question:
    {question}

    Only return the SQL query without explanation or formatting.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating query: {e}"

# --- Extract Schema ---
def get_schema(db_path, table):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            return f"Table {table} has columns: " + ", ".join([f"{col[1]} ({col[2]})" for col in columns])
    except Exception as e:
        return f"Error retrieving schema: {e}"

# --- Execute SQL ---
def run_query(sql, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return rows, columns
    except Exception as e:
        return None, [f"Error executing query: {e}"]

# --- Streamlit UI ---
st.set_page_config("SQL Generator with Gemini")
st.title("Gemini App to Generate SQL Queries")

question = st.text_input("Enter your question:")
uploaded_db = st.file_uploader("Upload your SQLite .db file", type="db")
table_name = st.text_input("Enter table name to extract schema:")

if st.button("Generate & Run SQL"):
    if uploaded_db and question and table_name:
        # Save uploaded DB file locally
        with open(uploaded_db.name, "wb") as f:
            f.write(uploaded_db.getbuffer())
        
        schema = get_schema(uploaded_db.name, table_name)
        st.text(f"Schema:\n{schema}")

        sql_query = get_sql_from_question(question, schema)
        st.subheader("Generated SQL Query")
        st.code(sql_query)

        if "Error" not in sql_query:
            rows, columns = run_query(sql_query, uploaded_db.name)
            if rows:
                st.subheader("Query Results")
                st.table([dict(zip(columns, row)) for row in rows])
            else:
                st.warning(columns[0])  # Display error
        else:
            st.error(sql_query)
    else:
        st.warning("Please provide a question, database file, and table name.")
