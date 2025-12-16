"""
ETL Service - Importação de Processos via Upload
Processamento robusto de planilhas Excel com validações múltiplas
"""
from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime
from decimal import Decimal
import re
from io import BytesIO

from models import (
    db, Processo, ProcessoTributario, ProcessoTrabalhista, ProcessoCivel,
    ProcessoCamposEspecificos
)


class ProcessoETLService:
    """Service para ETL de importação de processos"""
    
    def __init__(self):
        self.erros = []
        self.avisos = []
        self.transformacoes = []
        
    def importar_planilha(self, arquivo_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Importa planilha Excel/CSV com ETL completo
        
        Args:
            arquivo_bytes: Bytes do arquivo
            filename: Nome do arquivo
            
        Returns:
            Relatório detalhado da importação
        """
        inicio = datetime.now()
        
        try:
            # Fase 1: Validação e Extração
            df = self._extrair_dados(arquivo_bytes, filename)
            total_registros = len(df)
            
            # Fase 2: Limpeza Conservadora
            df = self._limpar_dados(df)
            
            # Fase 3: Validação Estrutural
            df_valido, df_invalido = self._validar_dados(df)
            
            # Fase 4: Transformação
            df_valido = self._transformar_dados(df_valido)
            
            # Fase 5: Inserção Transacional
            importados, erros_insercao = self._inserir_dados(df_valido)
            
            # Gerar Relatório
            tempo_total = (datetime.now() - inicio).total_seconds()
            
            return {
                'sucesso': True,
                'total_registros': total_registros,
                'importados': len(importados),
                'erros': len(df_invalido) + len(erros_insercao),
                'avisos': len(self.avisos),
                'ids_importados': importados,
                'registros_com_erro': df_invalido.to_dict('records') if len(df_invalido) > 0 else [],
                'erros_insercao': erros_insercao,
                'avisos': self.avisos,
                'transformacoes': self.transformacoes[:100],  # Limitar a 100
                'tempo_segundos': round(tempo_total, 2),
                'taxa_sucesso': round((len(importados) / total_registros * 100), 2) if total_registros > 0 else 0
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'total_registros': 0,
                'importados': 0
            }
    
    def _extrair_dados(self, arquivo_bytes: bytes, filename: str) -> pd.DataFrame:
        """Fase 1: Extração e validação do arquivo"""
        extensao = filename.lower().split('.')[-1]
        
        if extensao in ['xlsx', 'xls']:
            df = pd.read_excel(BytesIO(arquivo_bytes))
        elif extensao == 'csv':
            df = pd.read_csv(BytesIO(arquivo_bytes))
        else:
            raise ValueError(f"Formato não suportado: {extensao}")
        
        if len(df) == 0:
            raise ValueError("Planilha vazia")
        
        # Normalizar nomes de colunas
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        return df
    
    def _limpar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fase 2: Limpeza conservadora"""
        df_limpo = df.copy()
        
        # Limpar strings
        for col in df_limpo.select_dtypes(include=['object']).columns:
            df_limpo[col] = df_limpo[col].apply(self._limpar_string)
        
        self.transformacoes.append({
            'etapa': 'limpeza',
            'registros_afetados': len(df_limpo)
        })
        
        return df_limpo
    
    def _limpar_string(self, valor: Any) -> Any:
        """Limpeza de string preservando dados"""
        if pd.isna(valor):
            return None
        
        if not isinstance(valor, str):
            return valor
        
        # Remove espaços início/fim
        valor = valor.strip()
        
        # Substitui múltiplos espaços por um
        valor = re.sub(r'\s+', ' ', valor)
        
        # Remove caracteres de controle (exceto \n)
        valor = ''.join(char for char in valor if ord(char) >= 32 or char == '\n')
        
        return valor if valor else None
    
    def _validar_dados(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fase 3: Validação estrutural"""
        registros_validos = []
        registros_invalidos = []
        
        for idx, row in df.iterrows():
            erros_linha = []
            
            # Validação obrigatória: pasta
            if pd.isna(row.get('pasta')) or not str(row.get('pasta')).strip():
                erros_linha.append('pasta vazia')
            
            # Validação CNJ (se presente)
            cnj = row.get('numero_cnj') or row.get('cnj')
            if cnj and not pd.isna(cnj):
                if not self._validar_cnj(str(cnj)):
                    erros_linha.append(f'CNJ inválido: {cnj}')
            
            # Validação natureza
            natureza = row.get('natureza')
            if natureza:
                natureza_id = self._mapear_natureza(str(natureza))
                if not natureza_id:
                    erros_linha.append(f'Natureza inválida: {natureza}')
            
            if erros_linha:
                row_dict = row.to_dict()
                row_dict['_erros'] = ', '.join(erros_linha)
                registros_invalidos.append(row_dict)
            else:
                registros_validos.append(row.to_dict())
        
        df_valido = pd.DataFrame(registros_validos) if registros_validos else pd.DataFrame()
        df_invalido = pd.DataFrame(registros_invalidos) if registros_invalidos else pd.DataFrame()
        
        return df_valido, df_invalido
    
    def _validar_cnj(self, cnj: str) -> bool:
        """Validação básica de CNJ"""
        # Remove caracteres não numéricos
        cnj_numeros = re.sub(r'[^0-9]', '', cnj)
        
        # CNJ tem 20 dígitos
        if len(cnj_numeros) != 20:
            return False
        
        # Regex padrão: NNNNNNN-DD.AAAA.J.TR.OOOO
        pattern = r'^\d{7}-?\d{2}\.?\d{4}\.?\d{1}\.?\d{2}\.?\d{4}$'
        return bool(re.match(pattern, cnj))
    
    def _transformar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fase 4: Transformação de dados"""
        df_transformado = df.copy()
        
        # Mapear natureza ID
        if 'natureza' in df_transformado.columns:
            df_transformado['natureza_id'] = df_transformado['natureza'].apply(self._mapear_natureza)
        
        # Mapear status ID
        if 'status' in df_transformado.columns:
            df_transformado['status_id'] = df_transformado['status'].apply(self._mapear_status)
        else:
            df_transformado['status_id'] = 1  # Ativo por padrão
        
        # Converter valores monetários
        for col in ['valor_causa', 'valor_principal', 'valor_multa', 'valor_acordo']:
            if col in df_transformado.columns:
                df_transformado[col] = df_transformado[col].apply(self._converter_moeda)
        
        # Converter datas
        for col in ['data_distribuicao', 'data_acordo']:
            if col in df_transformado.columns:
                df_transformado[col] = pd.to_datetime(df_transformado[col], errors='coerce')
        
        return df_transformado
    
    def _mapear_natureza(self, valor: str) -> int:
        """Mapeia nome da natureza para ID"""
        if pd.isna(valor):
            return 1  # Tributário padrão
        
        valor = str(valor).lower().strip()
        
        mapeamento = {
            'tributário': 1,
            'tributario': 1,
            'trib': 1,
            'trabalhista': 2,
            'trab': 2,
            'cível': 3,
            'civel': 3,
            'civil': 3
        }
        
        return mapeamento.get(valor, 1)
    
    def _mapear_status(self, valor: str) -> int:
        """Mapeia nome do status para ID"""
        if pd.isna(valor):
            return 1  # Ativo padrão
        
        valor = str(valor).lower().strip()
        
        mapeamento = {
            'ativo': 1,
            'em andamento': 1,
            'arquivado': 2,
            'suspenso': 3
        }
        
        return mapeamento.get(valor, 1)
    
    def _converter_moeda(self, valor: Any) -> Decimal:
        """Converte string monetária para Decimal"""
        if pd.isna(valor):
            return None
        
        if isinstance(valor, (int, float)):
            return Decimal(str(valor))
        
        # Remove R$, pontos de milhar, substitui vírgula por ponto
        valor_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        
        try:
            return Decimal(valor_str)
        except:
            return None
    
    def _inserir_dados(self, df: pd.DataFrame) -> Tuple[List[int], List[Dict]]:
        """Fase 5: Inserção transacional em batches"""
        importados = []
        erros = []
        
        batch_size = 50
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            inicio = batch_num * batch_size
            fim = min((batch_num + 1) * batch_size, len(df))
            batch = df.iloc[inicio:fim]
            
            try:
                for _, row in batch.iterrows():
                    processo_id = self._inserir_processo(row)
                    if processo_id:
                        importados.append(processo_id)
                
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                for _, row in batch.iterrows():
                    erros.append({
                        'pasta': row.get('pasta'),
                        'erro': str(e)
                    })
        
        return importados, erros
    
    def _inserir_processo(self, row: pd.Series) -> int:
        """Insere um processo no banco"""
        # Criar processo base
        processo = Processo(
            pasta=str(row.get('pasta')),
            numero_cnj=row.get('numero_cnj') or row.get('cnj'),
            natureza_id=int(row.get('natureza_id', 1)),
            status_id=int(row.get('status_id', 1)),
            titulo=row.get('titulo'),
            valor_causa=row.get('valor_causa'),
            data_distribuicao=row.get('data_distribuicao'),
            data_criacao=datetime.now(),
            ativo=True
        )
        
        db.session.add(processo)
        db.session.flush()
        
        # Criar dados específicos por natureza
        natureza_id = int(row.get('natureza_id', 1))
        
        if natureza_id == 1:  # Tributário
            self._criar_dados_tributario(processo.id_processo, row)
        elif natureza_id == 2:  # Trabalhista
            self._criar_dados_trabalhista(processo.id_processo, row)
        elif natureza_id == 3:  # Cível
            self._criar_dados_civel(processo.id_processo, row)
        
        return processo.id_processo
    
    def _criar_dados_tributario(self, processo_id: int, row: pd.Series):
        """Cria dados específicos tributário"""
        trib = ProcessoTributario(
            processo_id=processo_id,
            numero_aiim=row.get('numero_aiim'),
            valor_principal=row.get('valor_principal'),
            valor_multa=row.get('valor_multa')
        )
        db.session.add(trib)
    
    def _criar_dados_trabalhista(self, processo_id: int, row: pd.Series):
        """Cria dados específicos trabalhista"""
        trab = ProcessoTrabalhista(
            processo_id=processo_id,
            valor_acordo=row.get('valor_acordo')
        )
        db.session.add(trab)
    
    def _criar_dados_civel(self, processo_id: int, row: pd.Series):
        """Cria dados específicos cível"""
        civel = ProcessoCivel(
            processo_id=processo_id,
            valor_acordo=row.get('valor_acordo)
        )
        db.session.add(civel)
