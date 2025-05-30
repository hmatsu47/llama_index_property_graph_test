import asyncio
from dotenv import load_dotenv
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.core import PropertyGraphIndex, Settings, SimpleDirectoryReader
from llama_index.core.callbacks import CallbackManager
from llama_index.core.indices.property_graph import ImplicitPathExtractor, SimpleLLMPathExtractor
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.graph_stores.postgres import PostgresPropertyGraphStore
from llama_index.llms.bedrock_converse import BedrockConverse
import nest_asyncio
import os

nest_asyncio.apply()

load_dotenv()

async def main():
    documents = SimpleDirectoryReader(
        "~/llama_index_property_graph_test/data/"
    ).load_data()

    graph_store = PostgresPropertyGraphStore(
        db_connection_string=os.getenv("DB_CONNECTION_URL"),
    )

    langfuse_callback_handler = LlamaIndexCallbackHandler(
        public_key=os.getenv("LANGFUSE_P_KEY"),
        secret_key=os.getenv("LANGFUSE_S_KEY"),
        host="http://localhost:3000",
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

    index = PropertyGraphIndex.from_documents(
        documents,
        embed_model=embed_model,
        kg_extractors=[
            SimpleLLMPathExtractor(llm=llm),
            ImplicitPathExtractor(),
        ],
        property_graph_store=graph_store,
        show_progress=True,
    )

    index.property_graph_store.save_networkx_graph(name="./kg.html")

    query_engine = index.as_query_engine(include_text=True)
    response = query_engine.query("InterleafとViawebでは何が起きましたか？")
    print(response)


if __name__ == "__main__":
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
