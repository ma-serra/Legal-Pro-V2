"""
Preparação da base de conhecimento CPFL para RAG
Estrutura processos jurídicos para embeddings otimizados
"""

import json
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def prepare_processos_for_embedding(processos_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Estrutura cada processo em formato otimizado para embeddings
    """
    processed = []
    
    for idx, processo in enumerate(processos_raw, start=1):
        texto_completo = f"""
PROCESSO: {processo.get('Número do Processo', 'N/A')}
SITUAÇÃO: {processo.get('Situação', 'N/A')}
CAUSA-RAIZ: {processo.get('Causa-Raiz', 'N/A')}
COMARCA: {processo.get('Comarca Desdobramento', 'N/A')}
FASE: {processo.get('Fase', 'N/A')}
CLASSIFICAÇÃO DE RISCO: {processo.get('Classificação', 'N/A')}
VALOR ENVOLVIDO: R$ {processo.get('Valor Envolvido Atual - Passiva', 0):,.2f}

DECISÃO 1ª INSTÂNCIA: {processo.get('Decisão (1ª Instância)', 'Pendente')}
DECISÃO 2ª INSTÂNCIA: {processo.get('Decisão (2ª Instância)', 'Não aplicável')}
RESULTADO FINAL: {processo.get('Resultado final', 'Em andamento')}

ESTRATÉGIA: {processo.get('Acordo x Defesa', 'N/A')}
POSSUI LIMINAR: {processo.get('Possui liminar', 'N/A')}

CONTEXTO ADICIONAL:
- Tipo de Ação: {processo.get('Tipo de Ação', 'N/A')}
- Parte Contrária: {processo.get('Parte Contrária', 'N/A')}
- Escritório: {processo.get('Escritório', 'N/A')}
- Advogado Responsável: {processo.get('Advogado Responsável', 'N/A')}
- Vara: {processo.get('Vara', 'N/A')}
- Juiz: {processo.get('Juiz/Desembargador', 'N/A')}
        """.strip()
        
        decisao_1 = processo.get('Decisão (1ª Instância)', '')
        resultado_final = processo.get('Resultado final', '')
        
        favoravel = (
            'Improcedente' in decisao_1 or 
            'Improcedente' in resultado_final or
            'Extinto' in resultado_final
        )
        
        desfavoravel = (
            'Procedente' in decisao_1 or
            'Procedente' in resultado_final
        )
        
        metadata = {
            'id_processo': idx,
            'numero_processo': processo.get('Número do Processo', ''),
            'causa_raiz': processo.get('Causa-Raiz', ''),
            'comarca': processo.get('Comarca Desdobramento', ''),
            'fase': processo.get('Fase', ''),
            'classificacao': processo.get('Classificação', ''),
            'valor_envolvido': float(processo.get('Valor Envolvido Atual - Passiva', 0)),
            'decisao_1_instancia': processo.get('Decisão (1ª Instância)', ''),
            'decisao_2_instancia': processo.get('Decisão (2ª Instância)', ''),
            'resultado_final': processo.get('Resultado final', ''),
            'possui_liminar': processo.get('Possui liminar', '') == 'Sim',
            'acordo_defesa': processo.get('Acordo x Defesa', ''),
            'tipo_acao': processo.get('Tipo de Ação', ''),
            'vara': processo.get('Vara', ''),
            'juiz': processo.get('Juiz/Desembargador', ''),
            'situacao': processo.get('Situação', ''),
            
            'favoravel_cpfl': favoravel,
            'desfavoravel_cpfl': desfavoravel,
            'tem_decisao_final': bool(resultado_final),
            'valor_alto': float(processo.get('Valor Envolvido Atual - Passiva', 0)) > 100000
        }
        
        processed.append({
            'id': idx,
            'texto': texto_completo,
            'metadata': metadata
        })
    
    logger.info(f"✅ {len(processed)} processos preparados para embedding")
    return processed


def chunk_processo(processo: Dict[str, Any], max_tokens: int = 512) -> List[Dict[str, Any]]:
    """
    Divide textos longos em chunks menores se necessário
    """
    palavras = processo['texto'].split()
    
    if len(palavras) <= max_tokens:
        return [{
            'id': f"{processo['id']}_0",
            'texto': processo['texto'],
            'metadata': {**processo['metadata'], 'chunk_index': 0}
        }]
    
    chunks = []
    for i in range(0, len(palavras), max_tokens):
        chunk = ' '.join(palavras[i:i + max_tokens])
        chunks.append({
            'id': f"{processo['id']}_{len(chunks)}",
            'texto': chunk,
            'metadata': {
                **processo['metadata'],
                'chunk_index': len(chunks),
                'is_chunked': True
            }
        })
    
    return chunks


def load_processos_from_json(filepath: str = 'cpfl-analytics/data/processed/cpfl_processos_completo.json') -> List[Dict[str, Any]]:
    """Carrega processos do arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ {len(data)} processos carregados de {filepath}")
        return data
    except Exception as e:
        logger.error(f"❌ Erro ao carregar processos: {e}")
        return []
