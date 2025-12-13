# Scripts do Legal Design Pro

## Estrutura de Organização

Todos os scripts estão organizados dentro da pasta `scripts/` nas seguintes subcategorias:

### 📁 **Estrutura Principal:**
- **setup/** - Scripts de configuração inicial e setup do sistema
- **database/** - Scripts relacionados ao banco de dados e migrações  
- **agents/** - Scripts para gerenciamento de agentes e assistentes
- **templates/** - Scripts para templates legais e documentos
- **validation/** - Scripts de validação e verificação
- **security/** - Scripts de segurança e auditoria
- **deployment/** - Scripts de deploy e produção
- **vectorial/** - Scripts relacionados a bases vetoriais e Qdrant
- **admin/** - Scripts administrativos e de usuários
- **maintenance/** - Scripts de manutenção e limpeza

### 📁 **Subcategorias:**
- **apis/** - Todas as APIs organizadas por tipo
  - **core/** - APIs principais
  - **analysis/** - APIs de análise
  - **export/** - APIs de exportação  
  - **multi_agent/** - APIs multi-agente
- **tests/** - Todos os testes organizados
- **examples/** - Exemplos e demonstrações
- **config/** - Arquivos de configuração
- **utils/** - Utilitários e ferramentas auxiliares

## Como usar

Execute sempre a partir da raiz do projeto:
```bash
python scripts/setup/configurar_agentes_completos.py
python scripts/apis/core/api_chat_juridico.py
```
