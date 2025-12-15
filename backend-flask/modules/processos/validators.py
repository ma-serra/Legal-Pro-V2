"""
Validadores para Processos
CNJ, CPF/CNPJ, Valores Monetários
"""
import re
from typing import Optional
from decimal import Decimal


class CNJValidator:
    """Validador de número CNJ"""
    
    # Formato: NNNNNNN-DD.AAAA.J.TRT.OOOO
    PATTERN = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$')
    
    @staticmethod
    def validar(numero_cnj: str) -> bool:
        """
        Valida formato e dígitos verificadores do número CNJ
        
        Args:
            numero_cnj: Número no formato NNNNNNN-DD.AAAA.J.TRT.OOOO
            
        Returns:
            True se válido
        """
        if not numero_cnj:
            return False
        
        # Verificar formato
        if not CNJValidator.PATTERN.match(numero_cnj):
            return False
        
        # Extrair partes
        partes = numero_cnj.replace('-', '').replace('.', '')
        
        # Número sequencial (7 dígitos)
        numero = partes[0:7]
        
        # Dígitos verificadores (2 dígitos)
        dv_informado = partes[7:9]
        
        # Ano (4 dígitos)
        ano = partes[9:13]
        
        # Segmento judiciário (1 dígito)
        segmento = partes[13:14]
        
        # Tribunal (2 dígitos)
        tribunal = partes[14:16]
        
        # Origem (4 dígitos)
        origem = partes[16:20]
        
        # Calcular DV
        base = origem + ano + segmento + tribunal + numero
        resto = int(base) % 97
        dv_calculado = 98 - resto
        
        return str(dv_calculado).zfill(2) == dv_informado
    
    @staticmethod
    def formatar(numero_limpo: str) -> Optional[str]:
        """
        Formata número CNJ
        
        Args:
            numero_limpo: Apenas dígitos (20 caracteres)
            
        Returns:
            Número formatado ou None
        """
        if not numero_limpo or len(numero_limpo) != 20:
            return None
        
        return f"{numero_limpo[0:7]}-{numero_limpo[7:9]}.{numero_limpo[9:13]}.{numero_limpo[13:14]}.{numero_limpo[14:16]}.{numero_limpo[16:20]}"


class CPFCNPJValidator:
    """Validador de CPF e CNPJ"""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF"""
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
        
        if cpf == cpf[0] * 11:
            return False
        
        # Calcular primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10 % 11) % 10
        
        # Calcular segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10 % 11) % 10
        
        return cpf[-2:] == f"{digito1}{digito2}"
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """Valida CNPJ"""
        cnpj = ''.join(filter(str.isdigit, cnpj))
        
        if len(cnpj) != 14:
            return False
        
        if cnpj == cnpj[0] * 14:
            return False
        
        # Calcular primeiro dígito
        peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
        digito1 = (soma % 11)
        digito1 = 0 if digito1 < 2 else 11 - digito1
        
        # Calcular segundo dígito
        peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
        digito2 = (soma % 11)
        digito2 = 0 if digito2 < 2 else 11 - digito2
        
        return cnpj[-2:] == f"{digito1}{digito2}"


class MonetaryValidator:
    """Validador de valores monetários"""
    
    @staticmethod
    def validar_valor(valor: any, permitir_zero: bool = True, permitir_negativo: bool = False) -> bool:
        """
        Valida valor monetário
        
        Args:
            valor: Valor a validar
            permitir_zero: Se permite zero
            permitir_negativo: Se permite negativo
            
        Returns:
            True se válido
        """
        try:
            if valor is None:
                return True
            
            valor_decimal = Decimal(str(valor))
            
            if not permitir_zero and valor_decimal == 0:
                return False
            
            if not permitir_negativo and valor_decimal < 0:
                return False
            
            # Verificar máximo 2 casas decimais
            if valor_decimal.as_tuple().exponent < -2:
                return False
            
            return True
            
        except:
            return False
    
    @staticmethod
    def formatar_valor(valor: any, simbolo: str = 'R$') -> str:
        """
        Formata valor monetário
        
        Args:
            valor: Valor a formatar
            simbolo: Símbolo da moeda
            
        Returns:
            Valor formatado
        """
        if valor is None:
            return f"{simbolo} 0,00"
        
        valor_decimal = Decimal(str(valor))
        valor_formatado = f"{valor_decimal:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return f"{simbolo} {valor_formatado}"
    
    @staticmethod
    def parse_valor(valor_str: str) -> Optional[Decimal]:
        """
        Parse string monetária para Decimal
        
        Args:
            valor_str: String como "R$ 1.234,56"
            
        Returns:
            Decimal ou None
        """
        try:
            # Remover símbolo e espaços
            valor_limpo = valor_str.replace('R$', '').replace(' ', '')
            
            # Trocar separadores
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            
            return Decimal(valor_limpo)
            
        except:
            return None


class DateValidator:
    """Validador de datas"""
    
    @staticmethod
    def validar_data_futura(data: any, permitir_hoje: bool = True) -> bool:
        """Valida se data não é futura"""
        from datetime import datetime, date
        
        if data is None:
            return True
        
        if isinstance(data, str):
            data = datetime.fromisoformat(data).date()
        elif isinstance(data, datetime):
            data = data.date()
        
        hoje = date.today()
        
        if permitir_hoje:
            return data <= hoje
        else:
            return data < hoje
    
    @staticmethod
    def validar_periodo(data_inicio: any, data_fim: any) -> bool:
        """Valida se data_fim >= data_inicio"""
        if data_inicio is None or data_fim is None:
            return True
        
        from datetime import datetime
        
        if isinstance(data_inicio, str):
            data_inicio = datetime.fromisoformat(data_inicio)
        if isinstance(data_fim, str):
            data_fim = datetime.fromisoformat(data_fim)
        
        return data_fim >= data_inicio
