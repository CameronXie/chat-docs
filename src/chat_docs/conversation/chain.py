from typing import Any, AsyncIterator

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.language_models import LanguageModelLike
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import RetrieverLike
from langchain_core.runnables.history import (
    GetSessionHistoryCallable,
    RunnableWithMessageHistory,
)

_CTX_QUESTION_SYSTEM_PROMPT = """Take the latest user question and the chat history into account. \
    Reformulate the question to make it understandable without relying on the chat history. \
    Do not provide the answer, simply return the question as is if no changes are required."""

_ANSWER_SYSTEM_PROMPT = """As an assistant tasked with answering questions, \
    use the provided context to provide a concise, accurate response. If the answer is not known, state that clearly. \
    Please restrict your response to no more than three sentences. \
    {context}"""


class ConversationChain:

    """Represents a conversation chain that utilizes a language model, a retriever, and a session history to generate responses to user queries."""

    def __init__(
        self,
        llm: LanguageModelLike,
        retriever: RetrieverLike,
        get_session_history: GetSessionHistoryCallable,
    ):
        input_messages_key = "input"
        history_messages_key = "chat_history"

        history_aware_retriever = create_history_aware_retriever(
            llm,
            retriever,
            ChatPromptTemplate.from_messages(
                [
                    ("system", _CTX_QUESTION_SYSTEM_PROMPT),
                    MessagesPlaceholder(history_messages_key),
                    ("human", f"{{{input_messages_key}}}"),
                ]
            ),
        )

        context_docs_chain = create_stuff_documents_chain(
            llm,
            ChatPromptTemplate.from_messages(
                [
                    ("system", _ANSWER_SYSTEM_PROMPT),
                    MessagesPlaceholder(history_messages_key),
                    ("human", f"{{{input_messages_key}}}"),
                ]
            ),
        )

        self._chain = RunnableWithMessageHistory(
            create_retrieval_chain(history_aware_retriever, context_docs_chain),
            get_session_history,
            input_messages_key=input_messages_key,
            history_messages_key=history_messages_key,
            output_messages_key="answer",
        )

    async def astream(
        self, query: str, session_id: str, callbacks: list[Any] | Any | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """Asynchronously streams results of the given query."""
        async for item in self._chain.astream(
            {"input": query},
            config=RunnableConfig(
                configurable={"session_id": session_id},
                callbacks=callbacks,
            ),
        ):
            yield item
