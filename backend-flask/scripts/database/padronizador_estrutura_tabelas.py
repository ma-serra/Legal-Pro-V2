#!/usr/bin/env python3
"""
Padronizador de Estrutura de Tabelas
Normaliza e padroniza a estrutura do banco de dados para agentes jurídicos
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

class PadronizadorEstrutura:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL não encontrada")
        
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Estrutura padronizada para campos redundantes
        self.campos_padronizados = {
            'agente_juridico': {
                'campos_obsoletos': [
                    'capacidades',  # Migrar para detalhes_tecnicos
                    'data_criacao',  # Usar created_at
                    'data_atualizacao',  # Usar updated_at
                    'nivel'  # Usar nivel_especializacao
                ],
                'campos_obrigatorios': [
                    'nome', 'categoria_id', 'detalhes_tecnicos', 
                    'ativo', 'icone', 'cor_destaque'
                ],
                'campos_padrao': {
                    'ativo': True,
                    'nivel_especializacao': 4,
                    'modelo_ai': 'openai',
                    'temperatura': 0.3,
                    'top_p': 0.95,
                    'max_tokens': 4000,
                    'top_k': 50
                }
            },
            'template_juridico': {
                'campos_obrigatorios': [
                    'nome', 'categoria_id', 'area_juridica', 
                    'tipo_documento', 'ativo'
                ],
                'campos_padrao': {
                    'ativo': True,
                    'nivel_complexidade': 'medio',
                    'tempo_estimado': 30,
                    'total_utilizacoes': 0,
                    'aprovado': False,
                    'versao': '1.0'
                }
            }
        }

    def normalizar_campos_agentes(self) -> Dict[str, Any]:
        """Normaliza campos redundantes e inconsistentes na tabela agente_juridico"""
        try:
            resultados = {
                'agentes_normalizados': 0,
                'campos_migrados': 0,
                'erros': []
            }
            
            # 1. Migrar capacidades para detalhes_tecnicos se necessário
            query_capacidades = text("""
                SELECT id, nome, capacidades, detalhes_tecnicos
                FROM agente_juridico 
                WHERE capacidades IS NOT NULL 
                  AND (detalhes_tecnicos IS NULL OR detalhes_tecnicos = '{}' OR detalhes_tecnicos = '')
            """)
            
            agentes_sem_detalhes = self.session.execute(query_capacidades).fetchall()
            
            for row in agentes_sem_detalhes:
                agente_id, nome, capacidades_old, detalhes_atual = row
                
                try:
                    # Criar estrutura padronizada
                    detalhes_padrao = {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "temperatura": 0.3,
                        "top_p": 0.95,
                        "top_k": 50,
                        "max_tokens": 4000,
                        "timeout": 60,
                        "retry_attempts": 3,
                        "capacidades": capacidades_old if capacidades_old else [],
                        "fontes_conhecimento": [
                            "Legislação especializada",
                            "Jurisprudência atualizada",
                            "Doutrinas específicas",
                            "Precedentes judiciais"
                        ]
                    }
                    
                    # Atualizar detalhes_tecnicos
                    update_query = text("""
                        UPDATE agente_juridico 
                        SET detalhes_tecnicos = :detalhes,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :agente_id
                    """)
                    
                    self.session.execute(update_query, {
                        'detalhes': json.dumps(detalhes_padrao, ensure_ascii=False),
                        'agente_id': agente_id
                    })
                    
                    resultados['campos_migrados'] += 1
                    
                except Exception as e:
                    resultados['erros'].append(f"Erro migração {nome}: {e}")
            
            # 2. Padronizar campos obrigatórios ausentes
            query_padronizar = text("""
                UPDATE agente_juridico 
                SET 
                    icone = COALESCE(icone, 'fas fa-balance-scale'),
                    cor_destaque = COALESCE(cor_destaque, '#007bff'),
                    nivel_especializacao = COALESCE(nivel_especializacao, 4),
                    modelo_ai = COALESCE(modelo_ai, 'openai'),
                    temperatura = COALESCE(temperatura, 0.3),
                    top_p = COALESCE(top_p, 0.95),
                    max_tokens = COALESCE(max_tokens, 4000),
                    top_k = COALESCE(top_k, 50),
                    updated_at = CURRENT_TIMESTAMP
                WHERE icone IS NULL 
                   OR cor_destaque IS NULL 
                   OR nivel_especializacao IS NULL
                   OR modelo_ai IS NULL
                   OR temperatura IS NULL
                   OR top_p IS NULL
                   OR max_tokens IS NULL
                   OR top_k IS NULL
            """)
            
            result = self.session.execute(query_padronizar)
            resultados['agentes_normalizados'] = result.rowcount
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro na normalização de agentes: {e}")
            return {'erro': str(e)}

    def criar_relacionamentos_padronizados(self) -> Dict[str, Any]:
        """Cria relacionamentos padronizados entre tabelas"""
        try:
            resultados = {
                'relacionamentos_criados': 0,
                'indices_criados': 0,
                'constraints_adicionadas': 0
            }
            
            # 1. Garantir foreign keys consistentes
            foreign_keys = [
                {
                    'tabela': 'agente_juridico',
                    'coluna': 'categoria_id',
                    'referencia': 'categoria_juridica(id)',
                    'nome': 'fk_agente_categoria'
                },
                {
                    'tabela': 'template_juridico', 
                    'coluna': 'categoria_id',
                    'referencia': 'categoria_juridica(id)',
                    'nome': 'fk_template_categoria'
                }
            ]
            
            for fk in foreign_keys:
                try:
                    # Verificar se FK já existe
                    check_fk = text(f"""
                        SELECT constraint_name 
                        FROM information_schema.table_constraints 
                        WHERE table_name = '{fk['tabela']}' 
                          AND constraint_name = '{fk['nome']}'
                          AND constraint_type = 'FOREIGN KEY'
                    """)
                    
                    existe = self.session.execute(check_fk).fetchone()
                    
                    if not existe:
                        # Criar FK
                        create_fk = text(f"""
                            ALTER TABLE {fk['tabela']} 
                            ADD CONSTRAINT {fk['nome']} 
                            FOREIGN KEY ({fk['coluna']}) 
                            REFERENCES {fk['referencia']}
                            ON DELETE SET NULL
                        """)
                        
                        self.session.execute(create_fk)
                        resultados['constraints_adicionadas'] += 1
                        logger.info(f"FK criada: {fk['nome']}")
                        
                except Exception as e:
                    logger.warning(f"Erro ao criar FK {fk['nome']}: {e}")
            
            # 2. Criar índices para performance
            indices = [
                ('idx_agente_categoria', 'agente_juridico', 'categoria_id'),
                ('idx_agente_ativo', 'agente_juridico', 'ativo'),
                ('idx_template_categoria', 'template_juridico', 'categoria_id'),
                ('idx_template_ativo', 'template_juridico', 'ativo'),
                ('idx_agente_nome', 'agente_juridico', 'nome'),
                ('idx_template_area', 'template_juridico', 'area_juridica')
            ]
            
            for nome_idx, tabela, coluna in indices:
                try:
                    # Verificar se índice já existe
                    check_idx = text(f"""
                        SELECT indexname 
                        FROM pg_indexes 
                        WHERE tablename = '{tabela}' 
                          AND indexname = '{nome_idx}'
                    """)
                    
                    existe = self.session.execute(check_idx).fetchone()
                    
                    if not existe:
                        create_idx = text(f"""
                            CREATE INDEX {nome_idx} ON {tabela} ({coluna})
                        """)
                        
                        self.session.execute(create_idx)
                        resultados['indices_criados'] += 1
                        logger.info(f"Índice criado: {nome_idx}")
                        
                except Exception as e:
                    logger.warning(f"Erro ao criar índice {nome_idx}: {e}")
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro na criação de relacionamentos: {e}")
            return {'erro': str(e)}

    def padronizar_metadados_tabelas(self) -> Dict[str, Any]:
        """Padroniza metadados e comentários das tabelas"""
        try:
            resultados = {'comentarios_adicionados': 0}
            
            # Comentários para tabelas principais
            comentarios_tabelas = {
                'agente_juridico': 'Agentes especializados em áreas jurídicas específicas',
                'categoria_juridica': 'Categorias/áreas do direito para organização dos agentes',
                'template_juridico': 'Templates de documentos jurídicos por área especializada'
            }
            
            # Comentários para colunas importantes
            comentarios_colunas = {
                'agente_juridico': {
                    'detalhes_tecnicos': 'Configurações IA em JSON (capacidades, modelo, parâmetros)',
                    'nivel_especializacao': 'Nível de especialização de 1-5',
                    'categoria_id': 'Referência para categoria_juridica.id',
                    'base_vetorial': 'Nome da tabela de embeddings específica',
                    'cor_destaque': 'Cor hexadecimal para interface (#RRGGBB)'
                },
                'categoria_juridica': {
                    'cor_tema': 'Cor principal da categoria para interface',
                    'ativa': 'Se categoria está disponível para uso'
                },
                'template_juridico': {
                    'categoria_id': 'Referência para categoria_juridica.id',
                    'campos': 'Definição de campos do template em JSON',
                    'nivel_complexidade': 'Complexidade: simples, medio, avancado'
                }
            }
            
            # Aplicar comentários
            for tabela, descricao in comentarios_tabelas.items():
                try:
                    comment_table = text(f"""
                        COMMENT ON TABLE {tabela} IS '{descricao}'
                    """)
                    self.session.execute(comment_table)
                    resultados['comentarios_adicionados'] += 1
                    
                except Exception as e:
                    logger.warning(f"Erro ao comentar tabela {tabela}: {e}")
            
            for tabela, colunas in comentarios_colunas.items():
                for coluna, descricao in colunas.items():
                    try:
                        comment_column = text(f"""
                            COMMENT ON COLUMN {tabela}.{coluna} IS '{descricao}'
                        """)
                        self.session.execute(comment_column)
                        resultados['comentarios_adicionados'] += 1
                        
                    except Exception as e:
                        logger.warning(f"Erro ao comentar {tabela}.{coluna}: {e}")
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro na padronização de metadados: {e}")
            return {'erro': str(e)}

    def validar_integridade_dados(self) -> Dict[str, Any]:
        """Valida integridade referencial e consistência dos dados"""
        try:
            resultados = {
                'agentes_sem_categoria': 0,
                'templates_sem_categoria': 0,
                'agentes_sem_detalhes': 0,
                'categorias_inativas_com_agentes': 0,
                'inconsistencias': []
            }
            
            # 1. Agentes sem categoria válida
            query_agentes_sem_cat = text("""
                SELECT COUNT(*)
                FROM agente_juridico a
                LEFT JOIN categoria_juridica c ON a.categoria_id = c.id
                WHERE a.ativo = true AND (c.id IS NULL OR c.ativa = false)
            """)
            resultados['agentes_sem_categoria'] = self.session.execute(query_agentes_sem_cat).scalar()
            
            # 2. Templates sem categoria válida
            query_templates_sem_cat = text("""
                SELECT COUNT(*)
                FROM template_juridico t
                LEFT JOIN categoria_juridica c ON t.categoria_id = c.id
                WHERE t.ativo = true AND (c.id IS NULL OR c.ativa = false)
            """)
            resultados['templates_sem_categoria'] = self.session.execute(query_templates_sem_cat).scalar()
            
            # 3. Agentes sem detalhes técnicos válidos
            query_agentes_sem_detalhes = text("""
                SELECT COUNT(*)
                FROM agente_juridico
                WHERE ativo = true 
                  AND (detalhes_tecnicos IS NULL 
                       OR detalhes_tecnicos = '' 
                       OR detalhes_tecnicos = '{}')
            """)
            resultados['agentes_sem_detalhes'] = self.session.execute(query_agentes_sem_detalhes).scalar()
            
            # 4. Verificar categorias inativas com agentes ativos
            query_cat_inativas = text("""
                SELECT c.nome, COUNT(a.id) as total_agentes
                FROM categoria_juridica c
                JOIN agente_juridico a ON c.id = a.categoria_id
                WHERE c.ativa = false AND a.ativo = true
                GROUP BY c.id, c.nome
            """)
            categorias_problema = self.session.execute(query_cat_inativas).fetchall()
            resultados['categorias_inativas_com_agentes'] = len(categorias_problema)
            
            # Adicionar inconsistências específicas
            for cat_nome, total in categorias_problema:
                resultados['inconsistencias'].append(
                    f"Categoria inativa '{cat_nome}' tem {total} agentes ativos"
                )
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro na validação de integridade: {e}")
            return {'erro': str(e)}

    def gerar_relatorio_estrutura(self) -> str:
        """Gera relatório completo da estrutura padronizada"""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Executar validações
        normalizacao = self.normalizar_campos_agentes()
        relacionamentos = self.criar_relacionamentos_padronizados()
        metadados = self.padronizar_metadados_tabelas()
        integridade = self.validar_integridade_dados()
        
        relatorio = f"""
