# 🤖 CrashHelper Mobile: Assistente Multiagente

Um sistema inteligente que demonstra a integração prática de arquitetura multiagente (CrewAI), RAG (Retrieval-Augmented Generation), embeddings vetoriais, protocolo MCP e modelos de linguagem locais para triagem e resolução automatizada de crashes em aplicativos mobile.

## 👥 Integrantes
- Júlio Caetano Vieira dos Santos

---

## 🏆 Objetivos Alcançados (Checklist do Projeto)
- **Arquitetura Multiagente**: 2 agentes especializados (Analista de Diagnóstico e Engenheiro de Correção) operando em fluxo sequencial.
- **RAG com Embeddings**: ChromaDB com embeddings `nomic-embed-text` locais para busca semântica na documentação.
- **Modelos Locais**: Integração 100% local com Ollama executando o modelo **LLaMA 3.2**.
- **Tools e MCP**: 3 ferramentas integradas via CrewAI e um Servidor FastMCP autônomo (expondo 1 Tool e 1 Resource).
- **Interface Terminal**: CLI rica e interativa usando Typer e Rich.
- **Base de Conhecimento**: Documentação de erros Mobile indexada no vetor.

---

## 🏗️ Arquitetura do Sistema

    ┌─────────────────────────────────────────────────────────────┐
    │                        main.py (CLI)                        │
    │          Typer · pré-execução Git · scan de arquivos        │
    └────────────────────────┬────────────────────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │ CrewAI (Sequential) │
                  └──────────┬──────────┘
                             │
              ┌──────────────▼──────────────┐
              │ 1. AGENTE ANALISTA          │
              │    Tool: RAG (ChromaDB)     │
              │    Saída: Diagnóstico       │
              └──────────────┬──────────────┘
                             │
              ┌──────────────▼──────────────┐
              │ 2. AGENTE ENGENHEIRO        │
              │    Tool: LerArquivoLocal    │
              │    Entrada: Histórico Git   │
              │    Saída: Plano de Correção │
              └──────────────┬──────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Relatório .md      │
                  │  reports/           │
                  └─────────────────────┘

---

## 🧩 Componentes Principais

### Agentes LLM (`agents.py` & `tasks.py`)
- **AnalistaAgent**: Recebe o log de crash, consulta a base de conhecimento RAG e formula o diagnóstico técnico estruturado.
- **EngenheiroAgent**: Recebe o diagnóstico, lê os arquivos do código-fonte do repositório (resolvendo caminhos dinamicamente) e propõe a solução em código.

### Sistema de RAG (`rag_setup.py`)
- **Embeddings**: `nomic-embed-text` via Ollama.
- **Armazenamento**: ChromaDB persistente local.
- **Indexação**: Chunk size de 1000 tokens com overlap de 150. Recupera contexto (Top-k) para enriquecer o diagnóstico.

### Servidor MCP (`mcp_server.py`)
- Implementa o **Model Context Protocol (FastMCP)** padronizando o acesso aos dados:
  - **Resource**: `docs://lista` (Expõe a lista de documentos lidos pelo RAG).
  - **Tool**: `buscar_rag` (Expõe a busca semântica do ChromaDB para clientes universais).

---

## 💻 Tecnologias Utilizadas
- **CrewAI**: Orquestração multiagente.
- **Ollama**: Execução local de modelos (`llama3.2` e `nomic-embed-text`).
- **LangChain / ChromaDB**: Pipeline de Embeddings e RAG.
- **FastMCP**: Implementação do Model Context Protocol.
- **Python 3.11+ / Typer**: Interface de linha de comando.
- **GitPython**: Análise estática de repositórios.

---

## 🚀 Instalação e Execução

### 1. Pré-requisitos
* Python 3.11+
* [Ollama](https://ollama.com) instalado.

Configuração do Ollama no terminal:

    # Baixar o modelo LLaMA 3.2 e Embeddings
    ollama pull llama3.2
    ollama pull nomic-embed-text
    
    # Iniciar o servidor (geralmente em localhost:11434)
    ollama serve

### 2. Configuração do Projeto

    # Criar e ativar o ambiente virtual
    python -m venv venv
    venv\Scripts\activate  # Windows
    # source venv/bin/activate # macOS/Linux
    
    # Instalar as dependências
    pip install -r requirements.txt

### 3. Utilização do Sistema

**Passo A: Indexar a Base de Dados (RAG)**
Gera o banco vetorial a partir da pasta `docs_rag/`.

    python src/main.py indexar

**Passo B: Executar a Análise de Crash**
Gera o relatório interagindo com o projeto cobaia.

    python src/main.py analisar error_log.txt --repo "app_cobaia" --verbose

**Passo C: Testar o Servidor MCP**
Inicia o servidor de protocolo de contexto.

    python src/main.py servidor

---

## ⚠️ Limitações Conhecidas

O sistema foi desenvolvido e validado com o modelo **LLaMA 3.2**, focado em execução 100% local e fluida em hardware padrão. Isso garante que o projeto seja testável em qualquer máquina sem depender de APIs pagas ou clusters de GPU. Devido à natureza enxuta de modelos menores, as seguintes características são esperadas:

- **Abstração de Código**: O modelo possui excelente capacidade de raciocínio para apontar a causa raiz (ex: overflow de layout) e a direção da solução. No entanto, o trecho de código gerado no relatório final pode ser simplificado ou apresentar alucinações estruturais (ex: gerar um `MyWidget` genérico).
- **Foco da Ferramenta**: O relatório deve ser interpretado como um **guia de diagnóstico e orientação técnica** avançada para o desenvolvedor, e não como um patch de código infalível para copiar e colar.

A arquitetura do sistema (Agentes, RAG, FastMCP) é agnóstica. Se a exata mesma infraestrutura for conectada a um modelo de maior densidade (como o LLaMA 3.1 70B ou Qwen 2.5 Coder 32B), a saída do código será estruturalmente perfeita e pronta para produção.

*(Todos os relatórios gerados são salvos automaticamente na pasta `reports/`)*