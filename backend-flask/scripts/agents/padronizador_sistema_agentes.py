#!/usr/bin/env python3
"""
Padronizador do Sistema de Agentes
Cria consistência visual e estrutural para todos os agentes jurídicos
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PadronizadorSistema:
    def __init__(self):
        """Inicializa o padronizador com conexão ao banco"""
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL não encontrada")
        
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Estrutura padrão para detalhes técnicos
        self.estrutura_padrao = {
            "provider": "openai",
            "model": "gpt-4o",
            "temperatura": 0.3,
            "top_p": 0.95,
            "top_k": 50,
            "max_tokens": 4000,
            "timeout": 60,
            "retry_attempts": 3,
            "capacidades": [],
            "fontes_conhecimento": [
                "Legislação especializada",
                "Jurisprudência atualizada", 
                "Doutrinas específicas",
                "Precedentes judiciais"
            ]
        }
        
        # Padrões visuais por categoria
        self.padroes_visuais = {
            1: {  # Direito Penal
                "cor_primaria": "#dc3545",
                "cor_secundaria": "#c41e3a", 
                "icone_categoria": "fas fa-gavel",
                "tema": "danger"
            },
            2: {  # Direito Empresarial  
                "cor_primaria": "#1565c0",
                "cor_secundaria": "#0d47a1",
                "icone_categoria": "fas fa-building",
                "tema": "primary"
            },
            3: {  # Direito Trabalhista
                "cor_primaria": "#a94513", 
                "cor_secundaria": "#8d3a0e",
                "icone_categoria": "fas fa-hard-hat",
                "tema": "warning"
            },
            4: {  # Direito Bancário
                "cor_primaria": "#1f5981",
                "cor_secundaria": "#218838", 
                "icone_categoria": "fas fa-university",
                "tema": "success"
            },
            5: {  # Direito do Consumidor
                "cor_primaria": "#17a2b8",
                "cor_secundaria": "#138496",
                "icone_categoria": "fas fa-shopping-cart", 
                "tema": "info"
            },
            6: {  # Direito Imobiliário
                "cor_primaria": "#6f42c1",
                "cor_secundaria": "#5a32a3",
                "icone_categoria": "fas fa-home",
                "tema": "purple"
            },
            7: {  # Recuperação de Crédito
                "cor_primaria": "#fd7e14",
                "cor_secundaria": "#e66a00", 
                "icone_categoria": "fas fa-money-bill-wave",
                "tema": "orange"
            }
        }

    def padronizar_estrutura_agente(self, agente_id: int, capacidades_especificas: List[str]) -> bool:
        """Padroniza a estrutura de um agente específico"""
        try:
            # Criar detalhes técnicos padronizados
            detalhes_padronizados = self.estrutura_padrao.copy()
            detalhes_padronizados["capacidades"] = capacidades_especificas
            
            # Atualizar no banco
            query = text("""
                UPDATE agente_juridico 
                SET 
                    detalhes_tecnicos = :detalhes,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :agente_id
            """)
            
            self.session.execute(query, {
                'detalhes': json.dumps(detalhes_padronizados, ensure_ascii=False, indent=2),
                'agente_id': agente_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao padronizar agente {agente_id}: {e}")
            return False

    def padronizar_cores_categoria(self) -> bool:
        """Padroniza cores e ícones por categoria"""
        try:
            for categoria_id, padroes in self.padroes_visuais.items():
                query = text("""
                    UPDATE agente_juridico 
                    SET 
                        cor_destaque = :cor_primaria,
                        icone = :icone_categoria,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE categoria_id = :categoria_id
                """)
                
                self.session.execute(query, {
                    'cor_primaria': padroes['cor_primaria'],
                    'icone_categoria': padroes['icone_categoria'],
                    'categoria_id': categoria_id
                })
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao padronizar cores: {e}")
            return False

    def remover_agentes_duplicados(self) -> int:
        """Remove agentes duplicados mantendo o mais recente"""
        try:
            # Identificar duplicatas
            query = text("""
                WITH duplicatas AS (
                    SELECT nome, categoria_id, 
                           array_agg(id ORDER BY created_at DESC) as ids
                    FROM agente_juridico 
                    WHERE ativo = true
                    GROUP BY nome, categoria_id
                    HAVING count(*) > 1
                )
                SELECT nome, categoria_id, ids[2:] as ids_para_remover
                FROM duplicatas
            """)
            
            resultados = self.session.execute(query).fetchall()
            total_removidos = 0
            
            for row in resultados:
                nome, categoria_id, ids_para_remover = row
                for agente_id in ids_para_remover:
                    # Desativar agente duplicado
                    update_query = text("""
                        UPDATE agente_juridico 
                        SET ativo = false, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :agente_id
                    """)
                    self.session.execute(update_query, {'agente_id': agente_id})
                    total_removidos += 1
                    logger.info(f"Removido duplicata: {nome} (ID: {agente_id})")
            
            return total_removidos
            
        except Exception as e:
            logger.error(f"Erro ao remover duplicatas: {e}")
            return 0

    def validar_capacidades_todos_agentes(self) -> Dict[str, Any]:
        """Valida e corrige capacidades de todos os agentes"""
        try:
            # Buscar todos os agentes ativos
            query = text("""
                SELECT id, nome, detalhes_tecnicos, categoria_id
                FROM agente_juridico 
                WHERE ativo = true
                ORDER BY categoria_id, nome
            """)
            
            resultados = self.session.execute(query).fetchall()
            agentes_corrigidos = 0
            agentes_com_problema = []
            
            for row in resultados:
                agente_id, nome, detalhes_str, categoria_id = row
                
                try:
                    # Verificar se detalhes_tecnicos é válido
                    if detalhes_str:
                        if isinstance(detalhes_str, str):
                            detalhes = json.loads(detalhes_str)
                        else:
                            detalhes = detalhes_str
                        
                        capacidades = detalhes.get('capacidades', [])
                        
                        # Verificar se há capacidades genéricas
                        if not capacidades or any('Especialidade Geral' in str(cap) for cap in capacidades):
                            agentes_com_problema.append({
                                'id': agente_id,
                                'nome': nome,
                                'problema': 'Capacidades genéricas ou vazias'
                            })
                    else:
                        agentes_com_problema.append({
                            'id': agente_id,
                            'nome': nome, 
                            'problema': 'detalhes_tecnicos ausente'
                        })
                        
                except json.JSONDecodeError:
                    agentes_com_problema.append({
                        'id': agente_id,
                        'nome': nome,
                        'problema': 'JSON inválido'
                    })
            
            return {
                'total_agentes': len(resultados),
                'agentes_com_problema': agentes_com_problema,
                'total_problemas': len(agentes_com_problema)
            }
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {'erro': str(e)}

    def gerar_relatorio_padronizacao(self) -> str:
        """Gera relatório detalhado da padronização"""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Executar validações
        relatorio_capacidades = self.validar_capacidades_todos_agentes()
        
        # Contar agentes por categoria
        query = text("""
            SELECT c.nome, COUNT(a.id) as total
            FROM categoria_juridica c
            LEFT JOIN agente_juridico a ON c.id = a.categoria_id AND a.ativo = true
            GROUP BY c.id, c.nome
            ORDER BY c.nome
        """)
        
        categorias = self.session.execute(query).fetchall()
        
        relatorio = f"""
