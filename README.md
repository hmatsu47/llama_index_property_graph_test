# llama_index_property_graph_test

[llama-index-graph-stores-postgres](https://github.com/hmatsu47/llama-index-graph-stores-postgres) を使ってグラフ RAG を試す

## PostgreSQL 17 with pgvector 0.8.0 or higher

```sh:
docker pull pgvector/pgvector:pg17
```

### for Linux

```sh:
docker run --net=host -e POSTGRES_PASSWORD='postgres' pgvector/pgvector:pg17
```

### for macOS

```sh:
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD='postgres' pgvector/pgvector:pg17
```

## Langfuse

```sh:
git clone https://github.com/langfuse/langfuse.git
cd langfuse
vi docker-compose.yml
```

- `postgres:`の`ports:`指定を`- 127.0.0.1:15432:5432`に書き換えて保存

```sh:
docker compose up
```

### 初期設定を実行

- https://qiita.com/moritalous/items/76ba9f2ad200df335d07#langfuse%E3%81%AE%E5%88%9D%E6%9C%9F%E8%A8%AD%E5%AE%9A

```sh:
touch .env
vi .env
```

- 公開鍵・秘密鍵を設定して保存

```text:
LANGFUSE_P_KEY="pk-lf-XXXXXXXX"
LANGFUSE_S_KEY="sk-lf-XXXXXXXX"
```

## Indexing

```sh:
python main.py
```

## Querying from existing index

```sh:
python from-existing.py
```
