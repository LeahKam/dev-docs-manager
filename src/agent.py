from pathlib import Path

import gradio as gr
from llama_index.core import PromptTemplate
from llama_index.core import VectorStoreIndex
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from netfree_unstrict_ssl import unstrict_ssl
from pinecone import Pinecone

from src.config import (
    COHERE_API_KEY,
    COHERE_MODEL,
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
)
from src.workflow import RAGWorkflow

unstrict_ssl()

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing from the environment")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is missing from the environment")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from the environment")


TEXT_QA_TEMPLATE = PromptTemplate(load_prompt("qa_prompt.md"))


def load_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)

    vector_store = PineconeVectorStore(
        pinecone_index=pinecone_index,
    )

    embed_model = CohereEmbedding(
        api_key=COHERE_API_KEY,
        model_name=COHERE_MODEL,
        input_type="search_query",
    )

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )

index = load_index()
retriever = index.as_retriever()

llm = OpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0.1,
)
response_synthesizer = get_response_synthesizer(
    llm=llm,
    text_qa_template=TEXT_QA_TEMPLATE,
    response_mode=ResponseMode.COMPACT
)

workflow = RAGWorkflow(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    timeout=120,
)


async def chat(message, history):
    return await workflow.run(query=message)


demo = gr.ChatInterface(
    fn=chat,
    title="RAG Chat",
    description="Ask a question about the indexed documents.",
)


if __name__ == "__main__":
    demo.launch()