import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

#utility function to generate unique thread ids
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = generate_thread_id()

# session state to store messages
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = {}

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

# load the previous conversation
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
#sidebar
st.sidebar.title("My Conversations")

#new chat button
if st.sidebar.button('New Chat'):
    reset_chat()

#Chat name display
st.sidebar.write(f"Thread ID: {st.session_state['thread_id']}")

user_input = st.chat_input('Type your message here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    #streaming response
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream( # type: ignore
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG, #type: ignore
                stream_mode= 'messages'
            )
        )
    
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
