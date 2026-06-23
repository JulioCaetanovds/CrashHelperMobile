from pathlib import Path
from typing import Type
import os

import git
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"  # banco vetorial gerado pelo rag_setup.py


class _QueryInput(BaseModel):
    query: str = Field(description="Termo ou descrição do erro para buscar na base de conhecimento.")


class ConsultarBaseConhecimentoTool(BaseTool):
    name: str = "Consultar Base de Conhecimento"
    description: str = (
        "Busca na base de conhecimento local (RAG) informações sobre erros, crashes "
        "e comportamentos conhecidos em aplicativos mobile Android e iOS."
    )
    args_schema: Type[BaseModel] = _QueryInput

    def _run(self, query: str) -> str:
        if not CHROMA_PATH.exists():
            return "Base de conhecimento não encontrada. Execute 'python src/rag_setup.py' primeiro."
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=embeddings)
        resultados = vectorstore.similarity_search(query, k=4)
        if not resultados:
            return "Nenhuma informação relevante encontrada na base de conhecimento."
        return "\n\n---\n\n".join(doc.page_content for doc in resultados)


class _FileInput(BaseModel):
    caminho: str = Field(
        description=(
            "Caminho do arquivo a ser lido. Pode ser relativo à raiz do repositório "
            "(ex: 'lib/main.dart') ou absoluto. A ferramenta resolve automaticamente."
        )
    )


def _normalizar(caminho: str) -> Path:
    return Path(os.path.normpath(caminho.replace("\\\\", "/").replace("\\", "/")))


class LerArquivoLocalTool(BaseTool):
    name: str = "Ler Arquivo Local"
    description: str = (
        "Lê e retorna o conteúdo de um arquivo do projeto. "
        "Aceita caminhos relativos à raiz do repositório (ex: 'lib/main.dart') "
        "ou caminhos absolutos. NÃO invente nomes de arquivo — use apenas os "
        "caminhos que apareceram no retorno do Analisador de Repositório Git."
    )
    args_schema: Type[BaseModel] = _FileInput
    # repo_path é injetado em tempo de construção, não vem do LLM
    repo_path: str = ""

    def _run(self, caminho: str) -> str:
        candidatos = []

        path_direto = _normalizar(caminho)
        candidatos.append(path_direto)

        if self.repo_path:
            raiz = _normalizar(self.repo_path)
            candidatos.append(raiz / _normalizar(caminho))
            candidatos.append(raiz / Path(caminho).name)

        for path in candidatos:
            if path.is_file():
                try:
                    conteudo = path.read_text(encoding="utf-8")
                    return f"[Arquivo: {path}]\n\n{conteudo}"
                except Exception as e:
                    return f"[ERRO] Falha ao ler '{path}': {e}"

        tentados = "\n  ".join(str(c) for c in candidatos)
        return (
            f"[ERRO] Arquivo não encontrado. Caminhos tentados:\n  {tentados}\n\n"
            "Use APENAS caminhos que apareceram literalmente no retorno do Git."
        )


class _GitInput(BaseModel):
    repo_path: str = Field(description="Caminho absoluto para a raiz do repositório Git.")
    n_commits: int = Field(default=3, description="Número de commits recentes a inspecionar.")


class GitAnalyzerTool(BaseTool):
    name: str = "Analisador de Repositório Git"
    description: str = (
        "Inspeciona os commits mais recentes de um repositório Git local. "
        "Retorna mensagens, autores, datas e arquivos modificados (caminhos RELATIVOS). "
        "Use esses caminhos relativos diretamente na ferramenta Ler Arquivo Local."
    )
    args_schema: Type[BaseModel] = _GitInput

    def _run(self, repo_path: str, n_commits: int = 3) -> str:
        repo_path = os.path.normpath(repo_path.replace("\\\\", "/").replace("\\", "/"))
        try:
            repo = git.Repo(repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            return f"[ERRO] Nenhum repositório Git encontrado em: '{repo_path}'"
        except Exception as e:
            return f"[ERRO] Falha ao abrir repositório: {e}"

        linhas = [f"## Últimos {n_commits} commits em '{Path(repo_path).name}'\n"]
        for commit in list(repo.iter_commits(max_count=n_commits)):
            arquivos = list(commit.stats.files.keys())
            linhas += [
                f"### `{commit.hexsha[:8]}` — {commit.authored_datetime.strftime('%d/%m/%Y %H:%M')}",
                f"- **Autor**: {commit.author.name}",
                f"- **Mensagem**: {commit.message.strip()}",
                f"- **Arquivos alterados** ({len(arquivos)}): {', '.join(arquivos) or 'nenhum'}",
                "",
            ]
        return "\n".join(linhas)
