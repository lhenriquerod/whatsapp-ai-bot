"""
Name Utilities
Funções para normalização e validação de nomes de contatos.
"""
import re
from typing import Tuple


def normalize_name(user_input: str) -> str:
    """
    Normaliza o input do usuário para extrair apenas o nome.
    
    Args:
        user_input: Texto enviado pelo usuário
        
    Returns:
        Nome normalizado e capitalizado
        
    Examples:
        >>> normalize_name("meu nome é joão silva")
        "João Silva"
        >>> normalize_name("MARIA123")
        "Maria"
        >>> normalize_name("sou o Pedro 😊")
        "Pedro"
    """
    if not user_input:
        return ""

    # Remove frases comuns de apresentação
    text = user_input.lower()
    text = re.sub(r'(meu nome é|eu sou|me chamo|sou o|sou a|pode me chamar de|meu nome e|eu me chamo)', '', text)
    
    # Remove emojis (caracteres Unicode não alfanuméricos)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove números
    text = re.sub(r'\d+', '', text)
    
    # Remove espaços extras
    text = ' '.join(text.split())
    
    # Capitaliza primeira letra de cada palavra
    name = text.title().strip()
    
    return name


def is_valid_name(name: str) -> bool:
    """
    Valida se o texto parece ser um nome válido.
    
    Args:
        name: Nome normalizado
        
    Returns:
        True se válido, False caso contrário
        
    Examples:
        >>> is_valid_name("João")
        True
        >>> is_valid_name("Maria Silva")
        True
        >>> is_valid_name("A")
        False
        >>> is_valid_name("123")
        False
    """
    if not name or len(name) < 2 or len(name) > 100:
        return False
    
    # Deve conter apenas letras (incluindo acentuadas) e espaços
    if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', name):
        return False
    
    return True


def is_confirmation(user_input: str) -> Tuple[bool, bool]:
    """
    Identifica se a resposta é uma confirmação ou negação.
    
    Args:
        user_input: Resposta do usuário
        
    Returns:
        Tupla (is_confirmation, is_positive)
        - (True, True) para confirmação positiva
        - (True, False) para confirmação negativa
        - (False, False) se não for confirmação
        
    Examples:
        >>> is_confirmation("sim")
        (True, True)
        >>> is_confirmation("não")
        (True, False)
        >>> is_confirmation("talvez")
        (False, False)
    """
    text = user_input.lower().strip()
    
    # Confirmações positivas
    positive = [
        'sim', 's', 'yes', 'y', 'yep', 'yeah',
        'correto', 'certo', 'exato', 'isso mesmo',
        'ok', 'okay', 'beleza', 'confirmo',
        'perfeito', 'pode ser', 'isso', 'uhum'
    ]
    
    for word in positive:
        if word in text:
            return (True, True)
    
    # Confirmações negativas
    negative = [
        'não', 'nao', 'n', 'no', 'nope',
        'incorreto', 'errado', 'negativo',
        'está errado', 'ta errado', 'nops'
    ]
    
    for word in negative:
        if word in text:
            return (True, False)
    
    return (False, False)
