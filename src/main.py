import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import typer
from crewai import Crew, Process
from agents import criar_analista, criar_engenheiro
from tasks import criar_tarefa_diagnostico, criar_tarefa_correcao
from tools import GitAnalyzerTool

app = typer.Typer(
    name="crashhelper",
    help="Assistente de Triagem e Resolução de Crashes Mobile — powered by LLM local (Ollama).",
    add_completion=False,
)

SEPARADOR = "═" * 62
REPORTS_DIR = Path(__file__).parent.parent / "reports"  # relatórios .md serão salvos aqui

_LIXO_SYCOPHANCY = [
    "i believe you are a great professional",
    "this final answer is complete",
    "i am extremely happy with it",
    "having ignored all possible issues",
    "expect an incredible quality from this work",
]


def _limpar_output(texto: str) -> str:
    return "\n".join(
        linha for linha in texto.splitlines()
        if not any(lixo in linha.lower() for lixo in _LIXO_SYCOPHANCY)
    ).strip()


def _listar_arquivos_repo(repo_path: str) -> str:
    ignorar = {".dart_tool", "build", ".flutter-plugins", ".packages", ".pub-cache", "generated"}
    extensoes = (".dart", ".kt", ".swift", ".java", ".tsx", ".ts")
    raiz = Path(repo_path)
    arquivos = []

    for ext in extensoes:
        for p in raiz.rglob(f"*{ext}"):
            if not any(parte in ignorar for parte in p.relative_to(raiz).parts):
                arquivos.append(str(p.relative_to(raiz)).replace("\\", "/"))

    if not arquivos:
        return "Nenhum arquivo de código encontrado no repositório."
    return "\n".join(f"- {a}" for a in sorted(arquivos))


def _salvar_relatorio(log_path: Path, repo_path: Path, diagnostico: str, correcao: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = REPORTS_DIR / f"relatorio_{timestamp}.md"
    conteudo = f"""# Relatório de Análise de Crash Mobile

**Data/Hora**: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
**Log analisado**: `{log_path.resolve()}`
**Repositório**: `{repo_path.resolve()}`

---

## Diagnóstico

{diagnostico}

---

## Plano de Correção

{correcao}

---
*Gerado automaticamente pelo CrashHelper Mobile*
"""
    arquivo.write_text(conteudo, encoding="utf-8")
    return arquivo


@app.command()
def analisar(
    log: Path = typer.Argument(
        ..., help="Caminho para o arquivo de log de crash (ex: error_log.txt)",
        exists=True, file_okay=True, dir_okay=False, readable=True,
    ),
    repo: Path = typer.Option(
        Path("."), "--repo", "-r",
        help="Caminho para a raiz do repositório Git do projeto.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Exibe o raciocínio interno dos agentes."),
    salvar: bool = typer.Option(True, "--salvar/--no-salvar", help="Salva o relatório .md em reports/."),
):

    typer.echo(f"\n{SEPARADOR}")
    typer.echo("CrashHelper Mobile — Análise Inteligente de Crashes")
    typer.echo(SEPARADOR)
    typer.echo(f"Log        : {log.resolve()}")
    typer.echo(f"Repositório: {repo.resolve()}")
    typer.echo(f"Relatório  : {'ativado' if salvar else 'desativado'}")
    typer.echo(f"{SEPARADOR}\n")

    conteudo_log = log.read_text(encoding="utf-8").strip()
    if not conteudo_log:
        typer.echo("[ERRO] O arquivo de log está vazio.", err=True)
        raise typer.Exit(code=1)

    repo_path_str = str(repo.resolve()).replace("\\", "/")

    typer.echo("Coletando histórico Git...")
    try:
        git_output = GitAnalyzerTool()._run(repo_path=repo_path_str, n_commits=3)
    except Exception as e:
        git_output = f"[Histórico Git indisponível: {e}]"
    typer.echo("✔  Histórico coletado.")

    typer.echo("Mapeando arquivos do repositório...")
    lista_arquivos = _listar_arquivos_repo(repo_path_str)
    typer.echo("✔  Mapeamento concluído.\n")

    typer.echo("Inicializando agentes...\n")
    analista   = criar_analista()
    engenheiro = criar_engenheiro(repo_path=repo_path_str)

    tarefa_diagnostico = criar_tarefa_diagnostico(analista, conteudo_log)
    tarefa_correcao    = criar_tarefa_correcao(engenheiro, repo_path_str, git_output, lista_arquivos)
    tarefa_correcao.context = [tarefa_diagnostico]

    crew = Crew(
        agents=[analista, engenheiro],
        tasks=[tarefa_diagnostico, tarefa_correcao],
        process=Process.sequential,
        verbose=verbose,
    )

    typer.echo("Executando pipeline de análise (isso pode levar alguns minutos)...\n")
    crew.kickoff()

    diagnostico = _limpar_output(tarefa_diagnostico.output.raw)
    correcao    = _limpar_output(tarefa_correcao.output.raw)

    typer.echo(f"\n{SEPARADOR}")
    typer.echo("RESULTADO FINAL DA ANÁLISE")
    typer.echo(SEPARADOR)
    typer.echo(correcao)
    typer.echo(f"{SEPARADOR}\n")

    if salvar:
        caminho_relatorio = _salvar_relatorio(log, repo, diagnostico, correcao)
        typer.echo(f"Relatório salvo em: {caminho_relatorio}\n")


@app.command()
def indexar(
    docs: Path = typer.Option(Path("docs_rag"), "--docs", "-d",
                              help="Pasta com documentos de conhecimento (.txt, .pdf)"),
):
    from rag_setup import build_rag, DOCS_PATH, CHROMA_PATH

    typer.echo(f"\n{SEPARADOR}")
    typer.echo("CrashHelper Mobile — Indexação da Base de Conhecimento")
    typer.echo(SEPARADOR)
    typer.echo(f"Origem  : {DOCS_PATH.resolve()}")
    typer.echo(f"Destino : {CHROMA_PATH.resolve()}")
    typer.echo(f"{SEPARADOR}\n")
    build_rag()
    typer.echo("\nIndexação concluída. Use 'analisar <log>' para iniciar uma análise.\n")

@app.command()
def servidor():
    typer.echo(f"\n{SEPARADOR}")
    typer.echo("CrashHelper Mobile — Servidor MCP")
    typer.echo(SEPARADOR)
    typer.echo("Iniciando servidor via FastMCP")
    typer.echo(f"{SEPARADOR}\n")
    
    from mcp_server import mcp
    mcp.run()


if __name__ == "__main__":
    app()