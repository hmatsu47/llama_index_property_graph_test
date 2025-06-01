from dotenv import load_dotenv
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.core import PropertyGraphIndex, Settings
from llama_index.core.callbacks import CallbackManager
from llama_index.core.indices.property_graph import ImplicitPathExtractor, SimpleLLMPathExtractor
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.graph_stores.postgres import PostgresPropertyGraphStore
from llama_index.llms.bedrock_converse import BedrockConverse
from typing import Generator
import os
import streamlit as st
import time

load_dotenv()

def load_index():

    graph_store = PostgresPropertyGraphStore(
        db_connection_string=os.getenv("DB_CONNECTION_URL"),
    )

    langfuse_callback_handler = LlamaIndexCallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
    Settings.callback_manager = CallbackManager([langfuse_callback_handler])

    llm=BedrockConverse(
        model=os.getenv("LLM_MODEL"),
        region_name=os.getenv("REGION_NAME"),
        temperature=0.0,
    )
    embed_model=BedrockEmbedding(
        model_name=os.getenv("EMBED_MODEL"),
        region_name=os.getenv("REGION_NAME"),
    )

    Settings.llm = llm
    Settings.embed_model = embed_model

    index = PropertyGraphIndex.from_existing(
        embed_model=embed_model,
        llm=llm,
        kg_extractors=[
            SimpleLLMPathExtractor(llm=llm),
            ImplicitPathExtractor(),
        ],
        property_graph_store=graph_store,
        show_progress=True,
    )

    query_engine = index.as_query_engine(include_text=True, streaming=True)

    return query_engine

def stream_data(data: str) -> Generator[str, None, None]:
    for word in data:
        yield word
        time.sleep(0.01)

def convert_empty(data: str):
    if data == "Empty Response":
        data = "ごめんなさい。わかりません。"
    return data

st.title("シンプルなチャット")

if "messages" not in st.session_state:
    st.session_state['messages'] = [
        # {"role": "system", "content": ""},
        {"role": "assistant", "content": "ポール・グレアムのエッセイについて聞きたいことは何ですか？"}
    ]

if "query_engine" not in st.session_state:
    st.session_state.query_engine = load_index()

for msg in st.session_state.messages:
    if msg["role"] not in ["user", "assistant"]:
        continue
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = st.session_state.query_engine.query(prompt)
    st.session_state.messages.append({"role": "assistant", "content": convert_empty(f"{response}")})
    st.chat_message("assistant").write_stream(stream_data(convert_empty(f"{response}")))
