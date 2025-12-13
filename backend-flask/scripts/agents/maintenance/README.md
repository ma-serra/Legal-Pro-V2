# Scripts de Manutenção de Agentes Jurídicos

Esta pasta contém scripts para manutenção e correção dos agentes jurídicos do sistema Legal Pro.

## 📋 Scripts Disponíveis

### 1. `revisar_categorizacao_agentes.py`
**Descrição:** Analisa todos os agentes ativos e detecta inconsistências entre o nome/descrição e o prompt do sistema.

**Uso:**
```bash
python3 scripts/agents/maintenance/revisar_categorizacao_agentes.py
```

**Saída:**
- Relatório no console
- Arquivo `/tmp/relatorio_agentes_categorizacao.txt`

**O que detecta:**
- Agentes com nome de uma área mas prompt de outra
- Inconsistências entre especialização declarada e prompt
- Lista de agentes que precisam correção

---

### 2. `corrigir_categorizacao_agentes.py`
**Descrição:** Corrige erros de categorização detectados, atualizando os prompts dos agentes.

**Uso:**
```bash
# 1. Primeiro execute o script de revisão
python3 scripts/agents/maintenance/revisar_categorizacao_agentes.py

# 2. Edite o script e adicione os IDs dos agentes a corrigir
# 3. Execute o script de correção
python3 scripts/agents/maintenance/corrigir_categorizacao_agentes.py
```

**Prompts disponíveis:**
- `PROMPT_ELEITORAL` - Para agentes de Direito Eleitoral
- `PROMPT_ADMINISTRATIVO` - Para agentes de Direito Administrativo

---

### 3. `atualizar_prompts_amplos.py`
**Descrição:** Atualiza todos os agentes para usar filosofia de análise AMPLA ao invés de RESTRITIVA.

**Uso:**
```bash
python3 scripts/agents/maintenance/atualizar_prompts_amplos.py
```

**O que faz:**
- Atualiza prompts com a filosofia "NA DÚVIDA, ANALISE!"
- Torna agentes menos restritivos
- Aceita documentos relacionados de forma ampla
- Mantém especialização técnica

**Áreas atualizadas:**
- Direito Tributário
- Direito Civil
- Direito Trabalhista
- Direito Penal
- Direito Previdenciário
- Direito do Consumidor
- Direito Ambiental
- + 15 outras áreas

---

## 🔧 Fluxo de Trabalho Recomendado

### Para Revisão e Correção de Categorização:

1. **Revisar:**
   ```bash
   python3 scripts/agents/maintenance/revisar_categorizacao_agentes.py
   ```

2. **Verificar relatório:**
   ```bash
   cat /tmp/relatorio_agentes_categorizacao.txt
   ```

3. **Corrigir (se necessário):**
   - Edite `corrigir_categorizacao_agentes.py`
   - Adicione IDs dos agentes na lista `agentes_exemplo`
   - Execute o script de correção

### Para Atualizar Filosofia dos Prompts:

```bash
python3 scripts/agents/maintenance/atualizar_prompts_amplos.py
```

---

## 📊 Histórico de Execuções

### Novembro 2025
- **11 agentes corrigidos** com erros de categorização
- **323 agentes atualizados** para filosofia ampla
- **0 erros** de categorização restantes após correção

---

## ⚠️ Importante

1. **Backup:** Sempre faça backup do banco antes de executar correções em massa
2. **Revisão:** Execute primeiro o script de revisão antes de corrigir
3. **Validação:** Verifique os agentes corrigidos manualmente após execução
4. **Logs:** Mantenha os relatórios para auditoria

---

## 🔍 Detecção de Áreas

O sistema detecta áreas jurídicas através de palavras-chave:

| Área | Palavras-chave |
|------|----------------|
| Tributário | tributário, tribut, icms, iss, fiscal |
| Eleitoral | eleitoral, eleição, tse, campanha |
| Civil | civil, contrato, obrigação |
| Trabalhista | trabalh, clt, emprego |
| Empresarial | empresarial, societário, sociedade |
| ... | ... |

---

## 📝 Autores

Sistema Legal Pro - Novembro 2025

---

## 📧 Suporte

Para dúvidas ou problemas, consulte a documentação principal em `/replit.md`
