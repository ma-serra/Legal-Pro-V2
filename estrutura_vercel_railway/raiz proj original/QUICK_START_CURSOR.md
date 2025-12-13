# Quick Start - Legal Design Pro V2 no Cursor

## ✅ EXPORTAÇÃO COMPLETA CONCLUÍDA!

O sistema **Legal Design Pro V2** foi exportado com sucesso para o Cursor. Você tem duas opções:

### 📦 Opção 1: Arquivo ZIP (Recomendado)
```
Legal_Design_Pro_V2_Cursor_20250727_0104.zip
```
- Download direto do arquivo compactado
- Extrair e importar no Cursor
- Tudo organizado e pronto

### 📁 Opção 2: Pasta Completa
```
Legal_Design_Pro_V2_Cursor_Export/
```
- Pasta com todos os arquivos
- Copiar diretamente para seu projeto
- Estrutura já organizada

## 🚀 3 PASSOS PARA COMEÇAR

### 1. Import no Cursor
```bash
# Abrir Cursor IDE
# File → Open Folder
# Selecionar: Legal_Design_Pro_V2_Cursor_Export
```

### 2. Configurar Ambiente
```bash
# Terminal no Cursor
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r dependencies.txt
```

### 3. Configurar APIs
```bash
# Copiar template
cp .env.example .env

# Editar .env com suas chaves:
# - OPENAI_API_KEY=sk-...
# - ANTHROPIC_API_KEY=sk-ant-...
# - GOOGLE_API_KEY=AIza...
# - DATABASE_URL=postgresql://...
```

## 📊 O QUE VOCÊ TEM AGORA

### ✅ Sistema Completo
- **349KB** de código principal (main.py + app.py)
- **46 templates HTML** responsivos
- **8 módulos** especializados
- **323 agentes jurídicos** (configurados via banco)
- **461 templates jurídicos** (configurados via banco)

### ✅ Funcionalidades Prontas
- Análise multi-agente de documentos
- Transcrição de áudio/vídeo
- Geração de mapas mentais
- Sistema de comparação de documentos
- Interface web moderna
- Base vetorial híbrida

### ✅ Configuração Profissional
- Dependencies organizadas
- Variáveis de ambiente estruturadas
- Documentação completa
- Scripts de deploy prontos

## 🔧 APIS NECESSÁRIAS

### Obrigatórias (Sistema Principal)
1. **OpenAI**: GPT-4o para análise de documentos
2. **Anthropic**: Claude 3.5 Sonnet para fallback
3. **Google**: Gemini 2.5 Flash para análise alternativa
4. **PostgreSQL**: Banco principal com pgvector

### Funcionais Específicas
5. **AssemblyAI**: Transcrição de áudio/vídeo ($50 grátis)
6. **Qdrant Cloud**: Banco vetorial (tier gratuito)

## 🌐 URLS APÓS INICIALIZAR

```bash
# Executar sistema
python main.py

# Acessar funcionalidades:
http://localhost:5000                              # Dashboard
http://localhost:5000/validacao-multi-agente-expandida  # Análise docs
http://localhost:5000/juridico/especialistas       # 323 agentes
http://localhost:5000/video/                      # Transcrição
http://localhost:5000/mapa-mental/                # Mapas mentais
```

## 📋 TROUBLESHOOTING RÁPIDO

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r dependencies.txt
```

### Erro de API Keys
```bash
# Verificar .env
cat .env | grep API_KEY

# Testar conexão
python -c "import openai; print('OpenAI OK')"
```

### Erro de Banco
```bash
# Instalar PostgreSQL
# Criar database: legal_design_pro_v2
# Instalar extensão: CREATE EXTENSION vector;
```

## 🎯 PRÓXIMOS PASSOS

1. **Configurar banco PostgreSQL** com pgvector
2. **Obter API keys** das 4 APIs principais
3. **Testar funcionalidades** principais
4. **Configurar Qdrant Cloud** para busca vetorial
5. **Personalizar** templates conforme necessário

## 📞 SUPORTE

### Arquivos de Ajuda Incluídos
- `INSTALACAO_CURSOR.md` - Setup completo
- `README_CURSOR.md` - Visão geral
- `EXPORT_INFO.json` - Metadados técnicos
- `.env.example` - Template de configuração

### Links Úteis
- OpenAI: https://platform.openai.com/
- Anthropic: https://console.anthropic.com/
- Google AI: https://aistudio.google.com/
- Qdrant Cloud: https://cloud.qdrant.io/
- AssemblyAI: https://www.assemblyai.com/

**🎉 Sistema Legal Design Pro V2 pronto para rodar no Cursor!**

Tempo estimado de setup: **30-45 minutos** (incluindo APIs)