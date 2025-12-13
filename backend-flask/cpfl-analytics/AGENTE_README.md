# 🤖 Agente Jurídico CPFL com RAG

## 📋 Visão Geral

O Agente Jurídico CPFL é um sistema de IA avançado que utiliza Retrieval-Augmented Generation (RAG) para fornecer análises jurídicas inteligentes baseadas em uma base de 3.216 processos reais da CPFL.

### Funcionalidades

- ✅ **Consultas Inteligentes**: Perguntas em linguagem natural sobre processos
- ✅ **Busca Semântica**: RAG com Qdrant para encontrar precedentes similares
- ✅ **Análise Preditiva**: Recomendações baseadas em padrões históricos
- ✅ **Geração de Peças**: Contestações e recursos fundamentados em precedentes
- ✅ **Multi-modelo**: Suporte para os modelos mais avançados
  - 🚀 **Claude Sonnet 4** (claude-sonnet-4-20250514)
  - 🚀 **GPT-5** (gpt-5)
  - 🚀 **Gemini 2.5 Flash** (gemini-2.5-flash)

## 🏗️ Arquitetura

```
Agente CPFL
├── Frontend (Chat Interface)
│   └── templates/cpfl/agente.html
├── Backend (Flask API)
│   └── cpfl-analytics/routes.py
├── Serviços
│   ├── cpfl_agent.py (Motor RAG)
│   ├── qdrant_service.py (Banco Vetorial)
│   └── knowledge_base.py (Preparação de Dados)
└── Scripts
    └── initialize_knowledge_base.py (Inicialização)
```

## 🚀 Configuração

### 1. Variáveis de Ambiente

Adicione ao seu `.env`:

```bash
# API Keys (obrigatório)
OPENAI_API_KEY=sk-...          # Para GPT-5 e GPT-4o
ANTHROPIC_API_KEY=sk-ant-...   # Para Claude Sonnet 4 e 3.5
GEMINI_API_KEY=AIza...         # Para Gemini 2.5 Flash e 1.5 Pro

# Qdrant (opcional - usa localhost se não especificado)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Deixe vazio para local
```

### 2. Instalação do Qdrant (Opção 1: Docker)

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Instalação do Qdrant (Opção 2: Cloud)

1. Crie uma conta em https://qdrant.tech/
2. Crie um cluster
3. Configure `QDRANT_URL` e `QDRANT_API_KEY`

### 4. Inicializar Base de Conhecimento

Execute o script de inicialização:

```bash
python cpfl-analytics/scripts/initialize_knowledge_base.py
```

Esse script irá:
- ✅ Carregar 3.216 processos do JSON
- ✅ Gerar embeddings usando OpenAI
- ✅ Criar collection no Qdrant
- ✅ Indexar todos os processos

**⚠️ IMPORTANTE**: Este processo pode levar de 10 a 30 minutos e custará aproximadamente $5-10 em créditos da API OpenAI (text-embedding-3-large).

## 💡 Como Usar

### Acessar Interface de Chat

1. Inicie o servidor Flask:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

2. Acesse: `http://localhost:5000/cpfl/agente`

### Exemplos de Consultas

**Análise de Precedentes:**
```
Quais processos de revisão tarifária foram favoráveis à CPFL?
```

**Estratégia Jurídica:**
```
Analise a estratégia mais eficaz em casos de qualidade de energia em Porto Alegre
```

**Geração de Peças:**
```
Gere uma contestação para um processo de cobrança indevida, baseada em precedentes favoráveis
```

**Busca Específica:**
```
Encontre processos similares sobre liminar de energia em Caxias do Sul com valor acima de R$ 100.000
```

### Filtros Disponíveis

- **Modelo IA**: Claude Sonnet 4, GPT-5, Gemini 2.5 Flash
- **Causa Raiz**: Filtrar por tipo de causa
- **Resultados**: Número de processos similares (3, 5, 10)

### Configurações de IA Otimizadas

Todos os modelos são configurados com parâmetros otimizados para análise jurídica:

- **Temperature**: 0.2 (baixa para máxima precisão)
- **Max Tokens**: 4096-8192 (respostas detalhadas)
- **Frequency Penalty**: 0.3 (evita repetições)
- **Presence Penalty**: 0.1 (mantém foco no tópico)

**GPT-5 e Gemini 2.5** suportam respostas estruturadas em JSON para análises programáticas.

## 📊 API Endpoints

### POST /cpfl/api/agente/query

Consulta ao agente com RAG:

```json
{
  "query": "Análise de processos de revisão tarifária",
  "model": "claude-3-5-sonnet-20241022",
  "filters": {
    "causa_raiz": "Revisão Tarifária",
    "apenas_favoraveis_cpfl": true
  },
  "max_processos": 5
}
```

### POST /cpfl/api/agente/gerar-peca

Geração de peça processual:

```json
{
  "tipo_peca": "contestação",
  "dados_processo": {
    "causa_raiz": "Qualidade de Energia",
    "comarca": "Porto Alegre",
    "valor": 50000
  },
  "model": "claude-3-5-sonnet-20241022"
}
```

### GET /cpfl/api/agente/stats

Estatísticas do banco vetorial:

```json
{
  "success": true,
  "stats": {
    "total_pontos": 3216,
    "vector_size": 3072,
    "distancia": "Cosine"
  }
}
```

## 🔧 Tecnologias

- **Backend**: Flask 3.0 + Python 3.11
- **IA Modelos**:
  - Claude Sonnet 4 (Anthropic)
  - GPT-5 (OpenAI)
  - Gemini 2.5 Flash (Google)
- **Embeddings**: OpenAI text-embedding-3-large
- **Banco Vetorial**: Qdrant
- **Frontend**: HTML5 + JavaScript (Vanilla)
- **Markdown**: Marked.js para renderização

## 📈 Custos Estimados

### Inicialização (Uma vez)
- Embeddings de 3.216 processos: ~$5-10 USD

### Uso Regular (Por consulta)
- Claude Sonnet 4: ~$0.003 por consulta
- GPT-5: ~$0.006 por consulta
- Gemini 2.5 Flash: ~$0.0001 por consulta (mais econômico!)
- Embeddings de busca: ~$0.0001 por consulta

💡 **Recomendação**: Use Gemini 2.5 Flash para consultas rápidas e econômicas, GPT-5 para análises complexas com JSON estruturado, e Claude Sonnet 4 para peças processuais que exigem máxima qualidade.

## 🐛 Troubleshooting

### Erro: "Qdrant connection failed"
- Verifique se o Qdrant está rodando
- Confirme QDRANT_URL correto
- Teste: `curl http://localhost:6333/collections`

### Erro: "OpenAI API key not found"
- Adicione OPENAI_API_KEY ao .env
- Reinicie o servidor Flask

### Base não inicializada
- Execute o script de inicialização primeiro
- Verifique logs em /tmp/logs/

## 📝 Próximos Passos

1. ✅ Sistema básico de RAG implementado
2. 🔄 Adicionar cache de embeddings
3. 🔄 Implementar histórico de conversas
4. 🔄 Adicionar exportação de análises em PDF
5. 🔄 Implementar feedback loop para melhorias

## 📞 Suporte

Para questões técnicas ou sugestões:
- Documentação: Ver código em cpfl-analytics/services/
- Logs: Verificar /tmp/logs/ ou console do workflow
