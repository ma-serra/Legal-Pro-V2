#!/bin/bash

# Script para mover arquivos api_* para pasta api_old
# Exceto os arquivos especificados na lista de exceções

# Criar pasta api_old se não existir
mkdir -p api_old

# Lista de arquivos que NÃO devem ser movidos
EXCEPTIONS=(
    "api_qdrant_integration.py"
    "api_chat_juridico.py" 
    "api_elementos_graficos.py"
    "api_template_content.py"
    "api_especialistas.py"
    "api_extrair_texto.py"
    "api_export_estruturado.py"
    "api_analise_estatistica.py"
    "api_analise_sequencial.py"
    "api_export_analise.py"
    "api_video_export.py"
    "api_validacao_multi_agente.py"
    "api_multi_agente_otimizada.py"
    "api_gemini_simples.py"
    "api_analise_manual.py"
    "api_selecao_inteligente.py"
    "api_analise_3_agentes_identica_fixed.py"
)

# Função para verificar se arquivo está na lista de exceções
is_exception() {
    local file="$1"
    for exception in "${EXCEPTIONS[@]}"; do
        if [[ "$file" == "$exception" ]]; then
            return 0  # É exceção
        fi
    done
    return 1  # Não é exceção
}

echo "=== MOVENDO ARQUIVOS API_* PARA api_old ==="
echo "Pasta destino: $(pwd)/api_old"
echo

# Contador de arquivos movidos
moved_count=0
skipped_count=0

# Processar todos os arquivos que começam com api_
for file in api_*; do
    # Verificar se o arquivo existe (caso não haja arquivos api_*)
    if [[ ! -e "$file" ]]; then
        echo "Nenhum arquivo encontrado com padrão api_*"
        exit 0
    fi
    
    # Verificar se é um arquivo (não diretório)
    if [[ -f "$file" ]]; then
        if is_exception "$file"; then
            echo "⏭️  Mantendo: $file (na lista de exceções)"
            ((skipped_count++))
        else
            echo "📦 Movendo: $file -> api_old/"
            mv "$file" api_old/
            if [[ $? -eq 0 ]]; then
                ((moved_count++))
            else
                echo "❌ Erro ao mover: $file"
            fi
        fi
    else
        echo "⚠️  Ignorando diretório: $file"
    fi
done

echo
echo "=== RESUMO ==="
echo "Arquivos movidos: $moved_count"
echo "Arquivos mantidos: $skipped_count"
echo "Destino: api_old/"

echo
echo "=== VERIFICAÇÃO ==="
echo "Arquivos em api_old:"
ls -la api_old/ 2>/dev/null || echo "Pasta api_old vazia ou não existe"

echo
echo "Arquivos api_* restantes no diretório atual:"
ls -1 api_* 2>/dev/null || echo "Nenhum arquivo api_* restante"
