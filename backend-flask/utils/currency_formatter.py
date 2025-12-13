"""
Utilitário universal para formatação monetária
Padrão brasileiro com símbolo R$ e separadores corretos
"""

import locale
from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Optional

def format_currency(value: Union[float, int, str, Decimal, None], 
                   include_symbol: bool = True, 
                   decimal_places: int = 2) -> str:
    """
    Formata valor para moeda brasileira com padrão R$ XX.XXX,XX
    
    Args:
        value: Valor a ser formatado (float, int, str, Decimal ou None)
        include_symbol: Se deve incluir o símbolo R$ (padrão: True)
        decimal_places: Número de casas decimais (padrão: 2)
    
    Returns:
        String formatada no padrão brasileiro
        
    Examples:
        format_currency(1234.56) -> "R$ 1.234,56"
        format_currency(1234.56, False) -> "1.234,56"
        format_currency(0) -> "R$ 0,00"
        format_currency(None) -> "R$ 0,00"
    """
    
    # Tratar valores None ou vazios
    if value is None or value == "":
        return "R$ 0,00" if include_symbol else "0,00"
    
    try:
        # Converter para Decimal para precisão
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto ponto e vírgula
            clean_value = value.replace("R$", "").replace(" ", "").strip()
            # Substituir vírgula por ponto se necessário
            if "," in clean_value and "." not in clean_value:
                clean_value = clean_value.replace(",", ".")
            elif "," in clean_value and "." in clean_value:
                # Formato brasileiro: 1.234,56 -> 1234.56
                parts = clean_value.split(",")
                if len(parts) == 2:
                    integer_part = parts[0].replace(".", "")
                    decimal_part = parts[1]
                    clean_value = f"{integer_part}.{decimal_part}"
            value = float(clean_value)
        
        # Converter para Decimal
        decimal_value = Decimal(str(value))
        
        # Arredondar para o número de casas decimais especificado
        rounded_value = decimal_value.quantize(
            Decimal('0.' + '0' * decimal_places), 
            rounding=ROUND_HALF_UP
        )
        
        # Converter para float para formatação
        float_value = float(rounded_value)
        
        # Separar parte inteira e decimal
        integer_part = int(abs(float_value))
        decimal_part = abs(float_value) - integer_part
        
        # Formatar parte inteira com pontos como separadores de milhares
        formatted_integer = f"{integer_part:,}".replace(",", ".")
        
        # Formatar parte decimal
        formatted_decimal = f"{decimal_part:.{decimal_places}f}"[2:]  # Remove "0."
        
        # Combinar partes
        formatted_value = f"{formatted_integer},{formatted_decimal}"
        
        # Adicionar sinal negativo se necessário
        if float_value < 0:
            formatted_value = f"-{formatted_value}"
        
        # Adicionar símbolo R$ se solicitado
        if include_symbol:
            return f"R$ {formatted_value}"
        else:
            return formatted_value
            
    except (ValueError, TypeError, AttributeError):
        # Em caso de erro, retornar valor padrão
        return "R$ 0,00" if include_symbol else "0,00"


def parse_currency(formatted_value: str) -> float:
    """
    Converte string formatada em moeda para float
    
    Args:
        formatted_value: String no formato "R$ 1.234,56" ou "1.234,56"
    
    Returns:
        Valor float correspondente
        
    Examples:
        parse_currency("R$ 1.234,56") -> 1234.56
        parse_currency("1.234,56") -> 1234.56
    """
    
    if not formatted_value or formatted_value.strip() == "":
        return 0.0
    
    try:
        # Remove R$ e espaços
        clean_value = str(formatted_value).replace("R$", "").strip()
        
        # Se contém vírgula e ponto, é formato brasileiro
        if "," in clean_value and "." in clean_value:
            parts = clean_value.split(",")
            if len(parts) == 2:
                integer_part = parts[0].replace(".", "")
                decimal_part = parts[1]
                return float(f"{integer_part}.{decimal_part}")
        
        # Se contém apenas vírgula, substituir por ponto
        elif "," in clean_value:
            clean_value = clean_value.replace(",", ".")
        
        # Se contém apenas pontos, verificar se é separador de milhares ou decimal
        elif "." in clean_value:
            parts = clean_value.split(".")
            if len(parts) > 2:
                # Múltiplos pontos = separadores de milhares + decimal
                integer_parts = parts[:-1]
                decimal_part = parts[-1]
                integer_value = "".join(integer_parts)
                clean_value = f"{integer_value}.{decimal_part}"
        
        return float(clean_value)
        
    except (ValueError, TypeError, AttributeError):
        return 0.0


# Função para uso direto em templates Jinja2
def currency_filter(value):
    """Filtro Jinja2 para formatação monetária"""
    return format_currency(value)


# Função para validação de entrada monetária
def validate_currency_input(value: str) -> tuple[bool, float]:
    """
    Valida entrada de valor monetário
    
    Returns:
        tuple: (is_valid, parsed_value)
    """
    try:
        parsed = parse_currency(value)
        return True, parsed
    except:
        return False, 0.0


# Constantes para uso em toda aplicação
CURRENCY_SYMBOL = "R$"
CURRENCY_DECIMAL_PLACES = 2
CURRENCY_THOUSANDS_SEPARATOR = "."
CURRENCY_DECIMAL_SEPARATOR = ","