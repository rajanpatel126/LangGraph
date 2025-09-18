from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from typing import TypedDict, Annotated

load_dotenv()

model = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

# checkpointer
checkpointer = InMemorySaver()

# create graph
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compile graph
chatbot = graph.compile(checkpointer=checkpointer)
