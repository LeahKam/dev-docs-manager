import os
from pathlib import Path

from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()

from dotenv import load_dotenv

load_dotenv()

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import TextNode
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

DATA_DIR = Path("data")

TOOL_NAME_MAP = {
    "CLAUDE.md": "claude-code",
    "AGENTS.md": "cursor",
}

PINECONE_INDEX_NAME = "devdocs-manager"
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"

COHERE_MODEL = "embed-english-v3.0"


def get_tool_name(file_path: Path) -> str:
    if file_path.name in TOOL_NAME_MAP:
        return TOOL_NAME_MAP[file_path.name]
    return file_path.parent.name


def extract_title(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    return None


#LOADING
documents = []
md_files = sorted(DATA_DIR.rglob("*.md"))

for md_file in md_files:
    reader = SimpleDirectoryReader(input_files=[str(md_file)])
    docs = reader.load_data()
    for doc in docs:
        doc.metadata["tool_name"] = get_tool_name(md_file)
        doc.metadata["file_path"] = str(md_file.resolve())
        doc.metadata["file_name"] = md_file.name
        title = extract_title(doc.text)
        if title:
            doc.metadata["title"] = title
    documents.extend(docs)

print(f"Total files loaded: {len(documents)}")

#CHUNKING
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

for i, node in enumerate(nodes):
    node.metadata["chunk_id"] = i

print(f"Number of chunks: {len(nodes)}")

# EMBEDDINGS
cohere_api_key = os.environ["COHERE_API_KEY"]

embed_model = CohereEmbedding(
    api_key=cohere_api_key,
    model_name=COHERE_MODEL,
    input_type="search_document",
)

sample_embedding = embed_model.get_text_embedding(nodes[0].text)

print(f"Embedding dimension: {len(sample_embedding)}")

#INDEXING & SAVING
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

existing_indexes = [idx.name for idx in pc.list_indexes()]
if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=len(sample_embedding),
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )

pinecone_index = pc.Index(PINECONE_INDEX_NAME)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

texts = [n.text for n in nodes]
embeddings = embed_model.get_text_embedding_batch(texts)

nodes_with_embeddings = []
for node, embedding in zip(nodes, embeddings):
    new_node = TextNode(
        text=node.text,
        metadata=node.metadata,
        embedding=embedding,
    )
    nodes_with_embeddings.append(new_node)

ids = vector_store.add(nodes_with_embeddings)
print(f"Number of indexed vectors: {len(ids)}")

print("\nDone.")
