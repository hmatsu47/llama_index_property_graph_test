# llama_index_property_graph_test

[llama-index-graph-stores-postgres](https://github.com/hmatsu47/llama-index-graph-stores-postgres) を使ってグラフ RAG を試す

## PostgreSQL 17 with pgvector 0.8.0 or higher

```sh:
docker pull pgvector/pgvector:pg17
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD='postgres' pgvector/pgvector:pg17
```

## CREATE EXTENSION

```sql:
CREATE EXTENSION IF NOT EXISTS vector;
```

## Indexing

```sh:
python main.py
```

## Querying from existing index

```sh:
python from-existing.py
```