# RELATÓRIO DE PADRONIZAÇÃO DE ESTRUTURA - {timestamp}

## Resumo da Normalização
- **Agentes Normalizados**: {normalizacao.get('agentes_normalizados', 0)}
- **Campos Migrados**: {normalizacao.get('campos_migrados', 0)}
- **Relacionamentos Criados**: {relacionamentos.get('constraints_adicionadas', 0)}
- **Índices Criados**: {relacionamentos.get('indices_criados', 0)}
- **Comentários Adicionados**: {metadados.get('comentarios_adicionados', 0)}

## Estrutura Padronizada

### Tabela: agente_juridico
- **Campos Obrigatórios**: nome, categoria_id, detalhes_tecnicos, ativo, icone, cor_destaque
- **Relacionamentos**: categoria_id → categoria_juridica.id
- **Índices**: categoria_id, ativo, nome
- **Formato detalhes_tecnicos**: JSON com capacidades, modelo IA, parâmetros

### Tabela: categoria_juridica
- **Campos Obrigatórios**: nome, ativa, cor_tema, icone
- **Relacionamentos**: Referenciada por agente_juridico e template_juridico
- **Padrões Visuais**: Cores específicas por área jurídica

### Tabela: template_juridico
- **Campos Obrigatórios**: nome, categoria_id, area_juridica, tipo_documento, ativo
- **Relacionamentos**: categoria_id → categoria_juridica.id
- **Índices**: categoria_id, ativo, area_juridica

