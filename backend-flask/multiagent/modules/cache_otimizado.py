"""
Módulo de cache otimizado para reduzir chamadas de API e melhorar performance.
"""
import json
import logging
import datetime
import hashlib
import time
from typing import Dict, List, Any, Optional, Union, Callable

from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from main import db
from models import CacheRespostaAPI
from multiagent.utils.api_key_manager import get_api_key

# Configuração de logging
logger = logging.getLogger(__name__)

# Cache em memória para respostas frequentes
# Estrutura: {hash_prompt: {resposta, timestamp, contador_uso}}
CACHE_MEMORIA = {}
CACHE_MEMORIA_LIMITE = 1000  # Limite de itens no cache em memória
CACHE_MEMORIA_TTL = 60 * 60  # Tempo de vida em segundos (1 hora)

class GerenciadorCache:
    """
    Classe para gerenciar o cache de respostas de APIs.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            config: Dicionário de configuração opcional
        """
        self.config = config or {}
        self.logger = logger
        
        # Configura o nível de cache
        self.nivel_cache = self.config.get("nivel_cache", 2)  # 0=desabilitado, 1=memória, 2=memória+banco, 3=agressivo
        self.usar_cache_memoria = self.nivel_cache >= 1
        self.usar_cache_db = self.nivel_cache >= 2
        self.cache_agressivo = self.nivel_cache >= 3
        
        # Configura tempos de expiração
        self.tempo_expiracao_db = self.config.get("tempo_expiracao_db", 24 * 60 * 60)  # 24 horas
        self.tempo_expiracao_memoria = self.config.get("tempo_expiracao_memoria", CACHE_MEMORIA_TTL)
        
        # Se configurado, faz limpeza do cache expirado no banco de dados
        if self.config.get("limpar_cache_expirado_startup", False):
            self._limpar_cache_expirado()
    
    def obter_resposta_cache(self, provedor: str, modelo: str, 
                           prompt: str, parametros: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Tenta obter uma resposta do cache.
        
        Args:
            provedor: Nome do provedor (openai, anthropic, etc.)
            modelo: Nome do modelo (gpt-4, claude-3, etc.)
            prompt: O prompt enviado para a API
            parametros: Parâmetros adicionais da chamada (opcional)
            
        Returns:
            Resposta do cache ou None se não encontrada
        """
        if self.nivel_cache == 0:
            return None  # Cache desabilitado
            
        # Gera o hash do prompt
        hash_prompt = self._gerar_hash(prompt)
        
        # Tenta obter do cache em memória primeiro (mais rápido)
        if self.usar_cache_memoria:
            resposta_memoria = self._obter_cache_memoria(hash_prompt, provedor, modelo)
            if resposta_memoria:
                return resposta_memoria
        
        # Se não encontrou na memória, tenta no banco de dados
        if self.usar_cache_db:
            resposta_db = self._obter_cache_db(hash_prompt, provedor, modelo, parametros)
            
            # Se encontrou no banco, atualiza o cache em memória
            if resposta_db and self.usar_cache_memoria:
                self._atualizar_cache_memoria(hash_prompt, provedor, modelo, resposta_db)
                
            return resposta_db
            
        return None
    
    def armazenar_resposta_cache(self, provedor: str, modelo: str, prompt: str,
                              resposta: str, parametros: Optional[Dict[str, Any]] = None,
                              tempo_expiracao: Optional[int] = None) -> bool:
        """
        Armazena uma resposta no cache.
        
        Args:
            provedor: Nome do provedor (openai, anthropic, etc.)
            modelo: Nome do modelo (gpt-4, claude-3, etc.)
            prompt: O prompt enviado para a API
            resposta: A resposta recebida da API
            parametros: Parâmetros adicionais da chamada (opcional)
            tempo_expiracao: Tempo em segundos até a expiração (opcional)
            
        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        if self.nivel_cache == 0:
            return False  # Cache desabilitado
            
        # Gera o hash do prompt
        hash_prompt = self._gerar_hash(prompt)
        
        # Armazena no cache em memória
        if self.usar_cache_memoria:
            self._atualizar_cache_memoria(hash_prompt, provedor, modelo, resposta)
        
        # Armazena no banco de dados
        if self.usar_cache_db:
            return self._armazenar_cache_db(
                hash_prompt, provedor, modelo, prompt, resposta, parametros, tempo_expiracao
            )
            
        return True
    
    def limpar_cache_provedor(self, provedor: Optional[str] = None, 
                           modelo: Optional[str] = None) -> Dict[str, Any]:
        """
        Limpa o cache para um provedor e/ou modelo específico.
        
        Args:
            provedor: Nome do provedor (opcional)
            modelo: Nome do modelo (opcional)
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Limpa cache em memória
            if self.usar_cache_memoria:
                removidos_memoria = 0
                keys_para_remover = []
                
                for key, valor in CACHE_MEMORIA.items():
                    if (provedor is None or valor.get("provedor") == provedor) and \
                       (modelo is None or valor.get("modelo") == modelo):
                        keys_para_remover.append(key)
                
                for key in keys_para_remover:
                    CACHE_MEMORIA.pop(key, None)
                    removidos_memoria += 1
            else:
                removidos_memoria = 0
            
            # Limpa cache no banco de dados
            if self.usar_cache_db:
                query = CacheRespostaAPI.query
                
                if provedor:
                    query = query.filter_by(provedor=provedor)
                    
                if modelo:
                    query = query.filter_by(modelo=modelo)
                
                removidos_db = query.delete()
                db.session.commit()
            else:
                removidos_db = 0
            
            return {
                "success": True,
                "removidos_memoria": removidos_memoria,
                "removidos_banco": removidos_db,
                "provedor": provedor,
                "modelo": modelo
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro de banco de dados ao limpar cache: {str(e)}")
            return {"success": False, "error": f"Erro de banco de dados: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            return {"success": False, "error": f"Erro ao limpar cache: {str(e)}"}
    
    def estatisticas_cache(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o uso do cache.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Estatísticas do cache em memória
            if self.usar_cache_memoria:
                tamanho_memoria = len(CACHE_MEMORIA)
                usos_memoria = sum(item.get("contador_uso", 0) for item in CACHE_MEMORIA.values())
                
                # Maiores usuários do cache em memória
                top_memoria = []
                for hash_prompt, item in CACHE_MEMORIA.items():
                    top_memoria.append({
                        "provedor": item.get("provedor", ""),
                        "modelo": item.get("modelo", ""),
                        "contador_uso": item.get("contador_uso", 0),
                        "timestamp": item.get("timestamp", 0)
                    })
                
                # Ordena por contador de uso
                top_memoria.sort(key=lambda x: x["contador_uso"], reverse=True)
                top_memoria = top_memoria[:10]  # Top 10
            else:
                tamanho_memoria = 0
                usos_memoria = 0
                top_memoria = []
            
            # Estatísticas do cache no banco de dados
            if self.usar_cache_db:
                # Total de itens no cache
                total_db = CacheRespostaAPI.query.count()
                
                # Total de usos do cache
                total_usos_db = db.session.query(db.func.sum(CacheRespostaAPI.contador_uso)).scalar() or 0
                
                # Itens por provedor
                itens_por_provedor = {}
                for provedor, contagem in db.session.query(
                    CacheRespostaAPI.provedor, db.func.count(CacheRespostaAPI.id)
                ).group_by(CacheRespostaAPI.provedor).all():
                    itens_por_provedor[provedor] = contagem
                
                # Top 10 itens mais usados
                top_items_db = CacheRespostaAPI.query.order_by(
                    CacheRespostaAPI.contador_uso.desc()
                ).limit(10).all()
                
                top_db = []
                for item in top_items_db:
                    top_db.append({
                        "provedor": item.provedor,
                        "modelo": item.modelo,
                        "contador_uso": item.contador_uso,
                        "data_criacao": item.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
                    })
            else:
                total_db = 0
                total_usos_db = 0
                itens_por_provedor = {}
                top_db = []
            
            return {
                "success": True,
                "nivel_cache": self.nivel_cache,
                "memoria": {
                    "habilitado": self.usar_cache_memoria,
                    "tamanho": tamanho_memoria,
                    "total_usos": usos_memoria,
                    "limite": CACHE_MEMORIA_LIMITE,
                    "ttl": self.tempo_expiracao_memoria,
                    "top_items": top_memoria
                },
                "banco_dados": {
                    "habilitado": self.usar_cache_db,
                    "tamanho": total_db,
                    "total_usos": total_usos_db,
                    "por_provedor": itens_por_provedor,
                    "ttl": self.tempo_expiracao_db,
                    "top_items": top_db
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {str(e)}")
            return {"success": False, "error": f"Erro ao obter estatísticas: {str(e)}"}
    
    def _gerar_hash(self, prompt: str) -> str:
        """
        Gera um hash SHA-256 para o prompt.
        
        Args:
            prompt: Prompt para gerar o hash
            
        Returns:
            Hash SHA-256 do prompt
        """
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    
    def _obter_cache_memoria(self, hash_prompt: str, provedor: str, modelo: str) -> Optional[str]:
        """
        Obtém uma resposta do cache em memória.
        
        Args:
            hash_prompt: Hash do prompt
            provedor: Nome do provedor
            modelo: Nome do modelo
            
        Returns:
            Resposta do cache ou None
        """
        # Verifica se existe no cache
        if hash_prompt not in CACHE_MEMORIA:
            return None
            
        item = CACHE_MEMORIA[hash_prompt]
        
        # Verifica se o provedor e modelo são os mesmos
        if item.get("provedor") != provedor or item.get("modelo") != modelo:
            return None
            
        # Verifica se o cache expirou
        timestamp = item.get("timestamp", 0)
        if time.time() - timestamp > self.tempo_expiracao_memoria:
            # Remove do cache
            CACHE_MEMORIA.pop(hash_prompt, None)
            return None
            
        # Incrementa contador de uso
        item["contador_uso"] = item.get("contador_uso", 0) + 1
        
        return item.get("resposta")
    
    def _atualizar_cache_memoria(self, hash_prompt: str, provedor: str, modelo: str, resposta: str) -> None:
        """
        Atualiza o cache em memória.
        
        Args:
            hash_prompt: Hash do prompt
            provedor: Nome do provedor
            modelo: Nome do modelo
            resposta: Resposta da API
        """
        # Se o cache em memória está cheio, remove o item menos usado
        if len(CACHE_MEMORIA) >= CACHE_MEMORIA_LIMITE:
            self._remover_item_menos_usado()
            
        # Atualiza o cache
        CACHE_MEMORIA[hash_prompt] = {
            "provedor": provedor,
            "modelo": modelo,
            "resposta": resposta,
            "timestamp": time.time(),
            "contador_uso": 1
        }
    
    def _remover_item_menos_usado(self) -> None:
        """
        Remove o item menos usado do cache em memória.
        """
        item_menos_usado = None
        menor_contagem = float('inf')
        
        for hash_prompt, item in CACHE_MEMORIA.items():
            contador = item.get("contador_uso", 0)
            if contador < menor_contagem:
                menor_contagem = contador
                item_menos_usado = hash_prompt
                
        if item_menos_usado:
            CACHE_MEMORIA.pop(item_menos_usado, None)
    
    def _obter_cache_db(self, hash_prompt: str, provedor: str, modelo: str,
                      parametros: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Obtém uma resposta do cache no banco de dados.
        
        Args:
            hash_prompt: Hash do prompt
            provedor: Nome do provedor
            modelo: Nome do modelo
            parametros: Parâmetros adicionais (opcional)
            
        Returns:
            Resposta do cache ou None
        """
        try:
            # Busca no banco de dados
            item = CacheRespostaAPI.query.filter_by(
                hash_prompt=hash_prompt,
                provedor=provedor,
                modelo=modelo
            ).first()
            
            if not item:
                return None
                
            # Verifica se o cache expirou
            if item.data_expiracao and item.data_expiracao < datetime.datetime.now():
                # Remove do banco
                db.session.delete(item)
                db.session.commit()
                return None
                
            # Incrementa contador de uso
            item.contador_uso += 1
            db.session.commit()
            
            return item.resposta
            
        except Exception as e:
            logger.error(f"Erro ao obter cache do banco: {str(e)}")
            return None
    
    def _armazenar_cache_db(self, hash_prompt: str, provedor: str, modelo: str,
                         prompt: str, resposta: str, parametros: Optional[Dict[str, Any]] = None,
                         tempo_expiracao: Optional[int] = None) -> bool:
        """
        Armazena uma resposta no cache do banco de dados.
        
        Args:
            hash_prompt: Hash do prompt
            provedor: Nome do provedor
            modelo: Nome do modelo
            prompt: O prompt enviado para a API
            resposta: A resposta recebida da API
            parametros: Parâmetros adicionais (opcional)
            tempo_expiracao: Tempo em segundos até a expiração (opcional)
            
        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        try:
            # Verifica se já existe
            item = CacheRespostaAPI.query.filter_by(
                hash_prompt=hash_prompt,
                provedor=provedor,
                modelo=modelo
            ).first()
            
            if item:
                # Atualiza o item existente
                item.resposta = resposta
                item.contador_uso += 1
                
                if parametros:
                    item.parametros = json.dumps(parametros)
                    
                # Atualiza a data de expiração
                if tempo_expiracao:
                    item.data_expiracao = datetime.datetime.now() + datetime.timedelta(seconds=tempo_expiracao)
                else:
                    item.data_expiracao = datetime.datetime.now() + datetime.timedelta(seconds=self.tempo_expiracao_db)
            else:
                # Cria um novo item
                data_expiracao = None
                if tempo_expiracao:
                    data_expiracao = datetime.datetime.now() + datetime.timedelta(seconds=tempo_expiracao)
                elif self.tempo_expiracao_db:
                    data_expiracao = datetime.datetime.now() + datetime.timedelta(seconds=self.tempo_expiracao_db)
                
                novo_item = CacheRespostaAPI(
                    provedor=provedor,
                    modelo=modelo,
                    hash_prompt=hash_prompt,
                    prompt=prompt,
                    resposta=resposta,
                    parametros=json.dumps(parametros) if parametros else None,
                    data_expiracao=data_expiracao,
                    contador_uso=1
                )
                
                db.session.add(novo_item)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao armazenar cache no banco: {str(e)}")
            return False
    
    def _limpar_cache_expirado(self) -> int:
        """
        Limpa itens expirados do cache no banco de dados.
        
        Returns:
            Número de itens removidos
        """
        try:
            # Remove itens cuja data de expiração já passou
            agora = datetime.datetime.now()
            itens_expirados = CacheRespostaAPI.query.filter(
                CacheRespostaAPI.data_expiracao.isnot(None),
                CacheRespostaAPI.data_expiracao < agora
            ).delete()
            
            db.session.commit()
            return itens_expirados
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao limpar cache expirado: {str(e)}")
            return 0


# Função decoradora para cachear chamadas de API
def cachear_api(provedor: str, modelo: str, tempo_expiracao: Optional[int] = None):
    """
    Decorador para cachear chamadas de API.
    
    Args:
        provedor: Nome do provedor
        modelo: Nome do modelo
        tempo_expiracao: Tempo em segundos até a expiração (opcional)
        
    Returns:
        Decorador para a função
    """
    def decorador(func):
        def wrapper(*args, **kwargs):
            # Obtém o gerenciador de cache
            config = kwargs.get("cache_config", {})
            gerenciador = GerenciadorCache(config)
            
            # Verifica se o cache está habilitado
            if gerenciador.nivel_cache == 0:
                return func(*args, **kwargs)
                
            # Gera uma representação do prompt a partir dos argumentos
            # Para simplificar, considera apenas o primeiro argumento de texto
            texto_args = []
            for arg in args:
                if isinstance(arg, str):
                    texto_args.append(arg)
                    break
            
            # Adiciona argumentos nomeados relevantes
            prompt_kwargs = {}
            for chave in ["prompt", "messages", "system"]:
                if chave in kwargs:
                    valor = kwargs[chave]
                    if isinstance(valor, list):
                        # Converte mensagens para string
                        prompt_kwargs[chave] = json.dumps(valor)
                    else:
                        prompt_kwargs[chave] = valor
            
            # Combina em uma única string para usar como chave de cache
            prompt_texto = json.dumps([texto_args, prompt_kwargs])
            
            # Tenta obter do cache
            resposta_cache = gerenciador.obter_resposta_cache(
                provedor=provedor,
                modelo=modelo,
                prompt=prompt_texto
            )
            
            if resposta_cache:
                logger.info(f"Resposta obtida do cache para {provedor}/{modelo}")
                return resposta_cache
            
            # Se não encontrou no cache, chama a função original
            resposta = func(*args, **kwargs)
            
            # Armazena no cache
            gerenciador.armazenar_resposta_cache(
                provedor=provedor,
                modelo=modelo,
                prompt=prompt_texto,
                resposta=resposta,
                tempo_expiracao=tempo_expiracao
            )
            
            return resposta
        
        return wrapper
    
    return decorador


# Funções auxiliares para uso fácil
def obter_resposta_cache(provedor: str, modelo: str, prompt: str,
                       parametros: Optional[Dict[str, Any]] = None,
                       config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Função auxiliar para obter uma resposta do cache.
    
    Args:
        provedor: Nome do provedor
        modelo: Nome do modelo
        prompt: O prompt enviado para a API
        parametros: Parâmetros adicionais da chamada (opcional)
        config: Configurações adicionais (opcional)
        
    Returns:
        Resposta do cache ou None
    """
    gerenciador = GerenciadorCache(config)
    return gerenciador.obter_resposta_cache(provedor, modelo, prompt, parametros)


def armazenar_resposta_cache(provedor: str, modelo: str, prompt: str, resposta: str,
                           parametros: Optional[Dict[str, Any]] = None,
                           tempo_expiracao: Optional[int] = None,
                           config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Função auxiliar para armazenar uma resposta no cache.
    
    Args:
        provedor: Nome do provedor
        modelo: Nome do modelo
        prompt: O prompt enviado para a API
        resposta: A resposta recebida da API
        parametros: Parâmetros adicionais da chamada (opcional)
        tempo_expiracao: Tempo em segundos até a expiração (opcional)
        config: Configurações adicionais (opcional)
        
    Returns:
        True se armazenado com sucesso, False caso contrário
    """
    gerenciador = GerenciadorCache(config)
    return gerenciador.armazenar_resposta_cache(
        provedor, modelo, prompt, resposta, parametros, tempo_expiracao
    )


def limpar_cache(provedor: Optional[str] = None, modelo: Optional[str] = None,
               config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Função auxiliar para limpar o cache.
    
    Args:
        provedor: Nome do provedor (opcional)
        modelo: Nome do modelo (opcional)
        config: Configurações adicionais (opcional)
        
    Returns:
        Dicionário com o resultado da operação
    """
    gerenciador = GerenciadorCache(config)
    return gerenciador.limpar_cache_provedor(provedor, modelo)


def obter_estatisticas_cache(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Função auxiliar para obter estatísticas do cache.
    
    Args:
        config: Configurações adicionais (opcional)
        
    Returns:
        Dicionário com estatísticas
    """
    gerenciador = GerenciadorCache(config)
    return gerenciador.estatisticas_cache()