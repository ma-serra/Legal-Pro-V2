"""
Módulo para população do banco de dados com dados sintéticos
Integração do LegalSyntheticDataGenerator com o sistema Flask/PostgreSQL
"""

import sys
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.synthetic_data_generator import LegalSyntheticDataGenerator


def converter_processo_para_modelo(processo_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte dicionário do gerador sintético para formato compatível com o modelo ProcessoJuridico
    """
    # Mapeamento de campos que podem ter nomes diferentes
    processo_modelo = processo_dict.copy()
    
    # Garantir que datas sejam objetos datetime.date
    campos_data = ['data_distribuicao', 'previsao_de_pagamento', 'data_acordo']
    for campo in campos_data:
        if campo in processo_modelo and processo_modelo[campo]:
            valor = processo_modelo[campo]
            if isinstance(valor, str):
                try:
                    processo_modelo[campo] = datetime.strptime(valor, '%Y-%m-%d').date()
                except ValueError:
                    processo_modelo[campo] = None
            elif isinstance(valor, datetime):
                processo_modelo[campo] = valor.date()
    
    # Adicionar campos obrigatórios que podem estar faltando
    processo_modelo.setdefault('data_registro', datetime.now())
    processo_modelo.setdefault('data_atualizacao', datetime.now())
    
    # Garantir que valores booleanos sejam tratados corretamente
    campos_boolean = [
        'horas_extras_e_reflexos', 'adicional_noturno_e_reflexos', 
        'fgts_e_a_multa_de_40_porcento', 'verbas_rescisoria', 
        'ferias_em_dobro', 'indenizacao_por_danos_morais',
        'indenizacao_por_danos_materiais', 'adicional_de_periculosidade',
        'acidente_de_trabalho', 'estabilidade', 'equiparacao_salarial',
        'diferencas_salariais'
    ]
    
    for campo in campos_boolean:
        if campo in processo_modelo:
            # Converter para booleano se for string
            if isinstance(processo_modelo[campo], str):
                processo_modelo[campo] = processo_modelo[campo].lower() in ['true', '1', 'yes', 't']
            elif processo_modelo[campo] is None:
                processo_modelo[campo] = False
    
    return processo_modelo


def popular_banco_dados_sinteticos(
    app, 
    db, 
    ProcessoJuridico, 
    quantidade: int = 100,
    areas_personalizadas: Optional[Dict[str, int]] = None,
    limpar_antes: bool = False
) -> Dict[str, Any]:
    """
    Popula o banco de dados com dados sintéticos
    
    Args:
        app: Aplicação Flask
        db: Instância do SQLAlchemy
        ProcessoJuridico: Modelo da tabela processo_juridico
        quantidade: Número de processos a gerar
        areas_personalizadas: Distribuição personalizada por área
        limpar_antes: Se deve limpar dados existentes antes de inserir
    
    Returns:
        Dicionário com estatísticas da operação
    """
    
    with app.app_context():
        try:
            # Limpar dados existentes se solicitado
            if limpar_antes:
                ProcessoJuridico.query.delete()
                db.session.commit()
                print(f"✅ Dados existentes removidos")
            
            # Gerar dados sintéticos
            gerador = LegalSyntheticDataGenerator()
            processos_sinteticos = gerador.gerar_lote_processos(quantidade, areas_personalizadas)
            
            # Inserir no banco de dados
            processos_inseridos = 0
            erros = []
            
            for processo_dict in processos_sinteticos:
                try:
                    # Converter para formato do modelo
                    processo_modelo = converter_processo_para_modelo(processo_dict)
                    
                    # Criar instância do modelo
                    processo = ProcessoJuridico(**processo_modelo)
                    
                    # Adicionar à sessão
                    db.session.add(processo)
                    processos_inseridos += 1
                    
                except Exception as e:
                    erros.append(f"Erro ao processar processo {processo_dict.get('numero_processo_cnj', 'N/A')}: {str(e)}")
                    continue
            
            # Commit das alterações
            db.session.commit()
            
            # Gerar relatório final
            relatorio = gerador.gerar_relatorio_estatistico(processos_sinteticos)
            
            resultado = {
                'sucesso': True,
                'processos_gerados': quantidade,
                'processos_inseridos': processos_inseridos,
                'erros': erros,
                'estatisticas': relatorio,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ {processos_inseridos} processos sintéticos inseridos com sucesso")
            if erros:
                print(f"⚠️  {len(erros)} erros durante a inserção")
                for erro in erros[:5]:  # Mostrar apenas os primeiros 5 erros
                    print(f"   - {erro}")
            
            return resultado
            
        except Exception as e:
            db.session.rollback()
            resultado = {
                'sucesso': False,
                'erro': str(e),
                'processos_inseridos': 0,
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ Erro na população do banco: {str(e)}")
            return resultado


def verificar_dados_existentes(app, ProcessoJuridico) -> Dict[str, Any]:
    """
    Verifica a quantidade de dados existentes no banco
    """
    with app.app_context():
        try:
            total = ProcessoJuridico.query.count()
            
            # Estatísticas por área
            from sqlalchemy import func
            areas = db.session.query(
                ProcessoJuridico.area_juridica,
                func.count(ProcessoJuridico.id).label('quantidade')
            ).group_by(ProcessoJuridico.area_juridica).all()
            
            # Valor total
            valor_total = db.session.query(
                func.sum(ProcessoJuridico.valor_da_causa)
            ).scalar() or 0
            
            return {
                'total_processos': total,
                'distribuicao_areas': {area: quantidade for area, quantidade in areas},
                'valor_total_causas': float(valor_total),
                'ultimo_processo': ProcessoJuridico.query.order_by(
                    ProcessoJuridico.data_registro.desc()
                ).first()
            }
            
        except Exception as e:
            return {
                'erro': str(e),
                'total_processos': 0
            }


def gerar_relatorio_banco_dados(app, ProcessoJuridico) -> str:
    """
    Gera relatório detalhado dos dados no banco
    """
    with app.app_context():
        dados = verificar_dados_existentes(app, ProcessoJuridico)
        
        if 'erro' in dados:
            return f"Erro ao gerar relatório: {dados['erro']}"
        
        relatorio = f"""
╔══════════════════════════════════════════════════════════╗
║                RELATÓRIO DO BANCO DE DADOS               ║
╠══════════════════════════════════════════════════════════╣
║ Total de Processos: {dados['total_processos']:>30} ║
║ Valor Total das Causas: R$ {dados['valor_total_causas']:>25,.2f} ║
╠══════════════════════════════════════════════════════════╣
║                   DISTRIBUIÇÃO POR ÁREA                 ║
╠══════════════════════════════════════════════════════════╣"""
        
        for area, quantidade in sorted(dados['distribuicao_areas'].items()):
            percentual = (quantidade / dados['total_processos']) * 100 if dados['total_processos'] > 0 else 0
            relatorio += f"\n║ {area:<30}: {quantidade:>4} ({percentual:>5.1f}%) ║"
        
        relatorio += "\n╚══════════════════════════════════════════════════════════╝"
        
        return relatorio


# Função de conveniência para uso direto no Flask
def setup_synthetic_data_population(app, db, ProcessoJuridico):
    """
    Configura função de população de dados sintéticos no contexto da aplicação Flask
    """
    
    def popular_dados(quantidade=100, areas=None, limpar=False):
        return popular_banco_dados_sinteticos(
            app, db, ProcessoJuridico, 
            quantidade, areas, limpar
        )
    
    def verificar_dados():
        return verificar_dados_existentes(app, ProcessoJuridico)
    
    def relatorio_banco():
        return gerar_relatorio_banco_dados(app, ProcessoJuridico)
    
    # Adicionar ao contexto da aplicação
    app.popular_dados_sinteticos = popular_dados
    app.verificar_dados_processos = verificar_dados
    app.relatorio_banco_processos = relatorio_banco
    
    return {
        'popular_dados': popular_dados,
        'verificar_dados': verificar_dados,
        'relatorio_banco': relatorio_banco
    }


if __name__ == "__main__":
    # Script independente para testar a população
    print("Módulo de População do Banco de Dados")
    print("Use este módulo dentro do contexto da aplicação Flask")