## Validação de Integridade
- **Agentes sem Categoria**: {integridade.get('agentes_sem_categoria', 0)}
- **Templates sem Categoria**: {integridade.get('templates_sem_categoria', 0)}
- **Agentes sem Detalhes**: {integridade.get('agentes_sem_detalhes', 0)}
- **Categorias Inconsistentes**: {integridade.get('categorias_inativas_com_agentes', 0)}

## Inconsistências Identificadas
"""
        
        if integridade.get('inconsistencias'):
            for inconsistencia in integridade['inconsistencias']:
                relatorio += f"- {inconsistencia}\n"
        else:
            relatorio += "- Nenhuma inconsistência encontrada\n"
        
        relatorio += f"""
## Padrões de Relacionamento

### Agente → Categoria
- **Tipo**: Many-to-One (N:1)
- **Constraint**: fk_agente_categoria
- **Ação**: ON DELETE SET NULL

### Template → Categoria  
- **Tipo**: Many-to-One (N:1)
- **Constraint**: fk_template_categoria
- **Ação**: ON DELETE SET NULL

### Agente → Base Vetorial
- **Tipo**: One-to-One (1:1)
- **Campo**: base_vetorial (nome da tabela)
- **Padrão**: embeddings_[area_juridica]

## Estrutura JSON Padronizada (detalhes_tecnicos)
```json
{{
  "provider": "openai",
  "model": "gpt-4o", 
  "temperatura": 0.3,
  "top_p": 0.95,
  "top_k": 50,
  "max_tokens": 4000,
  "timeout": 60,
  "retry_attempts": 3,
  "capacidades": ["Cap1", "Cap2", "Cap3"],
  "fontes_conhecimento": ["Legislação", "Jurisprudência", "Doutrina"]
}}
```

