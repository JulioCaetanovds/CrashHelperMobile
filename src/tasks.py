from crewai import Agent, Task

def criar_tarefa_diagnostico(analista: Agent, conteudo_log: str) -> Task:
    return Task(
        description=(
            "Analise o seguinte log de crash:\n\n"
            f"```\n{conteudo_log}\n```\n\n"
            "Passos:\n"
            "1. Identifique a exceção, a plataforma e o componente de origem.\n"
            "2. Faça UMA ÚNICA chamada à ferramenta de base de conhecimento para buscar contexto.\n"
            "   ATENÇÃO PARA O FORMATO DA FERRAMENTA: O Action Input DEVE ser estritamente um JSON plano apenas com a chave 'query'. Exemplo exato: {\"query\": \"RenderFlex overflowed\"}\n"
            "   Após receber a Observation, vá direto para o Final Answer. Não repita a chamada.\n"
            "3. Escreva o diagnóstico estruturado."
        ),
        expected_output=(
            "Diagnóstico em Português do Brasil com:\n"
            "- **Tipo do Erro**\n"
            "- **Plataforma**\n"
            "- **Componente Afetado**\n"
            "- **Causa Raiz**\n"
            "- **Contexto da Base de Conhecimento**\n"
            "- **Severidade**: Crítica / Alta / Média / Baixa"
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
            "Você recebeu o diagnóstico do Analista sobre um crash Flutter.\n\n"

            "## Histórico Git (já coletado — NÃO chame nenhuma ferramenta Git)\n\n"
            f"{git_output}\n\n"
            "---\n\n"

            "## Arquivos de código existentes no repositório\n\n"
            "ESTES SÃO OS ÚNICOS ARQUIVOS QUE EXISTEM. Qualquer outro caminho retornará ERRO.\n\n"
            f"{lista_arquivos}\n\n"
            "---\n\n"

            "## SUA ÚNICA AÇÃO OBRIGATÓRIA\n\n"
            "1. Com base no diagnóstico e no histórico Git, escolha UM arquivo da lista acima.\n"
            "2. Chame 'Ler Arquivo Local' UMA VEZ com o caminho relativo exatamente como está na lista.\n"
            "3. Ao receber a resposta da ferramenta com o código-fonte, NÃO chame ferramentas novamente.\n"
            "4. GERE IMEDIATAMENTE O RELATÓRIO FINAL usando OBRIGATORIAMENTE as seções solicitadas."
        ),
        expected_output=(
            "Relatório técnico completo em Português do Brasil contendo EXATAMENTE estas seções:\n\n"
            "## Contexto do Repositório\n"
            "## Arquivo Analisado\n"
            "## Causa Técnica Detalhada\n"
            "## Código Corrigido\n"
            "## Explicação das Alterações\n"
            "## Testes Recomendados\n"
            "## Boas Práticas"
        ),
        agent=engenheiro,
        context=[],
    )