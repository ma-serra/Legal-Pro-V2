# Sistema de IDs Únicos para Resultados de Fluxos

## Visão Geral

O sistema de resultados de fluxos implementa **três tipos de identificadores únicos** para cada execução:

### 1. ID Sequencial (SERIAL PRIMARY KEY)
- **Tipo**: `INTEGER` auto-incremental
- **Função**: Identificador interno principal do banco
- **Exemplo**: `1`, `2`, `3`...

### 2. UUID Único (gen_random_uuid())
- **Tipo**: `UUID` gerado pelo PostgreSQL
- **Função**: Identificador globalmente único
- **Formato**: `550e8400-e29b-41d4-a716-446655440000`
- **Características**: 
  - Único em qualquer sistema
  - Criptograficamente seguro
  - Não sequencial (mais seguro)

### 3. Hash de Conteúdo (SHA-256)
- **Tipo**: `VARCHAR(64)` hash SHA-256
- **Função**: Detectar duplicatas baseadas no conteúdo
- **Geração**: `SHA-256(fluxo_id + input_original + template_gerado)`
- **Exemplo**: `a3c8f9b2d4e6h7i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

## Estrutura da Tabela

```sql
CREATE TABLE fluxo_resultado (
    id SERIAL PRIMARY KEY,                               -- ID sequencial
    uuid_resultado UUID DEFAULT gen_random_uuid() UNIQUE, -- UUID único
    fluxo_id INTEGER NOT NULL,                           -- Referência ao fluxo
    input_original TEXT,                                 -- Entrada original
    template_gerado TEXT,                               -- Template jurídico gerado
    analise_juridica TEXT,                              -- Análise jurídica
    componentes_processados INTEGER DEFAULT 0,          -- Número de componentes
    tempo_execucao VARCHAR(50),                         -- Tempo de execução
    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp
    resultado_completo JSONB,                           -- Dados completos em JSON
    status VARCHAR(20) DEFAULT 'concluido',            -- Status da execução
    hash_resultado VARCHAR(64)                          -- Hash do conteúdo
);
```

## Funções Implementadas

### `salvar_resultado_fluxo(fluxo_id, resultado_data)`
- Gera automaticamente os 3 identificadores
- Retorna objeto com: `{'id': int, 'uuid': str, 'hash': str}`

### `obter_ultimo_resultado_fluxo(fluxo_id)`
- Busca o resultado mais recente de um fluxo
- Retorna dados completos incluindo todos os IDs

### `obter_resultado_por_uuid(uuid_resultado)`
- Busca resultado específico pelo UUID
- Útil para compartilhamento e referências externas

### `listar_resultados_fluxo(fluxo_id, limite=10)`
- Lista histórico de resultados de um fluxo
- Ordenados por data decrescente

## Vantagens do Sistema

1. **Segurança**: UUIDs não são sequenciais nem previsíveis
2. **Integridade**: Hash detecta alterações no conteúdo
3. **Performance**: ID sequencial para consultas internas rápidas
4. **Flexibilidade**: Múltiplas formas de referenciar o mesmo resultado
5. **Auditoria**: Detecção automática de duplicatas

## Uso nos Templates

```html
<!-- Exibir UUID no resultado -->
<div class="result-id">ID: {{ resultado.uuid_resultado }}</div>

<!-- Link direto via UUID -->
<a href="/resultado/{{ resultado.uuid_resultado }}">Ver Resultado</a>

<!-- Verificar integridade -->
{% if resultado.hash_resultado %}
<span class="integrity-verified">✓ Integridade Verificada</span>
{% endif %}
```

## Exemplo de Retorno da API

```json
{
  "id": 15,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "hash": "a3c8f9b2d4e6h7i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "fluxo_id": 17,
  "input_original": "Analisar contrato de compra e venda...",
  "template_gerado": "CONTRATO DE COMPRA E VENDA...",
  "data_execucao": "2025-07-22T15:30:45",
  "componentes_processados": 3,
  "status": "concluido"
}
```

## Status: ✅ IMPLEMENTADO E FUNCIONAL
- Sistema completo de IDs únicos ativo
- Detecção de duplicatas por hash implementada
- APIs de consulta por ID, UUID e listagem funcionais
- Integração com templates de resultado completa