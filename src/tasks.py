from crewai import Agent, Task

def criar_tarefa_diagnostico(analista: Agent, conteudo_log: str) -> Task:
    return Task(
        description=(
            "Analise o seguinte log de crash:\n\n"
            f"```\n{conteudo_log}\n```\n\n"
            "Passos OBRIGATÓRIOS:\n"
            "1. Chame a ferramenta de base de conhecimento UMA VEZ usando o formato JSON estrito: {\"query\": \"RenderFlex overflowed\"}\n"
            "2. Após a resposta da ferramenta, NÃO chame mais nada.\n"
            "3. Gere o diagnóstico FINAL."
        ),
        expected_output=(
            "Obrigatório retornar EXATAMENTE neste formato Markdown com quebras de linha:\n\n"
            "**Tipo do Erro**: [Preencher]\n"
            "**Plataforma**: [Preencher]\n"
            "**Componente Afetado**: [Preencher]\n"
            "**Causa Raiz**: [Preencher]\n"
            "**Contexto da Base de Conhecimento**: [Preencher]\n"
            "**Severidade**: [Alta/Média/Baixa]"
        ),
        agent=analista,
    )

def criar_tarefa_correcao(
    engenheiro: Agent,
    repo_path: str,
    git_output: str,
    lista_arquivos: str,
) -> Task:
    return Task(
        description=(
            "Você recebeu o diagnóstico de um crash Flutter.\n\n"
            f"Histórico Git:\n{git_output}\n\n"
            f"Arquivos no repositório:\n{lista_arquivos}\n\n"
            "Ações OBRIGATÓRIAS:\n"
            "1. Chame a ferramenta 'ler_arquivo_local' passando UM arquivo da lista acima.\n"
            "2. Ao receber o código do arquivo, GERE O RELATÓRIO FINAL imediatamente.\n"
            "3. É PROIBIDO inventar caminhos ou chamar a ferramenta mais de uma vez."
        ),
        expected_output=(
            "Obrigatório retornar EXATAMENTE nestas seções Markdown:\n\n"
            "## Contexto do Repositório\n"
            "[Escreva aqui]\n\n"
            "## Arquivo Analisado\n"
            "[Escreva aqui]\n\n"
            "## Causa Técnica Detalhada\n"
            "[Escreva aqui]\n\n"
            "## Código Corrigido\n"
            "[Escreva aqui]\n\n"
            "## Explicação das Alterações\n"
            "[Escreva aqui]\n\n"
            "## Testes Recomendados\n"
            "[Escreva aqui]\n\n"
            "## Boas Práticas\n"
            "[Escreva aqui]"
        ),
        agent=engenheiro,
        context=[],
    )