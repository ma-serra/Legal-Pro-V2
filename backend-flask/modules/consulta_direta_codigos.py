"""
Módulo para consulta direta aos arquivos dos códigos penais
Permite busca e validação jurídica independente da vetorização
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ConsultaDiretaCodigos:
    """Sistema de consulta direta aos códigos penais em arquivo"""
    
    def __init__(self):
        self.codigo_penal_path = "attached_assets/Codigo_Penal_8ed_otimizado_numerado.md"
        self.codigo_cpp_path = "attached_assets/Codigo_Processo_Penal_7ed_otimizado_numerado.md"
        
        # Cache dos códigos carregados
        self._codigo_penal_cache = None
        self._codigo_cpp_cache = None
        
        # Padrões de validação jurídica
        self.padroes_validacao = {
            'artigo_valido': r'Art\.?\s*(\d+)(?:[°º]?[AB]?)?(?:[-\s]?[A-Z])?',
            'paragrafo_valido': r'§\s*(\d+)[°º]?',
            'inciso_valido': r'([IVX]+)\s*[-–]',
            'alinea_valida': r'([a-z])\)'
        }
    
    def carregar_codigo_penal(self) -> str:
        """Carrega o Código Penal do arquivo"""
        if self._codigo_penal_cache is None:
            try:
                with open(self.codigo_penal_path, 'r', encoding='utf-8') as f:
                    self._codigo_penal_cache = f.read()
                logger.info("Código Penal carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar Código Penal: {e}")
                self._codigo_penal_cache = ""
        return self._codigo_penal_cache
    
    def carregar_codigo_cpp(self) -> str:
        """Carrega o Código de Processo Penal do arquivo"""
        if self._codigo_cpp_cache is None:
            try:
                with open(self.codigo_cpp_path, 'r', encoding='utf-8') as f:
                    self._codigo_cpp_cache = f.read()
                logger.info("Código de Processo Penal carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar Código de Processo Penal: {e}")
                self._codigo_cpp_cache = ""
        return self._codigo_cpp_cache
    
    def buscar_artigo_especifico(self, numero_artigo: str, codigo: str = 'ambos') -> List[Dict[str, Any]]:
        """Busca artigo específico nos códigos"""
        resultados = []
        
        # Normaliza número do artigo
        numero_limpo = re.sub(r'[^\d]', '', numero_artigo)
        
        if codigo in ['cp', 'ambos']:
            cp_content = self.carregar_codigo_penal()
            artigo_cp = self._extrair_artigo_completo(cp_content, numero_limpo, 'Código Penal')
            if artigo_cp:
                resultados.append(artigo_cp)
        
        if codigo in ['cpp', 'ambos']:
            cpp_content = self.carregar_codigo_cpp()
            artigo_cpp = self._extrair_artigo_completo(cpp_content, numero_limpo, 'Código de Processo Penal')
            if artigo_cpp:
                resultados.append(artigo_cpp)
        
        return resultados
    
    def _extrair_artigo_completo(self, texto: str, numero: str, fonte: str) -> Optional[Dict[str, Any]]:
        """Extrai artigo completo com todos os parágrafos e incisos"""
        # Padrão para encontrar o artigo
        padrao_inicio = rf'Art\.?\s*{numero}[°º]?[.-]?\s*'
        
        # Encontra o início do artigo
        match_inicio = re.search(padrao_inicio, texto, re.IGNORECASE)
        if not match_inicio:
            return None
        
        start_pos = match_inicio.start()
        
        # Encontra o próximo artigo para delimitar
        padrao_proximo = r'Art\.?\s*\d+[°º]?[.-]?\s*'
        matches_proximos = list(re.finditer(padrao_proximo, texto[start_pos + len(match_inicio.group()):], re.IGNORECASE))
        
        if matches_proximos:
            end_pos = start_pos + len(match_inicio.group()) + matches_proximos[0].start()
            conteudo_artigo = texto[start_pos:end_pos].strip()
        else:
            # Se não encontrar próximo artigo, pega até o final da seção
            conteudo_artigo = texto[start_pos:start_pos + 3000].strip()
        
        # Extrai título se disponível
        titulo = self._extrair_titulo_artigo(conteudo_artigo)
        
        return {
            'artigo': numero,
            'fonte': fonte,
            'titulo': titulo,
            'conteudo_completo': conteudo_artigo,
            'validado': True,
            'tipo_busca': 'consulta_direta'
        }
    
    def _extrair_titulo_artigo(self, conteudo: str) -> str:
        """Extrai o título do artigo quando disponível"""
        linhas = conteudo.split('\n')
        primeira_linha = linhas[0] if linhas else ""
        
        # Busca por padrões de título após o número do artigo
        match = re.search(r'Art\.?\s*\d+[°º]?[.-]?\s*(.+?)[:.-]', primeira_linha)
        if match:
            titulo = match.group(1).strip()
            return titulo if len(titulo) < 100 else titulo[:100] + "..."
        
        return "Artigo"
    
    def buscar_por_termo(self, termo: str, codigo: str = 'ambos', limite: int = 10) -> List[Dict[str, Any]]:
        """Busca por termo específico nos códigos"""
        resultados = []
        
        if codigo in ['cp', 'ambos']:
            cp_content = self.carregar_codigo_penal()
            resultados_cp = self._buscar_termo_no_texto(cp_content, termo, 'Código Penal', limite//2)
            resultados.extend(resultados_cp)
        
        if codigo in ['cpp', 'ambos']:
            cpp_content = self.carregar_codigo_cpp()
            resultados_cpp = self._buscar_termo_no_texto(cpp_content, termo, 'Código de Processo Penal', limite//2)
            resultados.extend(resultados_cpp)
        
        return sorted(resultados, key=lambda x: x.get('relevancia', 0), reverse=True)[:limite]
    
    def _buscar_termo_no_texto(self, texto: str, termo: str, fonte: str, limite: int) -> List[Dict[str, Any]]:
        """Busca termo específico no texto do código"""
        resultados = []
        termo_lower = termo.lower()
        
        # Divide o texto em artigos
        artigos = re.split(r'(Art\.?\s*\d+[°º]?[.-]?\s*)', texto)
        
        for i in range(1, len(artigos), 2):  # Índices ímpares contêm os artigos
            if i + 1 < len(artigos):
                cabecalho = artigos[i]
                conteudo = artigos[i + 1]
                texto_completo = cabecalho + conteudo
                
                # Verifica se o termo está presente
                if termo_lower in texto_completo.lower():
                    # Extrai número do artigo
                    match_artigo = re.search(r'Art\.?\s*(\d+)', cabecalho)
                    numero_artigo = match_artigo.group(1) if match_artigo else "?"
                    
                    # Calcula relevância baseada na frequência
                    frequencia = texto_completo.lower().count(termo_lower)
                    relevancia = min(frequencia * 0.2, 1.0)
                    
                    # Extrai contexto ao redor do termo
                    contexto = self._extrair_contexto_termo(texto_completo, termo, 200)
                    
                    resultados.append({
                        'artigo': numero_artigo,
                        'fonte': fonte,
                        'titulo': self._extrair_titulo_artigo(cabecalho + conteudo[:100]),
                        'conteudo_completo': texto_completo.strip(),
                        'contexto_termo': contexto,
                        'relevancia': relevancia,
                        'frequencia_termo': frequencia,
                        'validado': True,
                        'tipo_busca': 'busca_termo'
                    })
        
        return sorted(resultados, key=lambda x: x['relevancia'], reverse=True)[:limite]
    
    def _extrair_contexto_termo(self, texto: str, termo: str, tamanho_contexto: int = 200) -> str:
        """Extrai contexto ao redor do termo encontrado"""
        texto_lower = texto.lower()
        termo_lower = termo.lower()
        
        pos = texto_lower.find(termo_lower)
        if pos == -1:
            return texto[:tamanho_contexto]
        
        inicio = max(0, pos - tamanho_contexto // 2)
        fim = min(len(texto), pos + len(termo) + tamanho_contexto // 2)
        
        contexto = texto[inicio:fim]
        
        # Adiciona indicadores se o contexto foi cortado
        if inicio > 0:
            contexto = "..." + contexto
        if fim < len(texto):
            contexto = contexto + "..."
        
        return contexto
    
    def validar_citacao_juridica(self, citacao: str) -> Dict[str, Any]:
        """Valida se uma citação jurídica está correta"""
        validacao = {
            'valida': False,
            'fonte_encontrada': None,
            'artigo_encontrado': None,
            'detalhes': {},
            'sugestoes_correcao': []
        }
        
        # Extrai componentes da citação
        componentes = self._extrair_componentes_citacao(citacao)
        
        if not componentes['artigo']:
            validacao['sugestoes_correcao'].append("Especifique o número do artigo")
            return validacao
        
        # Busca o artigo nos códigos
        artigos_encontrados = self.buscar_artigo_especifico(componentes['artigo'])
        
        if artigos_encontrados:
            validacao['valida'] = True
            validacao['fonte_encontrada'] = artigos_encontrados[0]['fonte']
            validacao['artigo_encontrado'] = artigos_encontrados[0]
            
            # Valida parágrafos e incisos se especificados
            if componentes['paragrafo']:
                validacao['detalhes']['paragrafo_valido'] = self._validar_paragrafo(
                    artigos_encontrados[0]['conteudo_completo'], 
                    componentes['paragrafo']
                )
            
            if componentes['inciso']:
                validacao['detalhes']['inciso_valido'] = self._validar_inciso(
                    artigos_encontrados[0]['conteudo_completo'], 
                    componentes['inciso']
                )
        else:
            validacao['sugestoes_correcao'].append(f"Artigo {componentes['artigo']} não encontrado")
        
        return validacao
    
    def _extrair_componentes_citacao(self, citacao: str) -> Dict[str, Optional[str]]:
        """Extrai componentes de uma citação jurídica"""
        componentes = {
            'artigo': None,
            'paragrafo': None,
            'inciso': None,
            'alinea': None
        }
        
        # Extrai artigo
        match_artigo = re.search(self.padroes_validacao['artigo_valido'], citacao)
        if match_artigo:
            componentes['artigo'] = match_artigo.group(1)
        
        # Extrai parágrafo
        match_paragrafo = re.search(self.padroes_validacao['paragrafo_valido'], citacao)
        if match_paragrafo:
            componentes['paragrafo'] = match_paragrafo.group(1)
        
        # Extrai inciso
        match_inciso = re.search(self.padroes_validacao['inciso_valido'], citacao)
        if match_inciso:
            componentes['inciso'] = match_inciso.group(1)
        
        # Extrai alínea
        match_alinea = re.search(self.padroes_validacao['alinea_valida'], citacao)
        if match_alinea:
            componentes['alinea'] = match_alinea.group(1)
        
        return componentes
    
    def _validar_paragrafo(self, conteudo: str, numero_paragrafo: str) -> bool:
        """Valida se o parágrafo existe no artigo"""
        padrao = rf'§\s*{numero_paragrafo}[°º]?'
        return bool(re.search(padrao, conteudo))
    
    def _validar_inciso(self, conteudo: str, inciso: str) -> bool:
        """Valida se o inciso existe no artigo"""
        padrao = rf'{inciso}\s*[-–]'
        return bool(re.search(padrao, conteudo))
    
    def gerar_fundamentacao_completa(self, consulta: str) -> Dict[str, Any]:
        """Gera fundamentação jurídica completa para uma consulta"""
        # Identifica artigos mencionados na consulta
        artigos_mencionados = re.findall(r'art\.?\s*(\d+)', consulta, re.IGNORECASE)
        
        # Identifica termos jurídicos importantes
        termos_importantes = self._extrair_termos_juridicos(consulta)
        
        fundamentacao = {
            'artigos_diretos': [],
            'artigos_relacionados': [],
            'termos_encontrados': [],
            'validacao_geral': True,
            'observacoes': []
        }
        
        # Busca artigos específicos mencionados
        for artigo in artigos_mencionados:
            artigos_encontrados = self.buscar_artigo_especifico(artigo)
            fundamentacao['artigos_diretos'].extend(artigos_encontrados)
        
        # Busca por termos importantes
        for termo in termos_importantes:
            resultados_termo = self.buscar_por_termo(termo, limite=3)
            fundamentacao['termos_encontrados'].extend(resultados_termo)
        
        # Remove duplicatas
        fundamentacao['artigos_diretos'] = self._remover_duplicatas_artigos(fundamentacao['artigos_diretos'])
        fundamentacao['termos_encontrados'] = self._remover_duplicatas_artigos(fundamentacao['termos_encontrados'])
        
        return fundamentacao
    
    def _extrair_termos_juridicos(self, texto: str) -> List[str]:
        """Extrai termos jurídicos importantes do texto"""
        termos_penais = [
            'homicídio', 'furto', 'roubo', 'lesão corporal', 'estupro',
            'prisão preventiva', 'liberdade provisória', 'medidas cautelares',
            'tribunal do júri', 'pronúncia', 'quesitos', 'recurso',
            'denúncia', 'queixa', 'flagrante', 'busca e apreensão'
        ]
        
        texto_lower = texto.lower()
        termos_encontrados = []
        
        for termo in termos_penais:
            if termo in texto_lower:
                termos_encontrados.append(termo)
        
        return termos_encontrados
    
    def _remover_duplicatas_artigos(self, artigos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove artigos duplicados da lista"""
        vistos = set()
        unicos = []
        
        for artigo in artigos:
            chave = f"{artigo['fonte']}_{artigo['artigo']}"
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(artigo)
        
        return unicos