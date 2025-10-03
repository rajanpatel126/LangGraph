from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import sqlite3

load_dotenv()

model = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

conn = sqlite3.connect('chatbot.db', check_same_thread=False)
# checkpointer
checkpointer = SqliteSaver(conn=conn)

# create graph
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compile graph
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    
    for item in checkpointer.list(None):
        all_threads.add(item.config['configurable']['thread_id']) #type: ignore
    
    return list(all_threads)

def delete_thread_from_db(thread_id):
    """Delete all data for a specific thread from the SQLite database"""
    try:
        cursor = conn.cursor()
        
        # Delete from checkpoints table
        cursor.execute("""
            DELETE FROM checkpoints 
            WHERE thread_id = ?
        """, (thread_id,))
        
        # Delete from checkpoint_blobs table if it exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='checkpoint_blobs'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
                DELETE FROM checkpoint_blobs 
                WHERE thread_id = ?
            """, (thread_id,))
        
        # Delete from checkpoint_writes table if it exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='checkpoint_writes'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
                DELETE FROM checkpoint_writes 
                WHERE thread_id = ?
            """, (thread_id,))
        
        conn.commit()
        print(f"Successfully deleted thread {thread_id} from database")
        return True
        
    except Exception as e:
        print(f"Error deleting thread {thread_id} from database: {e}")
        conn.rollback()
        return False    