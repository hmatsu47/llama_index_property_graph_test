from typing import Optional
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.core.callbacks import CallbackManager

def create_bedrock_langfuse_callback_manager(public_key: str, secret_key: str, host: Optional[str] = None) -> CallbackManager:
    """
    Bedrock 用のカスタム Langfuse コールバックマネージャーを作成します
    
    Args:
        public_key: Langfuse の公開キー
        secret_key: Langfuse の秘密キー
        host: Langfuse のホスト URL (オプション)
        
    Returns:
        設定済みのコールバックマネージャー
    """
    # 標準の Langfuse コールバックハンドラーを作成
    langfuse_handler = LlamaIndexCallbackHandler(
        public_key=public_key,
        secret_key=secret_key,
        host=host
    )
    
    # オリジナルの on_event_end メソッドを保存
    original_on_event_end = langfuse_handler.on_event_end
    
    # パッチを適用した on_event_end メソッドを定義
    def patched_on_event_end(event_type, payload=None, event_id=None):
        # とりあえず何もしない（計測を正しくするため）
        
        # オリジナルのメソッドを呼び出す
        return original_on_event_end(event_type, payload, event_id)
    
    # メソッドを置き換え
    langfuse_handler.on_event_end = patched_on_event_end
    
    # コールバックマネージャーを作成して返す
    return CallbackManager([langfuse_handler])
