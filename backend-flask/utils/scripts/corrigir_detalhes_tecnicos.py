#!/usr/bin/env python3
"""
Script para corrigir o formato dos detalhes técnicos de todos os agentes jurídicos.
Este script verifica e converte todos os campos detalhes_tecnicos para formato JSON string.
"""
import json
import logging
from main import db
from models import AgenteJuridico

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def corrigir_detalhes_tecnicos():
    """
    Converte todos os campos detalhes_tecnicos do tipo dict para string JSON.
    """
    logger.info("Iniciando correção dos detalhes técnicos dos agentes jurídicos...")
    
    # Busca todos os agentes jurídicos
    agentes = AgenteJuridico.query.all()
    contador = 0
    
    for agente in agentes:
        try:
            # Pula se o campo for None
            if agente.detalhes_tecnicos is None:
                continue
                
            # Se já for uma string, verifica se é um JSON válido
            if isinstance(agente.detalhes_tecnicos, str):
                try:
                    # Tenta converter para dict e depois de volta para string para garantir formato correto
                    json_dict = json.loads(agente.detalhes_tecnicos)
                    agente.detalhes_tecnicos = json.dumps(json_dict)
                    contador += 1
                except json.JSONDecodeError:
                    # Se não for um JSON válido, inicializa como um dicionário vazio
                    logger.warning(f"Detalhes técnicos do agente {agente.id} não é um JSON válido. Corrigindo...")
                    agente.detalhes_tecnicos = json.dumps({})
                    contador += 1
            # Se for um dicionário, converte para string JSON
            elif isinstance(agente.detalhes_tecnicos, dict):
                agente.detalhes_tecnicos = json.dumps(agente.detalhes_tecnicos)
                contador += 1
            # Para outros tipos, como listas
            else:
                logger.warning(f"Detalhes técnicos do agente {agente.id} é do tipo {type(agente.detalhes_tecnicos)}. Corrigindo...")
                # Tenta converter para string JSON ou usa um dicionário vazio
                try:
                    agente.detalhes_tecnicos = json.dumps(agente.detalhes_tecnicos)
                except:
                    agente.detalhes_tecnicos = json.dumps({})
                contador += 1
        except Exception as e:
            logger.error(f"Erro ao processar agente {agente.id}: {str(e)}")
    
    # Salva as alterações
    try:
        db.session.commit()
        logger.info(f"Correção concluída. {contador} agentes atualizados.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar alterações: {str(e)}")

if __name__ == "__main__":
    corrigir_detalhes_tecnicos()