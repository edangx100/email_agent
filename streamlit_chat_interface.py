import streamlit as st
import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from arcade_3_agent_with_memory import build_graph
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Gmail Assistant Chat", page_icon="📧", layout="wide")

st.title("📧 Gmail Assistant Chat")
st.markdown("Ask me anything about your Gmail inbox!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What would you like to know about your emails?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build messages for the agent
                messages = [HumanMessage(content=prompt)]
                inputs = {"messages": messages}
                
                # Configuration for the agent
                email = os.environ.get("EMAIL", "default@gmail.com")
                config = {"configurable": {"thread_id": "streamlit_chat", "user_id": email}}
                
                # Run the agent synchronously
                response_placeholder = st.empty()
                full_response = ""
                
                # Since we can't use async in Streamlit easily, we'll run sync
                async def run_agent():
                    response_content = ""
                    async for chunk in st.session_state.graph.astream(inputs, config=config, stream_mode="values"):
                        if chunk["messages"]:
                            last_message = chunk["messages"][-1]
                            last_message.pretty_print()
                            if hasattr(last_message, 'content') and last_message.content:
                                response_content = last_message.content
                    return response_content
                
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(run_agent())
                loop.close()
                
                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    error_msg = "I'm sorry, I couldn't process your request. Please make sure you're authorized to access Gmail tools."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("This Gmail Assistant can help you:")
    st.markdown("- View emails from today")
    st.markdown("- Search emails by sender")
    st.markdown("- Create draft emails")
    st.markdown("- Manage your inbox")
    
    st.markdown("### 🔐 Setup Required")
    st.markdown("Make sure your `.env` file contains:")
    st.markdown("- `ARCADE_API_KEY`")
    st.markdown("- `OPENAIAPIKEY`")
    st.markdown("- `EMAIL`")
    st.markdown("- `MODEL_CHOICE`")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()