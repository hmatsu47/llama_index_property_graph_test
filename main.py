import asyncio
from llama_index.core import PropertyGraphIndex, Settings, SimpleDirectoryReader
from llama_index.embeddings.bedrock import BedrockEmbedding, Models
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.core.indices.property_graph import ImplicitPathExtractor, SimpleLLMPathExtractor
from llama_index.graph_stores.postgres import PostgresPropertyGraphStore
import nest_asyncio
nest_asyncio.apply()

async def main():
    documents = SimpleDirectoryReader(
        "~/llama_index_property_graph_test/data/"
    ).load_data()

    graph_store = PostgresPropertyGraphStore(
        db_connection_string="postgresql://postgres:postgres@localhost:5432/postgres",
    )
    # DB・ユーザー・パスワードはテスト用

    llm=BedrockConverse(model="us.anthropic.claude-3-7-sonnet-20250219-v1:0", region_name="us-west-2", temperature=0.0)
    embed_model=BedrockEmbedding(model_name=Models.TITAN_EMBEDDING_V2_0, region_name="us-west-2")

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

    query_engine = index.as_query_engine(include_text=True)
    response = query_engine.query("InterleafとViawebでは何が起きましたか？")
    print(response)


if __name__ == "__main__":
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
