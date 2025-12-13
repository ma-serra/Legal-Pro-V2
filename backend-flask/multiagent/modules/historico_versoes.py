"""
Módulo para gerenciamento de histórico de versões de documentos.
"""
import os
import json
import hashlib
import datetime
import logging
import difflib
from typing import Dict, List, Any, Optional, Tuple, Union

from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from main import db
from models import Documento, VersaoDocumento, AnaliseDocumento

# Configuração de logging
logger = logging.getLogger(__name__)

class GerenciadorVersoes:
    """
    Classe para gerenciar versões de documentos.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o gerenciador de versões.
        
        Args:
            config: Dicionário de configuração opcional
        """
        self.config = config or {}
        self.logger = logger
    
    def criar_documento(self, titulo: str, conteudo: str, usuario_id: int, 
                      tipo: Optional[str] = None, tags: Optional[str] = None,
                      descricao: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria um novo documento com sua primeira versão.
        
        Args:
            titulo: Título do documento
            conteudo: Conteúdo do documento
            usuario_id: ID do usuário que está criando o documento
            tipo: Tipo do documento (opcional)
            tags: Tags para o documento, separadas por vírgula (opcional)
            descricao: Descrição do documento (opcional)
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Gera o hash do conteúdo
            hash_conteudo = self._gerar_hash(conteudo)
            
            # Cria o documento
            documento = Documento(
                titulo=titulo,
                descricao=descricao,
                tipo=tipo,
                usuario_id=usuario_id,
                tags=tags,
                hash_conteudo=hash_conteudo
            )
            
            db.session.add(documento)
            db.session.flush()  # Para obter o ID do documento
            
            # Cria a primeira versão
            versao = VersaoDocumento(
                documento_id=documento.id,
                numero_versao=1,  # Primeira versão
                conteudo=conteudo,
                conteudo_html=self._formatar_html(conteudo),
                comentario="Versão inicial",
                usuario_id=usuario_id,
                hash_conteudo=hash_conteudo
            )
            
            db.session.add(versao)
            db.session.commit()
            
            return {
                "success": True,
                "documento": {
                    "id": documento.id,
                    "titulo": documento.titulo,
                    "versao_atual": 1,
                    "mensagem": "Documento criado com sucesso"
                }
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro de banco de dados ao criar documento: {str(e)}")
            return {"success": False, "error": f"Erro de banco de dados: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro ao criar documento: {str(e)}")
            return {"success": False, "error": f"Erro ao criar documento: {str(e)}"}
    
    def adicionar_versao(self, documento_id: int, conteudo: str, usuario_id: int,
                      comentario: Optional[str] = None) -> Dict[str, Any]:
        """
        Adiciona uma nova versão a um documento existente.
        
        Args:
            documento_id: ID do documento
            conteudo: Novo conteúdo do documento
            usuario_id: ID do usuário que está adicionando a versão
            comentario: Comentário sobre a nova versão (opcional)
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Verifica se o documento existe
            documento = Documento.query.get(documento_id)
            if not documento:
                return {"success": False, "error": "Documento não encontrado"}
            
            # Gera o hash do conteúdo
            hash_conteudo = self._gerar_hash(conteudo)
            
            # Verifica se o conteúdo é diferente da última versão
            ultima_versao = documento.versao_atual()
            if ultima_versao and ultima_versao.hash_conteudo == hash_conteudo:
                return {
                    "success": False, 
                    "error": "O conteúdo é idêntico à versão atual. Nenhuma alteração foi feita."
                }
            
            # Obtém o número da próxima versão
            proximo_numero = (ultima_versao.numero_versao + 1) if ultima_versao else 1
            
            # Cria a nova versão
            versao = VersaoDocumento(
                documento_id=documento_id,
                numero_versao=proximo_numero,
                conteudo=conteudo,
                conteudo_html=self._formatar_html(conteudo),
                comentario=comentario or f"Versão {proximo_numero}",
                usuario_id=usuario_id,
                hash_conteudo=hash_conteudo
            )
            
            # Atualiza o documento
            documento.hash_conteudo = hash_conteudo
            documento.data_atualizacao = datetime.datetime.now()
            
            db.session.add(versao)
            db.session.commit()
            
            return {
                "success": True,
                "versao": {
                    "id": versao.id,
                    "numero": versao.numero_versao,
                    "mensagem": f"Versão {versao.numero_versao} adicionada com sucesso"
                }
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro de banco de dados ao adicionar versão: {str(e)}")
            return {"success": False, "error": f"Erro de banco de dados: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro ao adicionar versão: {str(e)}")
            return {"success": False, "error": f"Erro ao adicionar versão: {str(e)}"}
    
    def obter_versao(self, documento_id: int, numero_versao: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtém uma versão específica de um documento.
        
        Args:
            documento_id: ID do documento
            numero_versao: Número da versão (opcional). Se não fornecido, retorna a versão mais recente.
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Verifica se o documento existe
            documento = Documento.query.get(documento_id)
            if not documento:
                return {"success": False, "error": "Documento não encontrado"}
            
            # Obtém a versão solicitada
            if numero_versao:
                versao = VersaoDocumento.query.filter_by(
                    documento_id=documento_id, 
                    numero_versao=numero_versao
                ).first()
                
                if not versao:
                    return {
                        "success": False, 
                        "error": f"Versão {numero_versao} não encontrada para o documento"
                    }
            else:
                # Obtém a versão mais recente
                versao = documento.versao_atual()
                if not versao:
                    return {
                        "success": False, 
                        "error": "Documento não possui versões"
                    }
            
            return {
                "success": True,
                "versao": {
                    "id": versao.id,
                    "numero": versao.numero_versao,
                    "conteudo": versao.conteudo,
                    "conteudo_html": versao.conteudo_html,
                    "comentario": versao.comentario,
                    "data_criacao": versao.data_criacao.strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario_id": versao.usuario_id
                },
                "documento": {
                    "id": documento.id,
                    "titulo": documento.titulo,
                    "tipo": documento.tipo,
                    "descricao": documento.descricao,
                    "total_versoes": documento.total_versoes()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter versão: {str(e)}")
            return {"success": False, "error": f"Erro ao obter versão: {str(e)}"}
    
    def listar_versoes(self, documento_id: int) -> Dict[str, Any]:
        """
        Lista todas as versões de um documento.
        
        Args:
            documento_id: ID do documento
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Verifica se o documento existe
            documento = Documento.query.get(documento_id)
            if not documento:
                return {"success": False, "error": "Documento não encontrado"}
            
            # Obtém todas as versões ordenadas por número
            versoes = VersaoDocumento.query.filter_by(documento_id=documento_id)\
                .order_by(VersaoDocumento.numero_versao.desc()).all()
            
            versoes_lista = []
            for versao in versoes:
                # Obtém análises relacionadas a esta versão
                analises = AnaliseDocumento.query.filter_by(versao_id=versao.id).count()
                
                versoes_lista.append({
                    "id": versao.id,
                    "numero": versao.numero_versao,
                    "comentario": versao.comentario,
                    "data_criacao": versao.data_criacao.strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario_id": versao.usuario_id,
                    "tamanho": len(versao.conteudo),
                    "possui_analises": analises > 0,
                    "total_analises": analises
                })
            
            return {
                "success": True,
                "documento": {
                    "id": documento.id,
                    "titulo": documento.titulo,
                    "tipo": documento.tipo,
                    "descricao": documento.descricao,
                    "total_versoes": len(versoes)
                },
                "versoes": versoes_lista
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar versões: {str(e)}")
            return {"success": False, "error": f"Erro ao listar versões: {str(e)}"}
    
    def comparar_versoes(self, documento_id: int, versao1: int, versao2: int) -> Dict[str, Any]:
        """
        Compara duas versões de um documento e gera um diff.
        
        Args:
            documento_id: ID do documento
            versao1: Número da primeira versão
            versao2: Número da segunda versão
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Verifica se o documento existe
            documento = Documento.query.get(documento_id)
            if not documento:
                return {"success": False, "error": "Documento não encontrado"}
            
            # Obtém as versões solicitadas
            v1 = VersaoDocumento.query.filter_by(
                documento_id=documento_id, 
                numero_versao=versao1
            ).first()
            
            v2 = VersaoDocumento.query.filter_by(
                documento_id=documento_id, 
                numero_versao=versao2
            ).first()
            
            if not v1 or not v2:
                return {
                    "success": False, 
                    "error": "Uma ou ambas as versões não foram encontradas"
                }
            
            # Gera o diff entre as versões
            diff_texto = self._gerar_diff(v1.conteudo, v2.conteudo)
            diff_html = self._gerar_diff_html(v1.conteudo, v2.conteudo)
            
            # Calcula estatísticas de alteração
            estatisticas = self._calcular_estatisticas_diff(v1.conteudo, v2.conteudo)
            
            return {
                "success": True,
                "documento": {
                    "id": documento.id,
                    "titulo": documento.titulo
                },
                "versao1": {
                    "id": v1.id,
                    "numero": v1.numero_versao,
                    "data": v1.data_criacao.strftime("%d/%m/%Y %H:%M:%S")
                },
                "versao2": {
                    "id": v2.id,
                    "numero": v2.numero_versao,
                    "data": v2.data_criacao.strftime("%d/%m/%Y %H:%M:%S")
                },
                "diff": diff_texto,
                "diff_html": diff_html,
                "estatisticas": estatisticas
            }
            
        except Exception as e:
            logger.error(f"Erro ao comparar versões: {str(e)}")
            return {"success": False, "error": f"Erro ao comparar versões: {str(e)}"}
    
    def _gerar_hash(self, conteudo: str) -> str:
        """
        Gera um hash SHA-256 para o conteúdo.
        
        Args:
            conteudo: Conteúdo para gerar o hash
            
        Returns:
            Hash SHA-256 do conteúdo
        """
        return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()
    
    def _formatar_html(self, conteudo: str) -> str:
        """
        Formata o conteúdo em HTML básico.
        
        Args:
            conteudo: Conteúdo para formatar
            
        Returns:
            Conteúdo formatado em HTML
        """
        # Implementação básica - pode ser expandida conforme necessário
        return conteudo.replace('\n', '<br>').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    
    def _gerar_diff(self, texto1: str, texto2: str) -> str:
        """
        Gera o diff entre dois textos.
        
        Args:
            texto1: Primeiro texto
            texto2: Segundo texto
            
        Returns:
            Diff formatado como texto
        """
        linhas1 = texto1.splitlines()
        linhas2 = texto2.splitlines()
        
        diff = difflib.unified_diff(linhas1, linhas2, lineterm='')
        return '\n'.join(diff)
    
    def _gerar_diff_html(self, texto1: str, texto2: str) -> str:
        """
        Gera o diff entre dois textos em formato HTML.
        
        Args:
            texto1: Primeiro texto
            texto2: Segundo texto
            
        Returns:
            Diff formatado como HTML
        """
        linhas1 = texto1.splitlines()
        linhas2 = texto2.splitlines()
        
        diff = difflib.HtmlDiff()
        return diff.make_file(linhas1, linhas2, 'Versão Antiga', 'Versão Nova')
    
    def _calcular_estatisticas_diff(self, texto1: str, texto2: str) -> Dict[str, Any]:
        """
        Calcula estatísticas sobre as diferenças entre dois textos.
        
        Args:
            texto1: Primeiro texto
            texto2: Segundo texto
            
        Returns:
            Dicionário com estatísticas das diferenças
        """
        linhas1 = texto1.splitlines()
        linhas2 = texto2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, texto1, texto2)
        similarity_ratio = matcher.ratio()
        
        # Conta adições e remoções
        diff = list(difflib.unified_diff(linhas1, linhas2, lineterm=''))
        adicoes = len([l for l in diff if l.startswith('+')])
        remocoes = len([l for l in diff if l.startswith('-')])
        
        # Conta palavras adicionadas e removidas
        palavras_antigas = len(texto1.split())
        palavras_novas = len(texto2.split())
        palavras_diff = palavras_novas - palavras_antigas
        
        return {
            "similaridade": round(similarity_ratio * 100, 2),
            "linhas_adicionadas": adicoes - 1 if adicoes > 0 else 0,  # -1 para ajustar o cabeçalho do diff
            "linhas_removidas": remocoes - 1 if remocoes > 0 else 0,  # -1 para ajustar o cabeçalho do diff
            "palavras_antigas": palavras_antigas,
            "palavras_novas": palavras_novas,
            "palavras_diferenca": palavras_diff
        }


# Funções auxiliares para uso fácil
def criar_documento(titulo: str, conteudo: str, usuario_id: int, 
                  tipo: Optional[str] = None, tags: Optional[str] = None,
                  descricao: Optional[str] = None) -> Dict[str, Any]:
    """
    Função auxiliar para criar um novo documento.
    
    Args:
        titulo: Título do documento
        conteudo: Conteúdo do documento
        usuario_id: ID do usuário que está criando o documento
        tipo: Tipo do documento (opcional)
        tags: Tags para o documento, separadas por vírgula (opcional)
        descricao: Descrição do documento (opcional)
        
    Returns:
        Dicionário com o resultado da operação
    """
    gerenciador = GerenciadorVersoes()
    return gerenciador.criar_documento(titulo, conteudo, usuario_id, tipo, tags, descricao)


def adicionar_versao(documento_id: int, conteudo: str, usuario_id: int,
                    comentario: Optional[str] = None) -> Dict[str, Any]:
    """
    Função auxiliar para adicionar uma nova versão a um documento.
    
    Args:
        documento_id: ID do documento
        conteudo: Novo conteúdo do documento
        usuario_id: ID do usuário que está adicionando a versão
        comentario: Comentário sobre a nova versão (opcional)
        
    Returns:
        Dicionário com o resultado da operação
    """
    gerenciador = GerenciadorVersoes()
    return gerenciador.adicionar_versao(documento_id, conteudo, usuario_id, comentario)


def listar_documentos(usuario_id: Optional[int] = None, 
                     tipo: Optional[str] = None, 
                     tags: Optional[List[str]] = None, 
                     busca: Optional[str] = None,
                     limite: int = 50) -> List[Dict[str, Any]]:
    """
    Lista documentos com filtros opcionais.
    
    Args:
        usuario_id: Filtrar por ID do usuário (opcional)
        tipo: Filtrar por tipo de documento (opcional)
        tags: Filtrar por tags (opcional)
        busca: Texto para busca no título ou descrição (opcional)
        limite: Limite de documentos a retornar
        
    Returns:
        Lista de documentos
    """
    try:
        query = Documento.query
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        if busca:
            query = query.filter(
                (Documento.titulo.ilike(f'%{busca}%')) | 
                (Documento.descricao.ilike(f'%{busca}%'))
            )
        
        if tags:
            # Filtra por qualquer uma das tags
            for tag in tags:
                query = query.filter(Documento.tags.ilike(f'%{tag}%'))
        
        # Ordena por data de atualização mais recente
        query = query.order_by(Documento.data_atualizacao.desc())
        
        # Limita o número de resultados
        query = query.limit(limite)
        
        documentos = query.all()
        
        resultados = []
        for doc in documentos:
            versao_atual = doc.versao_atual()
            
            resultados.append({
                "id": doc.id,
                "titulo": doc.titulo,
                "tipo": doc.tipo,
                "tags": doc.tags.split(',') if doc.tags else [],
                "descricao": doc.descricao,
                "usuario_id": doc.usuario_id,
                "data_criacao": doc.data_criacao.strftime("%d/%m/%Y %H:%M:%S"),
                "data_atualizacao": doc.data_atualizacao.strftime("%d/%m/%Y %H:%M:%S"),
                "versao_atual": versao_atual.numero_versao if versao_atual else None,
                "total_versoes": doc.total_versoes(),
            })
        
        return resultados
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {str(e)}")
        return []