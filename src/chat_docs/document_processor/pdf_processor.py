import asyncio

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PDFProcessor:

    """Processes PDF files and adds document chunks to a vector store."""

    def __init__(self, vectorstore: VectorStore):
        self._vectorstore = vectorstore

    async def process(self, file_path: str, chunk_size: int, chunk_overlap: int, batch_size: int) -> None:
        """Process a file by splitting it into chunks, embedding the chunks, and adding them to a vector store."""
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        splits = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ).split_documents(pages)
        num_splits = len(splits)

        tasks = [
            self._vectorstore.aadd_documents(splits[i : min(i + batch_size, num_splits)])
            for i in range(0, num_splits, batch_size)
        ]
        await asyncio.gather(*tasks)
