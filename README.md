# llama_index_property_graph_test

- [llama-index-graph-stores-postgres](https://github.com/hmatsu47/llama-index-graph-stores-postgres) を使ってグラフ RAG を試す
  - Amazon Bedrock の Anthropic Claude 3.7 Sonnet と Amazon Titan Text Embeddings V2 を使用（オレゴンリージョン）

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

- DB 接続と使用モデル（LLM）・リージョン指定を記述

```text:
DB_CONNECTION_URL="postgresql://postgres:postgres@localhost:5432/postgres"
LLM_MODEL="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
EMBED_MODEL="amazon.titan-embed-text-v2:0"
REGION_NAME="us-west-2"
```

- 公開鍵・秘密鍵の指定を追記して保存

```text:
LANGFUSE_PUBLIC_KEY="pk-lf-XXXXXXXX"
LANGFUSE_SECRET_KEY="sk-lf-XXXXXXXX"
LANGFUSE_HOST="http://localhost:3000"
```

## Indexing

```sh:
python indexing.py
```

### 結果

```text:
Parsing nodes: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  7.20it/s]
Extracting paths from text: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:25<00:00,  1.29s/it]
Extracting implicit paths: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:00<00:00, 29715.22it/s]
Generating embeddings: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  2.11it/s]
Generating embeddings: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:01<00:00,  5.04it/s]
Interleafはムーアの法則によって影響を受けた企業でした。頭の良い人材と優れた技術を持っていたにもかかわらず、1990年代にIntel製プロセッサの性能が指数関数的に向上したことで、専用高性能ハードとそれに対応したソフトウェアを提供していた企業として苦境に立たされました。

一方、Viawebはウェブベースのオンラインストア作成ツールとして開発されました。当初は「Webgen」という名前でしたが、後にViawebに改名されました。このソフトウェアはユーザーが自分のウェブブラウザ上でストアを構築できる初のツールでした。サーバーサイドコードはすべてLispで書かれており、製品は成功して顧客も増えていきました。最終的に1998年にYahoo!に買収され、創業者たちは大きな利益を得ることになりました。
```

- 実際には`LlamaIndexInstrumentor`を使うとレスポンスに含まれる`usage`のフォーマットが Langfuse 形式・OpenAI 形式のいずれとも合わないもの（`{}`）が含まれるため`langfuse/utils/__init__.py`の`_convert_usage_input`で`ValueError`が発生する（実行には支障なし）
  - `ValueError: Usage object must have either {input, output, total, unit} or {promptTokens, completionTokens, totalTokens}`
  - 以降の実行時の結果も同様
- [グラフの状態（kg.html）はこちら](./kg.html)

## Querying from existing index

```sh:
python from_existing.py
```

### 結果

```text:
提供された情報によると、InterleafとViawebは異なる運命をたどりました。

Interleafは頭の良い人材と優れた技術を持っていた企業でしたが、1990年代にムーアの法則の影響で苦境に陥りました。Intel製プロセッサの性能が指数関数的に向上したため、Interleafのような専用高性能ハードとそれに対応したソフトウェアを提供していた企業は市場から排除されていきました。

一方、Viawebはロバート・モリスと共同で開発されたウェブベースのオンラインストア作成ツールで、当初は「Webgen」と呼ばれていました。これはユーザーが自分のウェブブラウザ上でストアを構築できる初のソフトウェアでした。ViawebのサーバーサイドコードはすべてLispで書かれており、ユーザーがページのスタイルを自分で定義できるコードエディタも備えていました。Viawebは1998年にYahoo!に買収され、開発者たちは大きな利益を得ることになりました。
```

## Streamlit によるシンプルなチャット

```sh:
streamlit run simple_chat.py --server.port 8080
```

![チャット画面](./screen_shot.png)
