import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

config = {'configurable': {'thread_id': '1'}}

# session state to store messages
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# load the previous conversation
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

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
                config= {'configurable': {'thread_id': 'thread-1'}},
                stream_mode= 'messages'
            )
        )
    
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
