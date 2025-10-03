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