# RELATÓRIO DE PADRONIZAÇÃO DO SISTEMA - {timestamp}

## Resumo Executivo
- **Total de Agentes Ativos**: {relatorio_capacidades.get('total_agentes', 0)}
- **Agentes com Problemas**: {relatorio_capacidades.get('total_problemas', 0)}
- **Taxa de Conformidade**: {((relatorio_capacidades.get('total_agentes', 0) - relatorio_capacidades.get('total_problemas', 0)) / max(relatorio_capacidades.get('total_agentes', 1), 1)) * 100:.1f}%

## Distribuição por Categoria
"""
        for categoria in categorias:
            relatorio += f"- **{categoria[0]}**: {categoria[1]} agentes\n"
        
        if relatorio_capacidades.get('agentes_com_problema'):
            relatorio += "\n## Agentes que Necessitam Correção\n"
            for agente in relatorio_capacidades['agentes_com_problema']:
                relatorio += f"- **{agente['nome']}** (ID: {agente['id']}): {agente['problema']}\n"
        
        relatorio += f"""
## Padrões Visuais Aplicados
- **Direito Penal**: Vermelho (#dc3545) - Ícone: gavel
- **Direito Empresarial**: Azul (#1565c0) - Ícone: building  
- **Direito Trabalhista**: Laranja (#a94513) - Ícone: hard-hat
- **Direito Bancário**: Verde (#1f5981) - Ícone: university
- **Direito do Consumidor**: Ciano (#17a2b8) - Ícone: shopping-cart
- **Direito Imobiliário**: Roxo (#6f42c1) - Ícone: home
- **Recuperação de Crédito**: Laranja (#fd7e14) - Ícone: money-bill-wave

## Estrutura Técnica Padronizada
- **Provider**: OpenAI
- **Model**: gpt-4o
- **Temperatura**: 0.3
- **Top P**: 0.95
- **Max Tokens**: 4000
- **Timeout**: 60s

---
Relatório gerado automaticamente pelo Padronizador do Sistema
"""
        return relatorio

    def executar_padronizacao_completa(self) -> Dict[str, Any]:
        """Executa padronização completa do sistema"""
        logger.info("🎯 Iniciando padronização completa do sistema...")
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'duplicatas_removidas': 0,
            'cores_padronizadas': False,
            'estruturas_corrigidas': 0,
            'relatorio': ''
        }
        
        try:
            # 1. Remover duplicatas
            duplicatas_removidas = self.remover_agentes_duplicados()
            resultados['duplicatas_removidas'] = duplicatas_removidas
            logger.info(f"✅ {duplicatas_removidas} agentes duplicados removidos")
            
            # 2. Padronizar cores por categoria
            if self.padronizar_cores_categoria():
                resultados['cores_padronizadas'] = True
                logger.info("✅ Cores e ícones padronizados por categoria")
            
            # 3. Commit das alterações
            self.session.commit()
            
            # 4. Gerar relatório
            resultados['relatorio'] = self.gerar_relatorio_padronizacao()
            
            logger.info("🎯 Padronização completa finalizada com sucesso")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro na padronização: {e}")
            self.session.rollback()
            resultados['erro'] = str(e)
            return resultados
        finally:
            self.session.close()

def main():
    """Função principal"""
    try:
        padronizador = PadronizadorSistema()
        resultados = padronizador.executar_padronizacao_completa()
        
        # Salvar relatório
        if resultados.get('relatorio'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_relatorio = f"relatorio_padronizacao_{timestamp}.md"
            
            with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
                f.write(resultados['relatorio'])
            
            print(f"📄 Relatório salvo: {arquivo_relatorio}")
        
        # Log dos resultados
        print(f"🎯 Padronização concluída:")
        print(f"   - Duplicatas removidas: {resultados.get('duplicatas_removidas', 0)}")
        print(f"   - Cores padronizadas: {'✅' if resultados.get('cores_padronizadas') else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    main()