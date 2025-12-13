"""
Gerenciador Central dos Módulos Jurídicos Especializados
Integra todos os assistentes especializados com a nova arquitetura moderna
"""
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, Blueprint, request, jsonify, render_template
from datetime import datetime
import os

from modules.assistentes import obter_assistente, ASSISTENTES_JURIDICOS

logger = logging.getLogger(__name__)

class GerenciadorModulos:
    """Gerenciador central dos módulos jurídicos especializados"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.assistentes_cache = {}
        self.modulos_ativos = {}
        
        # Configuração dos módulos por área
        self.configuracao_modulos = {
            'criminal': {
                'nome': 'Direito Criminal',
                'icone': 'fas fa-gavel',
                'cor': '#dc3545',
                'rota': '/juridico/criminal',
                'templates_especificos': ['denuncia_criminal', 'defesa_previa', 'habeas_corpus']
            },
            'agrario': {
                'nome': 'Direito Agrário',
                'icone': 'fas fa-seedling',
                'cor': '#1f5981',
                'rota': '/juridico/agrario',
                'templates_especificos': ['contrato_arrendamento', 'acao_usucapiao_rural']
            },
            'bancario': {
                'nome': 'Direito Bancário',
                'icone': 'fas fa-university',
                'cor': '#007bff',
                'rota': '/juridico/bancario',
                'templates_especificos': ['contrato_financiamento', 'acao_revisional']
            },
            'empresarial': {
                'nome': 'Direito Empresarial',
                'icone': 'fas fa-building',
                'cor': '#6f42c1',
                'rota': '/juridico/empresarial',
                'templates_especificos': ['contrato_social', 'acordo_acionistas']
            },
            'recuperacao': {
                'nome': 'Recuperação Judicial',
                'icone': 'fas fa-chart-line',
                'cor': '#fd7e14',
                'rota': '/juridico/recuperacao',
                'templates_especificos': ['peticao_recuperacao', 'plano_recuperacao']
            },
            'trabalhista': {
                'nome': 'Direito Trabalhista',
                'icone': 'fas fa-hard-hat',
                'cor': '#20c997',
                'rota': '/juridico/trabalhista',
                'templates_especificos': ['reclamatoria_trabalhista', 'contrato_trabalho']
            },
            'consumidor': {
                'nome': 'Direito do Consumidor',
                'icone': 'fas fa-shopping-cart',
                'cor': '#e83e8c',
                'rota': '/juridico/consumidor',
                'templates_especificos': ['acao_consumidor', 'reclamacao_procon']
            }
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializa o gerenciador com a aplicação Flask"""
        self.app = app
        self._registrar_blueprints()
        self._inicializar_assistentes()
    
    def _registrar_blueprints(self):
        """Registra os blueprints para cada módulo jurídico"""
        for area, config in self.configuracao_modulos.items():
            blueprint = self._criar_blueprint_modulo(area, config)
            self.app.register_blueprint(blueprint, url_prefix=f'/juridico/{area}')
            logger.info(f"✅ Módulo {config['nome']} registrado em {config['rota']}")
    
    def _criar_blueprint_modulo(self, area: str, config: Dict) -> Blueprint:
        """Cria blueprint para um módulo jurídico específico"""
        bp = Blueprint(f'modulo_{area}', __name__)
        
        @bp.route('/')
        def index():
            """Página principal do módulo"""
            assistente = self.obter_assistente(area)
            templates_area = assistente.obter_templates_area()
            
            return render_template('modulos/modulo_especializado.html',
                                 area=area,
                                 config=config,
                                 assistente=assistente,
                                 templates=templates_area,
                                 provedores_ia=self._obter_provedores_disponiveis())
        
        @bp.route('/chat', methods=['POST'])
        def processar_chat():
            """Processa consultas do chat especializado"""
            try:
                dados = request.get_json()
                mensagem = dados.get('mensagem', '')
                contexto = dados.get('contexto', {})
                provider = dados.get('provider', 'openai')
                modelo = dados.get('modelo', 'gpt-4o')
                
                # Adicionar configurações de IA ao contexto
                contexto.update({
                    'provider': provider,
                    'modelo': modelo,
                    'area_juridica': area
                })
                
                assistente = self.obter_assistente(area)
                resultado = assistente.processar_consulta(mensagem, contexto)
                
                return jsonify(resultado)
                
            except Exception as e:
                logger.error(f"Erro no chat {area}: {e}")
                return jsonify({
                    'sucesso': False,
                    'erro': f'Erro interno: {str(e)}'
                }), 500
        
        @bp.route('/gerar-documento', methods=['POST'])
        def gerar_documento():
            """Gera documento baseado em template"""
            try:
                dados = request.get_json()
                template_id = dados.get('template_id')
                campos = dados.get('campos', {})
                
                assistente = self.obter_assistente(area)
                resultado = assistente.gerar_documento(template_id, campos)
                
                return jsonify(resultado)
                
            except Exception as e:
                logger.error(f"Erro na geração de documento {area}: {e}")
                return jsonify({
                    'sucesso': False,
                    'erro': f'Erro na geração: {str(e)}'
                }), 500
        
        @bp.route('/templates')
        def listar_templates():
            """Lista templates específicos da área"""
            assistente = self.obter_assistente(area)
            templates = assistente.obter_templates_area()
            return jsonify(templates)
        
        @bp.route('/upload', methods=['POST'])
        def upload_arquivo():
            """Upload e análise de arquivos jurídicos"""
            try:
                if 'arquivo' not in request.files:
                    return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400
                
                arquivo = request.files['arquivo']
                if arquivo.filename == '':
                    return jsonify({'sucesso': False, 'erro': 'Nome de arquivo inválido'}), 400
                
                # Processar arquivo (PDF, DOCX, etc.)
                resultado = self._processar_upload_arquivo(arquivo, area)
                return jsonify(resultado)
                
            except Exception as e:
                logger.error(f"Erro no upload {area}: {e}")
                return jsonify({
                    'sucesso': False,
                    'erro': f'Erro no upload: {str(e)}'
                }), 500
        
        return bp
    
    def _inicializar_assistentes(self):
        """Inicializa todos os assistentes especializados"""
        for area in self.configuracao_modulos.keys():
            try:
                assistente = obter_assistente(area)
                self.assistentes_cache[area] = assistente
                self.modulos_ativos[area] = True
                logger.info(f"✅ Assistente {assistente.nome} inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar assistente {area}: {e}")
                self.modulos_ativos[area] = False
    
    def obter_assistente(self, area: str):
        """Obtém assistente especializado para a área"""
        if area not in self.assistentes_cache:
            assistente = obter_assistente(area)
            self.assistentes_cache[area] = assistente
        return self.assistentes_cache[area]
    
    def _obter_provedores_disponiveis(self) -> List[Dict]:
        """Retorna lista de provedores de IA disponíveis"""
        provedores = []
        
        if os.getenv('OPENAI_API_KEY'):
            provedores.append({
                'id': 'openai',
                'nome': 'OpenAI (GPT)',
                'icone': '🤖',
                'modelos': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
            })
        
        if os.getenv('ANTHROPIC_API_KEY'):
            provedores.append({
                'id': 'anthropic',
                'nome': 'Anthropic (Claude)',
                'icone': '🧠',
                'modelos': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229']
            })
        
        if os.getenv('GOOGLE_API_KEY_APP'):
            provedores.append({
                'id': 'google',
                'nome': 'Google (Gemini)',
                'icone': '🌟',
                'modelos': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
            })
        
        return provedores
    
    def _processar_upload_arquivo(self, arquivo, area: str) -> Dict[str, Any]:
        """Processa arquivo enviado para análise"""
        try:
            # Salvar arquivo temporariamente
            nome_arquivo = arquivo.filename
            extensao = nome_arquivo.split('.')[-1].lower()
            
            if extensao not in ['pdf', 'docx', 'txt']:
                return {
                    'sucesso': False,
                    'erro': 'Tipo de arquivo não suportado. Use PDF, DOCX ou TXT.'
                }
            
            # Extrair texto do arquivo
            texto_extraido = self._extrair_texto_arquivo(arquivo, extensao)
            
            # Analisar com assistente especializado
            assistente = self.obter_assistente(area)
            contexto = {
                'tipo_analise': 'upload_arquivo',
                'nome_arquivo': nome_arquivo,
                'extensao': extensao
            }
            
            resultado_analise = assistente.processar_consulta(
                f"Analise o seguinte documento jurídico:\n\n{texto_extraido[:2000]}...",
                contexto
            )
            
            return {
                'sucesso': True,
                'arquivo': nome_arquivo,
                'texto_extraido': texto_extraido[:500] + "..." if len(texto_extraido) > 500 else texto_extraido,
                'analise': resultado_analise.get('resposta', 'Análise não disponível'),
                'area': area
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro no processamento: {str(e)}'
            }
    
    def _extrair_texto_arquivo(self, arquivo, extensao: str) -> str:
        """Extrai texto de diferentes tipos de arquivo"""
        try:
            if extensao == 'txt':
                return arquivo.read().decode('utf-8')
            elif extensao == 'pdf':
                # Implementar extração de PDF
                return "Extração de PDF não implementada ainda."
            elif extensao == 'docx':
                # Implementar extração de DOCX
                return "Extração de DOCX não implementada ainda."
            else:
                return "Tipo de arquivo não suportado."
        except Exception as e:
            logger.error(f"Erro na extração de texto: {e}")
            return f"Erro na extração: {str(e)}"
    
    def obter_status_modulos(self) -> Dict[str, Any]:
        """Retorna status de todos os módulos"""
        status = {}
        for area, config in self.configuracao_modulos.items():
            assistente = self.assistentes_cache.get(area)
            status[area] = {
                'nome': config['nome'],
                'ativo': self.modulos_ativos.get(area, False),
                'assistente_carregado': assistente is not None,
                'templates_disponiveis': len(assistente.obter_templates_area()) if assistente else 0,
                'rota': config['rota']
            }
        return status
    
    def obter_configuracao_completa(self) -> Dict[str, Any]:
        """Retorna configuração completa do sistema"""
        return {
            'modulos': self.configuracao_modulos,
            'status': self.obter_status_modulos(),
            'provedores_ia': self._obter_provedores_disponiveis(),
            'total_assistentes': len(ASSISTENTES_JURIDICOS),
            'timestamp': datetime.now().isoformat()
        }