---
Relatório gerado automaticamente pelo Padronizador de Estrutura
"""
        return relatorio

    def executar_padronizacao_completa(self) -> Dict[str, Any]:
        """Executa padronização completa da estrutura"""
        logger.info("🎯 Iniciando padronização completa da estrutura...")
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'normalizacao': {},
            'relacionamentos': {},
            'metadados': {},
            'integridade': {},
            'relatorio': ''
        }
        
        try:
            # 1. Normalizar campos dos agentes
            resultados['normalizacao'] = self.normalizar_campos_agentes()
            logger.info("✅ Normalização de campos concluída")
            
            # 2. Criar relacionamentos padronizados
            resultados['relacionamentos'] = self.criar_relacionamentos_padronizados()
            logger.info("✅ Relacionamentos padronizados")
            
            # 3. Padronizar metadados
            resultados['metadados'] = self.padronizar_metadados_tabelas()
            logger.info("✅ Metadados padronizados")
            
            # 4. Validar integridade
            resultados['integridade'] = self.validar_integridade_dados()
            logger.info("✅ Integridade validada")
            
            # 5. Commit das alterações
            self.session.commit()
            
            # 6. Gerar relatório
            resultados['relatorio'] = self.gerar_relatorio_estrutura()
            
            logger.info("🎯 Padronização estrutural concluída com sucesso")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro na padronização estrutural: {e}")
            self.session.rollback()
            resultados['erro'] = str(e)
            return resultados
        finally:
            self.session.close()

def main():
    """Função principal"""
    try:
        padronizador = PadronizadorEstrutura()
        resultados = padronizador.executar_padronizacao_completa()
        
        # Salvar relatório
        if resultados.get('relatorio'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_relatorio = f"relatorio_estrutura_tabelas_{timestamp}.md"
            
            with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
                f.write(resultados['relatorio'])
            
            print(f"📄 Relatório salvo: {arquivo_relatorio}")
        
        # Log dos resultados
        norm = resultados.get('normalizacao', {})
        rel = resultados.get('relacionamentos', {})
        meta = resultados.get('metadados', {})
        
        print(f"🎯 Padronização estrutural concluída:")
        print(f"   - Agentes normalizados: {norm.get('agentes_normalizados', 0)}")
        print(f"   - Campos migrados: {norm.get('campos_migrados', 0)}")
        print(f"   - Constraints criadas: {rel.get('constraints_adicionadas', 0)}")
        print(f"   - Índices criados: {rel.get('indices_criados', 0)}")
        print(f"   - Comentários adicionados: {meta.get('comentarios_adicionados', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    main()