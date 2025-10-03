import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

#utility function to generate unique thread ids
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    st.session_state['thread_id'] = generate_thread_id()
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def delete_thread(thread_id):
    """Delete a conversation thread"""
    if thread_id in st.session_state['chat_threads']:
        st.session_state['chat_threads'].remove(thread_id)
    
    # If we're deleting the current thread, create a new one
    if st.session_state['thread_id'] == thread_id:
        reset_chat()
    
    # Clear confirmation state
    st.session_state['confirm_delete'] = None
    
    # Force refresh
    st.rerun()
        
def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

# session state to store messages
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'confirm_delete' not in st.session_state:
    st.session_state['confirm_delete'] = None

# Ensure current thread is in the threads list
if st.session_state['thread_id'] not in st.session_state['chat_threads']:
    add_thread(st.session_state['thread_id'])
     
#sidebar
st.sidebar.title("My Conversations")

#new chat button
if st.sidebar.button('New Chat'):
    reset_chat()

# Confirmation dialog for deletion
if st.session_state['confirm_delete']:
    thread_to_delete = st.session_state['confirm_delete']
    st.sidebar.warning(f"Delete Thread: {thread_to_delete[:8]} ?")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Yes", key="confirm_yes"):
            delete_thread(thread_to_delete)
    
    with col2:
        if st.button("Cancel", key="confirm_cancel"):
            st.session_state['confirm_delete'] = None
            st.rerun()

#Chat name display
for thread in st.session_state['chat_threads'][::-1]:
    col1, col2 = st.sidebar.columns([3, 1])
    
    with col1:
        if st.button(f"Thread: {thread[:8]}", key=f"thread_{thread}"):
            st.session_state['thread_id'] = thread
            messages = load_conversation(thread)

            temp_msg = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    role='user'
                else:
                    role='assistant'
                temp_msg.append({'role': role, 'content': msg.content})
            
            st.session_state['message_history'] = temp_msg
            st.rerun()
    
    with col2:
        if st.button("🗑️", key=f"delete_{thread}", help="Delete conversation"):
            st.session_state['confirm_delete'] = thread
            st.rerun()

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type your message here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    
    #streaming response
    with st.chat_message('assistant'):
        def ai_stream_only():
            for message_chunk, metadata in chatbot.stream( # type: ignore
                    {'messages': [HumanMessage(content=user_input)]}, #type: ignore
                    config=CONFIG, #type: ignore
                    stream_mode= 'messages'
                ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content
                    
        ai_message = st.write_stream(ai_stream_only())
    
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
