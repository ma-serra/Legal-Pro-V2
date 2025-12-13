"""
Assistente Jurídico Universal
Sistema completo para todos os módulos jurídicos especializados
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistenteJuridicoUniversal:
    """
    Assistente jurídico universal que funciona com todos os módulos.
    Centraliza toda a lógica de processamento de consultas jurídicas.
    """
    
    def __init__(self):
        """Inicializa o assistente universal."""
        self.modulos_ativos = {
            'criminal': 'Direito Penal',
            'empresarial': 'Direito Empresarial', 
            'bancario': 'Direito Bancário e Financeiro',
            'recuperacao': 'Recuperação de Crédito',
            'agrario': 'Direito Agrário',
            'trabalhista': 'Direito Trabalhista',
            'consumidor': 'Direito do Consumidor'
        }
        
        self.provedores_ia = {
            'openai': self._setup_openai,
            'anthropic': self._setup_anthropic,
            'perplexity': self._setup_perplexity,
            'google': self._setup_google
        }
        
        self.personalidades = {
            'advogado': 'Advogado experiente e técnico',
            'juiz': 'Magistrado imparcial e fundamentado',
            'promotor': 'Promotor rigoroso e sistemático',
            'academico': 'Professor acadêmico didático',
            'consultor': 'Consultor estratégico e prático',
            'mediador': 'Mediador equilibrado e conciliador'
        }
        
        self.tons_voz = {
            'sistematico': 'Análise sistemática e organizada',
            'persuasivo': 'Argumentação persuasiva e convincente',
            'didatico': 'Explicação didática e educativa',
            'tecnico': 'Linguagem técnica e precisa',
            'acessivel': 'Linguagem acessível e clara',
            'formal': 'Linguagem formal e protocolar'
        }
        
    def processar_consulta(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma consulta jurídica completa.
        
        Args:
            dados: Dicionário com os dados da consulta
            
        Returns:
            Dicionário com a resposta processada
        """
        try:
            # Extrair dados da consulta
            mensagem = dados.get('message', '').strip()
            modulo = dados.get('modulo', 'geral')
            provedor = dados.get('provider', 'openai')
            personalidade = dados.get('personalidade', 'advogado')
            tom = dados.get('tom', 'sistematico')
            arquivos = dados.get('files', [])
            
            # Validar dados mínimos
            if not mensagem and not arquivos:
                return {
                    'sucesso': False,
                    'erro': 'Mensagem ou arquivos são obrigatórios',
                    'response': 'Por favor, forneça uma consulta ou envie arquivos para análise.'
                }
            
            # Processar arquivos se enviados
            conteudo_arquivos = []
            if arquivos:
                conteudo_arquivos = self._processar_arquivos(arquivos)
            
            # Construir prompt especializado
            prompt_sistema = self._construir_prompt_sistema(modulo, personalidade, tom)
            prompt_usuario = self._construir_prompt_usuario(mensagem, conteudo_arquivos, modulo)
            
            # Processar através do provedor de IA
            resposta = self._processar_com_ia(provedor, prompt_sistema, prompt_usuario)
            
            # Log da operação
            logger.info(f"Consulta processada - Módulo: {modulo}, Provedor: {provedor}")
            
            return {
                'sucesso': True,
                'response': resposta,
                'modulo': modulo,
                'provedor': provedor,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
            return {
                'sucesso': False,
                'erro': str(e),
                'response': f'Erro ao processar sua consulta: {str(e)}. Verifique se as chaves de API estão configuradas.'
            }
    
    def _construir_prompt_sistema(self, modulo: str, personalidade: str, tom: str) -> str:
        """Constrói o prompt do sistema baseado no módulo e configurações."""
        
        area_especializada = self.modulos_ativos.get(modulo, 'Direito Geral')
        perfil_personalidade = self.personalidades.get(personalidade, 'Advogado experiente')
        estilo_tom = self.tons_voz.get(tom, 'Análise sistemática')
        
        prompt = f"""Você é um especialista em {area_especializada} com vasta experiência advocatícia. Está em reunião com colegas advogados discutindo estratégias jurídicas.

PERFIL: {perfil_personalidade} - {estilo_tom}

Responda com rigor técnico apropriado para profissionais do direito, utilizando:
- Terminologia jurídica precisa e atual
- Citação de dispositivos legais específicos
- Referências jurisprudenciais pertinentes
- Análise doutrinária quando relevante
- Considerações práticas processuais

Mantenha tom conversacional mas técnico, como em discussão entre pares especializados. Seja direto, fundamentado e ofereça insights práticos baseados na experiência advocatícia em {area_especializada}."""

        return prompt
    
    def _construir_prompt_usuario(self, mensagem: str, arquivos: List[str], modulo: str) -> str:
        """Constrói o prompt do usuário com contexto dos arquivos."""
        
        prompt = f"CONSULTA JURÍDICA - {self.modulos_ativos.get(modulo, 'Geral')}:\n\n"
        
        if mensagem:
            prompt += f"PERGUNTA: {mensagem}\n\n"
        
        if arquivos:
            prompt += "DOCUMENTOS ANEXADOS:\n"
            for i, conteudo in enumerate(arquivos, 1):
                prompt += f"\n--- DOCUMENTO {i} ---\n{conteudo}\n"
            prompt += "\nPor favor, analise os documentos anexados em conjunto com a consulta.\n\n"
        
        prompt += "Aguardo sua análise jurídica fundamentada."
        
        return prompt
    
    def _processar_arquivos(self, arquivos: List) -> List[str]:
        """Processa arquivos enviados e extrai o conteúdo."""
        conteudos = []
        
        for arquivo in arquivos:
            try:
                if hasattr(arquivo, 'read'):
                    # É um objeto de arquivo
                    conteudo = arquivo.read()
                    if isinstance(conteudo, bytes):
                        conteudo = conteudo.decode('utf-8', errors='ignore')
                    conteudos.append(conteudo[:5000])  # Limitar tamanho
                else:
                    # É um caminho de arquivo
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()[:5000]
                        conteudos.append(conteudo)
                        
            except Exception as e:
                logger.warning(f"Erro ao processar arquivo: {e}")
                conteudos.append(f"[Erro ao processar arquivo: {str(e)}]")
        
        return conteudos
    
    def _processar_com_ia(self, provedor: str, prompt_sistema: str, prompt_usuario: str) -> str:
        """Processa a consulta com o provedor de IA selecionado."""
        
        processador = self.provedores_ia.get(provedor)
        if not processador:
            raise ValueError(f"Provedor {provedor} não suportado")
        
        return processador(prompt_sistema, prompt_usuario)
    
    def _setup_openai(self, prompt_sistema: str, prompt_usuario: str) -> str:
        """Processa consulta com OpenAI."""
        try:
            import openai
            
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("Chave da API OpenAI não configurada")
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Modelo mais recente
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Erro na API OpenAI: {str(e)}")
    
    def _setup_anthropic(self, prompt_sistema: str, prompt_usuario: str) -> str:
        """Processa consulta com Anthropic."""
        try:
            import anthropic
            
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("Chave da API Anthropic não configurada")
            
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Modelo mais recente
                system=prompt_sistema,
                messages=[
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Corrigir acesso ao conteúdo
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            else:
                return str(response.content[0])
            
        except Exception as e:
            raise Exception(f"Erro na API Anthropic: {str(e)}")
    
    def _setup_perplexity(self, prompt_sistema: str, prompt_usuario: str) -> str:
        """Processa consulta com Perplexity."""
        try:
            import requests
            
            api_key = os.environ.get('PERPLEXITY_API_KEY')
            if not api_key:
                raise ValueError("Chave da API Perplexity não configurada")
            
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            raise Exception(f"Erro na API Perplexity: {str(e)}")
    
    def _setup_google(self, prompt_sistema: str, prompt_usuario: str) -> str:
        """Processa consulta com Google Gemini."""
        try:
            # Tentar importar a biblioteca do Google
            try:
                import google.generativeai as genai
            except ImportError:
                raise ValueError("Biblioteca google-generativeai não está instalada")
            
            api_key = os.environ.get('GOOGLE_API_KEY_APP')
            if not api_key:
                raise ValueError("Chave da API Google não configurada")
            
            # Configurar a API
            if hasattr(genai, 'configure'):
                genai.configure(api_key=api_key)
            else:
                raise ValueError("Método configure não disponível na biblioteca")
            
            # Criar modelo
            if hasattr(genai, 'GenerativeModel'):
                model = genai.GenerativeModel('gemini-pro')
            else:
                raise ValueError("GenerativeModel não disponível na biblioteca")
            
            prompt_completo = f"{prompt_sistema}\n\n{prompt_usuario}"
            
            response = model.generate_content(prompt_completo)
            
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
            
        except Exception as e:
            raise Exception(f"Erro na API Google: {str(e)}")
    
    def obter_configuracoes_modulo(self, modulo: str) -> Dict[str, Any]:
        """Retorna as configurações específicas de um módulo."""
        
        configuracoes_base = {
            'criminal': {
                'nome': 'Direito Penal',
                'icone': 'fas fa-gavel',
                'cores': {'primaria': '#dc3545', 'secundaria': '#c82333'},
                'descricao': 'Crimes, processo penal e defesa criminal',
                'especialidades': ['Crimes contra a pessoa', 'Crimes patrimoniais', 'Processo penal', 'Execução penal']
            },
            'empresarial': {
                'nome': 'Direito Empresarial',
                'icone': 'fas fa-building',
                'cores': {'primaria': '#6f42c1', 'secundaria': '#5a32a3'},
                'descricao': 'Contratos empresariais, sociedades e direito societário',
                'especialidades': ['Contratos empresariais', 'Direito societário', 'Fusões e aquisições', 'Compliance']
            },
            'bancario': {
                'nome': 'Direito Bancário e Financeiro',
                'icone': 'fas fa-university',
                'cores': {'primaria': '#17a2b8', 'secundaria': '#138496'},
                'descricao': 'Consultivo e contencioso bancário, regulatório',
                'especialidades': ['Operações bancárias', 'Regulação financeira', 'Contratos bancários', 'Mercado de capitais']
            },
            'recuperacao': {
                'nome': 'Recuperação de Crédito',
                'icone': 'fas fa-search-dollar',
                'cores': {'primaria': '#fd7e14', 'secundaria': '#e56b00'},
                'descricao': 'Localização devedores, acordos, execuções',
                'especialidades': ['Execução judicial', 'Negociação de dívidas', 'Localização de bens', 'Acordos extrajudiciais']
            },
            'agrario': {
                'nome': 'Direito Agrário',
                'icone': 'fas fa-seedling',
                'cores': {'primaria': '#1f5981', 'secundaria': '#1e7e34'},
                'descricao': 'Reforma agrária, propriedade rural e contratos agrários',
                'especialidades': ['Reforma agrária', 'Propriedade rural', 'Contratos agrários', 'Questões fundiárias']
            },
            'trabalhista': {
                'nome': 'Direito Trabalhista',
                'icone': 'fas fa-hard-hat',
                'cores': {'primaria': '#ffc107', 'secundaria': '#e0a800'},
                'descricao': 'Relações de trabalho e processo trabalhista',
                'especialidades': ['Relações trabalhistas', 'Processo trabalhista', 'Direito sindical', 'Segurança do trabalho']
            },
            'consumidor': {
                'nome': 'Direito do Consumidor',
                'icone': 'fas fa-shopping-cart',
                'cores': {'primaria': '#6610f2', 'secundaria': '#520dc2'},
                'descricao': 'Proteção do consumidor e relações de consumo',
                'especialidades': ['Defesa do consumidor', 'Relações de consumo', 'Publicidade', 'Contratos de consumo']
            }
        }
        
        return configuracoes_base.get(modulo, configuracoes_base['criminal'])
    
    def listar_modulos_disponiveis(self) -> List[Dict[str, Any]]:
        """Lista todos os módulos jurídicos disponíveis."""
        modulos = []
        
        for modulo_id, nome in self.modulos_ativos.items():
            config = self.obter_configuracoes_modulo(modulo_id)
            modulos.append({
                'id': modulo_id,
                'nome': nome,
                'config': config,
                'ativo': True
            })
        
        return modulos

# Instância global do assistente
assistente_universal = AssistenteJuridicoUniversal()