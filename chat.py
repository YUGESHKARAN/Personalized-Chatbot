import streamlit as st
import openai
import os
#from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
#load_dotenv()


#LANGCHAIN_API_KEY=ls__d543df545ab54ddf943afd9a4e62aeaf
openai.api_key = st.secrets["GROQ_API_KEY"]
#os.environ['OPENAI_API_KEY'] = "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"
st.markdown("""<h1 style="text-align:center;color:#55E6C1;">welcome to <span style='color:red;'> Chatrobot </span> </h1>""",unsafe_allow_html=True)

st.markdown("""
            
<marquee style="border-top:2px solid red; border-bottom:2px solid red; color:#fff;" direction='left' bgcolor=black>NOTE: You can enter only maximum of 4 quries</marquee>
""",
unsafe_allow_html=True)

def show(msg:str):
   if msg is None:
      st.image("images/img_banner.png")
      #st.markdown(""" <img style='width:100%' src='images/n-modified.png'> """, unsafe_allow_html=True)
      st.markdown("""
            
         <marquee style="border-top:2px solid red;  border-bottom:2px solid red; color:black;" direction='left' bgcolor=#fff>NOTE: You can enter only maximum of 4 quries</marquee>
         """,
         unsafe_allow_html=True)





if "openai_model" not in st.session_state:
   st.session_state["openai_model"]="gpt-3.5-turbo"


if "messages" not in st.session_state:
    st.session_state.messages=[]





count=0
for messages in st.session_state.messages:
   with  st.chat_message(messages["role"]):
       st.markdown(messages["content"])
   count+=1
       
if count<8:
     prompt= st.chat_input("enter the text...")
else:
   prompt=st.markdown("### your query turn over")     
   print(prompt)
     

show(prompt)     
     
if prompt is not None and count<8:
   with st.chat_message("user"):
     st.markdown(prompt)

   st.session_state.messages.append({"role":"user","content":prompt})
  

   with st.chat_message("assistant"):
        stream = openai.chat.completions.create(
           model = st.session_state["openai_model"],
           messages=[
              {"role":m["role"],"content":m["content"]}
              for m in st.session_state.messages
           ],
           stream=True
        )

        response = st.write_stream(stream)
   st.session_state.messages.append({"role":"assistant","content":response})    
    
elif (count>8):
    prompt = st.markdown("""<h3 style='color:red;text-align:center;'>🤗 your query turn over 🤗</h3>""", unsafe_allow_html=True) 
    print(prompt) 