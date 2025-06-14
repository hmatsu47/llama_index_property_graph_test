import asyncio
from dotenv import load_dotenv
from langfuse.llama_index import LlamaIndexInstrumentor
from llama_index.core import PropertyGraphIndex, Settings
from llama_index.core.indices.property_graph import ImplicitPathExtractor, SimpleLLMPathExtractor
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.graph_stores.postgres import PostgresPropertyGraphStore
from llama_index.llms.bedrock_converse import BedrockConverse
import nest_asyncio
import os
from langfuse_patch import create_bedrock_langfuse_callback_manager

nest_asyncio.apply()

load_dotenv()

async def main():

    graph_store = PostgresPropertyGraphStore(
        db_connection_string=os.getenv("DB_CONNECTION_URL"),
    )

    # Create and set the Bedrock-compatible Langfuse callback manager
    Settings.callback_manager = create_bedrock_langfuse_callback_manager(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )

    instrumentor = LlamaIndexInstrumentor()
    instrumentor.start()

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

    query_engine = index.as_query_engine(include_text=True)
    response = query_engine.query("InterleafとViawebでは何が起きましたか？")
    print(response)

    instrumentor.flush()


if __name__ == "__main__":
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
