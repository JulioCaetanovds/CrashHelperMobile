import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

mcp = FastMCP("CrashHelper-MCP")

DOCS_PATH = Path(__file__).parent.parent / "docs_rag"
CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"

@mcp.resource("docs://lista")
def listar_docs() -> str:
    if not DOCS_PATH.exists():
        return "Pasta de documentos não encontrada."
    arquivos = [f.name for f in DOCS_PATH.iterdir() if f.is_file()]
    return "\n".join(arquivos) if arquivos else "Nenhum documento encontrado."

@mcp.tool()
def buscar_na_base(query: str, k: int = 3) -> str:
    if not CHROMA_PATH.exists():
        return "Banco vetorial não encontrado. Execute a indexação primeiro."
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=embeddings)
    resultados = vectorstore.similarity_search(query, k=k)
    
    if not resultados:
        return "Nenhuma informação relevante encontrada."
    
    return "\n\n---\n\n".join(doc.page_content for doc in resultados)

if __name__ == "__main__":
    mcp.run()