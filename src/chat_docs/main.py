import chainlit as cl
from chainlit.element import Element, ElementBased
from config import settings
from conversation.chain import ConversationChain
from document_processor.pdf_processor import PDFProcessor
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_milvus import Milvus
from session_store.memory_store import MemorySessionStore


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize components such as MemorySessionStore, VectorStore, and ConversationChain when a chat starts."""
    store = MemorySessionStore()

    vectorstore = Milvus(
        OllamaEmbeddings(
            model=settings.embeddings_model_name,
            base_url=settings.embeddings_base_url,
        ),
        connection_args={"host": settings.milvus_host, "port": settings.milvus_port},
        auto_id=True,
    )

    cl.user_session.set("pdf-processor", PDFProcessor(vectorstore))
    cl.user_session.set(
        "chain",
        ConversationChain(
            Ollama(model=settings.llm_model_name, base_url=settings.llm_base_url),
            vectorstore.as_retriever(),
            store.get_session_history,
        ),
    )


@cl.step(name="process_file")
async def process_file(files: list[ElementBased]) -> str | None:
    """Process a given PDF file according to the defined chunk size, overlap and batch size."""
    pdf_files = [file for file in files if file.mime and "application/pdf" in file.mime]

    if not pdf_files:
        return None

    pdf_file = pdf_files[0]
    pdf_processor: PDFProcessor = cl.user_session.get("pdf-processor")

    await pdf_processor.process(
        pdf_file.path,
        settings.text_chunk_size,
        settings.text_chunk_overlap,
        settings.doc_process_batch_size,
    )

    return f"File `{pdf_file.name}` has been successfully processed!"


@cl.on_message
async def main(message: cl.Message) -> None:
    """Process an incoming message and any attached PDF file."""
    if message.elements:
        await process_file(message.elements)

    msg = cl.Message("")
    text_elements: list[Element] = []
    chain: ConversationChain = cl.user_session.get("chain")

    async for chunk in chain.astream(
        message.content,
        cl.user_session.get("id"),
        [cl.AsyncLangchainCallbackHandler(stream_final_answer=True)],
    ):
        if "answer" in chunk:
            await msg.stream_token(chunk["answer"])

        if "context" in chunk:
            for _source_idx, source_doc in enumerate(chunk["context"]):
                source_name = f"page {source_doc.metadata.get('page')}"
                text_elements.append(
                    cl.Text(
                        name=source_name,
                        content=source_doc.page_content,
                        display="inline",
                    )
                )

    msg.elements = text_elements  # type: ignore[assignment]
    await msg.update()
