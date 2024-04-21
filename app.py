from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import sql_database

from langchain_groq import ChatGroq

from langchain.sql_database import SQLDatabase
import streamlit as st
from groq import Groq

import os
import openai
#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
#os.environ['OPENAI_API_KEY'] = "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" #sample


load_dotenv()


st.set_page_config(page_title="chat with MySQL",page_icon =":speech_baloon" )

st.markdown("""<h1 style="text-align:center;color:red;">Government Scheme Navigator</h1>""",unsafe_allow_html=True)
st.markdown("""
            
<marquee style="border-top:2px solid red; border-bottom:2px solid red; color:#fff;" direction='left' bgcolor=black> Welcome to<span style="color:#55E6C1; text-align:center;"> Government Scheme Navigator <span></marquee>
""",
unsafe_allow_html=True)

def chat(chatinput:str):

    if chatinput=="":
       st.image("images/ai2.png",caption="Explore opportunities for benefits and assistance seamlessly.")
       st.markdown("""
            
<marquee style="border-top:2px solid red; border-bottom:2px solid red; color:#fff;" direction='left' bgcolor=black>NOTE: Here you can search for Government Scheme details</marquee>
""",
unsafe_allow_html=True)
      



def init_database(user:str, password:str, host:str, port:str, database:str)->SQLDatabase:
    db_uri=f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):

    template="""
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the Conversation History into account.

    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}

    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.

    For exmaple:
    Question: what are the scheme_name available?
    SQL Query: SELECT Scheme_Name FROM gov_schemes;
    Question: What are the eligibility to obtain government schemes?
    SQL Query: SELECT Eligibility FROM gov_schemes;

    Your turn:

    Question; {question}
    SQL Query:
     """
    
    prompt = ChatPromptTemplate.from_template(template)       

    llm = ChatOpenAI()
    #llm = ChatGroq(temperature=0,model_name="mixtral-8x7b-32768") 

    def get_schema(_):
        return db.get_table_info()
    

    return(
      RunnablePassthrough.assign(schema = get_schema)
      | prompt
      | llm
      | StrOutputParser()
    )


def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)


    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""

    prompt = ChatPromptTemplate.from_template(template) 

    llm = ChatOpenAI()
    #llm = ChatGroq(temperature=0,model_name="mixtral-8x7b-32768") # groq_api_key="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",

    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
        schema=lambda _: db.get_table_info(),
        response=lambda vars: db.run(vars["query"]),
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
        
    })


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content = "Hey! I'm the chat assistant dedicated to helping you navigate government schemes."),
    ]





with st.sidebar:
    st.subheader("settings")
    st.write("This is a chat application for MySQL. To connect with Database")

    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port",value="3306", key="Port")
    st.text_input("User",value="root", key="User")
    st.text_input("Password",type="password",value="root", key="Password")
    st.text_input("Database", value="government", key="Database")

    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                    st.session_state["User"],
                    st.session_state["Password"],
                    st.session_state["Host"],
                    st.session_state["Port"],
                    st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Connected to database successfully!")
            
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI" ):
            st.markdown(message.content)

    elif isinstance(message, HumanMessage):
        with st.chat_message("Human",avatar='🧑‍💻'):
            st.markdown(message.content)

user_query = st.chat_input("Ask me your need...")

if user_query is not None and user_query.strip() !="":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human",avatar='🧑‍💻'):
        st.markdown(user_query)
   
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)

    st.session_state.chat_history.append(AIMessage(content=response))    
else:
    chat("")    