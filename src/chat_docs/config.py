from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    """project settings Class."""

    llm_model_name: str
    llm_base_url: str

    embeddings_model_name: str
    embeddings_base_url: str

    milvus_host: str
    milvus_port: int

    text_chunk_size: int
    text_chunk_overlap: int
    doc_process_batch_size: int


settings = Settings()  # type: ignore[call-arg]
