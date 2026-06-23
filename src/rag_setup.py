import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

DOCS_PATH   = Path(__file__).parent.parent / "docs_rag"
CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"


def _carregar_documentos() -> list:
    documentos = []

    loader_txt = DirectoryLoader(
        str(DOCS_PATH),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        silent_errors=True,
    )
    documentos.extend(loader_txt.load())

    for pdf_path in DOCS_PATH.rglob("*.pdf"):
        documentos.extend(PyPDFLoader(str(pdf_path)).load())

    return documentos


def build_rag() -> None:
    if not DOCS_PATH.exists() or not any(DOCS_PATH.iterdir()):
        print(f"[AVISO] Pasta '{DOCS_PATH}' vazia ou inexistente. Adicione arquivos .txt ou .pdf antes de indexar.")
        return

    print("Carregando documentos...")
    documentos = _carregar_documentos()

    if not documentos:
        print("[AVISO] Nenhum documento encontrado para indexar.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documentos)

    print(f"Gerando embeddings para {len(chunks)} chunks...")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_PATH),
    )
    vectorstore.persist()

    print(f"Base RAG criada com sucesso em '{CHROMA_PATH}' ({len(chunks)} chunks indexados).")


if __name__ == "__main__":
    build_rag()
