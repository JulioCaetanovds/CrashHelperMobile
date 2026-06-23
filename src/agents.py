from crewai import Agent, LLM
from tools import ConsultarBaseConhecimentoTool, LerArquivoLocalTool

_llm = LLM(
    model="openai/llama3.2",
    base_url="http://localhost:11434/v1",
    api_key="ollama-local"
)


def criar_analista() -> Agent:
    return Agent(
        role="Analista de Diagnóstico de Crashes Mobile",
        goal=(
            "Analisar o log de crash recebido, fazer UMA ÚNICA consulta à base de conhecimento "
            "e retornar o diagnóstico estruturado. Uma consulta é suficiente."
        ),
        backstory=(
            "Especialista em diagnóstico de crashes para Android e iOS. "
            "Você é objetivo e eficiente: faz uma consulta à base de conhecimento, "
            "interpreta o resultado e entrega o diagnóstico. Nunca repete a mesma consulta."
        ),
        tools=[ConsultarBaseConhecimentoTool()],
        llm=_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def criar_engenheiro(repo_path: str) -> Agent:
    return Agent(
        role="Engenheiro de Correção de Bugs Mobile",
        goal=(
            "Ler o arquivo de código indicado e propor a correção completa do crash. "
            "Você tem exatamente UMA ferramenta: 'Ler Arquivo Local'. "
            "Use-a UMA VEZ com um caminho da lista fornecida na tarefa e, "
            "com o código em mãos, escreva imediatamente o relatório completo de correção."
        ),
        backstory=(
            "Engenheiro sênior especializado em corrigir bugs mobile. "
            "O histórico Git e a lista de arquivos existentes já estão na sua tarefa. "
            "Você escolhe UM arquivo da lista, lê seu conteúdo com 'Ler Arquivo Local' "
            "e vai direto para o Final Answer — sem tentar ler outros arquivos depois."
        ),
        tools=[LerArquivoLocalTool(repo_path=repo_path)],
        llm=_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=6,
    )