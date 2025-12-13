"""
Módulo para análise comparativa entre diferentes análises de documentos.
"""
import json
import datetime
import logging
from typing import Dict, List, Any, Optional, Tuple

from flask import current_app

from models import (
    AnaliseDocumento, AnaliseComparativa, 
    Documento, AgenteJuridico
)

# Configuração de logging
logger = logging.getLogger(__name__)


class AnalisadorComparativo:
    """
    Classe responsável por comparar diferentes análises de documentos e identificar 
    pontos de concordância, divergência e elementos complementares.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o analisador comparativo.
        
        Args:
            config: Configurações opcionais para o analisador
        """
        self.config = config or {}
        self.debug = self.config.get('debug', False)
        
    def comparar_analises(self, analise_principal_id: int, analise_comparada_id: int, 
                          usuario_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Compara duas análises e identifica pontos de concordância, divergência e complementares.
        
        Args:
            analise_principal_id: ID da análise principal
            analise_comparada_id: ID da análise comparada
            usuario_id: ID do usuário solicitando a comparação (opcional)
            
        Returns:
            Dicionário com os resultados da comparação
        """
        try:
            # Busca as análises
            analise_principal = AnaliseDocumento.query.get(analise_principal_id)
            analise_comparada = AnaliseDocumento.query.get(analise_comparada_id)
            
            if not analise_principal or not analise_comparada:
                return {"success": False, "error": "Uma ou ambas as análises não foram encontradas"}
                
            # Verifica se as análises são do mesmo documento
            if analise_principal.documento_id != analise_comparada.documento_id:
                return {"success": False, "error": "As análises devem ser do mesmo documento"}
                
            # Processa a comparação
            resultado = self._processar_comparacao(analise_principal, analise_comparada)
            
            # Salva a comparação no banco de dados
            comparacao = AnaliseComparativa(
                analise_principal_id=analise_principal_id,
                analise_comparada_id=analise_comparada_id,
                usuario_id=usuario_id,
                nivel_concordancia=resultado['nivel_concordancia'],
                pontos_concordantes=json.dumps(resultado['pontos_concordantes']),
                pontos_divergentes=json.dumps(resultado['pontos_divergentes']),
                pontos_complementares=json.dumps(resultado['pontos_complementares']),
                resultado_texto=resultado['resultado_texto'],
                data_comparacao=datetime.datetime.now()
            )
            
            from main import db
            db.session.add(comparacao)
            db.session.commit()
            
            return {
                "success": True, 
                "resultado": resultado,
                "comparacao": {
                    "id": comparacao.id,
                    "data_comparacao": comparacao.data_comparacao.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao comparar análises: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def _processar_comparacao(self, analise_principal: AnaliseDocumento, 
                             analise_comparada: AnaliseDocumento) -> Dict[str, Any]:
        """
        Processa a comparação entre duas análises.
        
        Args:
            analise_principal: Objeto da análise principal
            analise_comparada: Objeto da análise comparada
            
        Returns:
            Dicionário com os resultados da comparação
        """
        try:
            # Em uma implementação real, aqui usaríamos LLMs para comparar as análises
            # Esta é uma implementação simplificada para demonstração
            
            # Níveis de concordância (1-5, onde 5 é máxima concordância)
            nivel_concordancia = 3  # Valor padrão médio
            
            # Extrai os pontos principais (seria feito por LLM na implementação real)
            pontos_concordantes = [
                "Ambas as análises concordam na interpretação dos principais fatos",
                "Ambas identificam a mesma base legal para o caso",
                "Concordam quanto à relevância das evidências apresentadas"
            ]
            
            pontos_divergentes = [
                "Discordam quanto à interpretação do artigo 5º da lei relevante",
                "Apresentam conclusões diferentes sobre a responsabilidade das partes",
                "Propõem soluções distintas para o conflito"
            ]
            
            pontos_complementares = [
                "A segunda análise acrescenta jurisprudência relevante não mencionada na primeira",
                "A primeira análise traz um histórico mais detalhado do caso",
                "A segunda análise propõe alternativas adicionais de acordo"
            ]
            
            # Gera texto de resultado
            resultado_texto = f"""
            # Resultado da Análise Comparativa
            
            ## Visão Geral
            A comparação entre as análises mostra um nível de concordância MÉDIO (3/5), com pontos importantes de convergência e algumas divergências significativas.
            
            ## Pontos de Concordância
            Os principais pontos de concordância estão relacionados à interpretação dos fatos e à base legal identificada. Ambas as análises seguem uma linha de raciocínio semelhante quanto aos princípios jurídicos aplicáveis.
            
            ## Pontos de Divergência
            As divergências mais relevantes aparecem na interpretação de aspectos específicos da legislação e nas conclusões. Estas diferenças podem impactar significativamente o resultado final da análise.
            
            ## Elementos Complementares
            As análises se complementam em diversos aspectos, trazendo perspectivas diferentes que, em conjunto, oferecem uma visão mais completa do caso.
            """
            
            return {
                "nivel_concordancia": nivel_concordancia,
                "pontos_concordantes": pontos_concordantes,
                "pontos_divergentes": pontos_divergentes,
                "pontos_complementares": pontos_complementares,
                "resultado_texto": resultado_texto
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar comparação: {str(e)}")
            raise
            
    def formatar_resultado_html(self, resultado: Dict[str, Any]) -> str:
        """
        Formata o resultado da comparação como HTML.
        
        Args:
            resultado: Dicionário com os resultados da comparação
            
        Returns:
            Resultado formatado em HTML
        """
        # Preparar o texto com as substituições necessárias
        texto_formatado = resultado.get('resultado_texto', '').replace('\n', '<br>').replace('# ', '<h3>').replace('## ', '<h4>').replace('#', '</h4>')
        nivel = resultado.get('nivel_concordancia', 3)
        
        html = f'''
<div class="analise-comparativa">
    <div class="card mb-4">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Resumo da Análise Comparativa</h5>
        </div>
        <div class="card-body">
            <p>{texto_formatado}</p>
            
            <div class="nivel-concordancia mt-3">
                <h5>Nível de Concordância: {nivel}/5</h5>
                <div class="progress">
                    <div class="progress-bar bg-success" role="progressbar" style="width: {nivel * 20}%" 
                         aria-valuenow="{nivel}" aria-valuemin="0" aria-valuemax="5"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-4">
            <div class="card mb-3">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">Pontos de Concordância</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        {self._format_list_html(resultado.get('pontos_concordantes', []))}
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card mb-3">
                <div class="card-header bg-danger text-white">
                    <h5 class="mb-0">Pontos de Divergência</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        {self._format_list_html(resultado.get('pontos_divergentes', []))}
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card mb-3">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">Pontos Complementares</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        {self._format_list_html(resultado.get('pontos_complementares', []))}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
'''
        return html
    
    def _format_list_html(self, items: List[str]) -> str:
        """
        Formata uma lista de itens como HTML.
        
        Args:
            items: Lista de itens
            
        Returns:
            HTML formatado
        """
        if not items:
            return "<li class=\"list-group-item text-muted\">Nenhum ponto identificado.</li>"
            
        return "\n".join([f"<li class=\"list-group-item\">{item}</li>" for item in items])


# Função auxiliar para uso fácil
def comparar_analises(analise_principal_id: int, analise_comparada_id: int, 
                     usuario_id: Optional[int] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Função auxiliar para comparar duas análises.
    
    Args:
        analise_principal_id: ID da análise principal
        analise_comparada_id: ID da análise comparada
        usuario_id: ID do usuário que solicitou a comparação (opcional)
        config: Configurações adicionais (opcional)
        
    Returns:
        Dicionário com os resultados da comparação
    """
    analisador = AnalisadorComparativo(config)
    return analisador.comparar_analises(analise_principal_id, analise_comparada_id, usuario_id)


def listar_analises_documento(documento_id: int) -> List[Dict[str, Any]]:
    """
    Lista todas as análises realizadas para um documento.
    
    Args:
        documento_id: ID do documento
        
    Returns:
        Lista de análises do documento
    """
    try:
        analises = AnaliseDocumento.query.filter_by(documento_id=documento_id).all()
        
        resultado = []
        for analise in analises:
            agente = AgenteJuridico.query.get(analise.agente_id)
            
            resultado.append({
                "id": analise.id,
                "agente_id": analise.agente_id,
                "agente_nome": agente.nome if agente else "Agente desconhecido",
                "data_analise": analise.data_analise.strftime("%d/%m/%Y %H:%M:%S"),
                "versao_id": analise.versao_id
            })
            
        return resultado
    except Exception as e:
        logger.error(f"Erro ao listar análises do documento: {str(e)}")
        return []


def listar_comparacoes_analise(analise_id: int) -> List[Dict[str, Any]]:
    """
    Lista todas as comparações que envolvem uma determinada análise.
    
    Args:
        analise_id: ID da análise
        
    Returns:
        Lista de comparações envolvendo a análise
    """
    try:
        # Busca comparações onde a análise é a principal
        comparacoes_principal = AnaliseComparativa.query.filter_by(analise_principal_id=analise_id).all()
        
        # Busca comparações onde a análise é a comparada
        comparacoes_secundaria = AnaliseComparativa.query.filter_by(analise_comparada_id=analise_id).all()
        
        resultado = []
        
        # Processa comparações onde a análise é a principal
        for comp in comparacoes_principal:
            analise_comparada = AnaliseDocumento.query.get(comp.analise_comparada_id)
            agente_comparado = AgenteJuridico.query.get(analise_comparada.agente_id) if analise_comparada else None
            
            resultado.append({
                "id": comp.id,
                "analise_principal_id": comp.analise_principal_id,
                "analise_comparada_id": comp.analise_comparada_id,
                "agente_comparado": agente_comparado.nome if agente_comparado else "Agente desconhecido",
                "nivel_concordancia": comp.nivel_concordancia,
                "data_comparacao": comp.data_comparacao.strftime("%d/%m/%Y %H:%M:%S"),
                "tipo_relacao": "principal"
            })
        
        # Processa comparações onde a análise é a comparada
        for comp in comparacoes_secundaria:
            analise_principal = AnaliseDocumento.query.get(comp.analise_principal_id)
            agente_principal = AgenteJuridico.query.get(analise_principal.agente_id) if analise_principal else None
            
            resultado.append({
                "id": comp.id,
                "analise_principal_id": comp.analise_principal_id,
                "analise_comparada_id": comp.analise_comparada_id,
                "agente_principal": agente_principal.nome if agente_principal else "Agente desconhecido",
                "nivel_concordancia": comp.nivel_concordancia,
                "data_comparacao": comp.data_comparacao.strftime("%d/%m/%Y %H:%M:%S"),
                "tipo_relacao": "comparada"
            })
            
        return resultado
    except Exception as e:
        logger.error(f"Erro ao listar comparações da análise: {str(e)}")
        return []
