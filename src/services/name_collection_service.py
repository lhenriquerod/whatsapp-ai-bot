"""
Name Collection Service
Gerencia o fluxo de coleta e confirmação de nome do contato.
"""
import logging
from typing import Tuple, Optional

from src.utils.name_utils import normalize_name, is_valid_name, is_confirmation
from src.services.state_manager import (
    ConversationState,
    get_or_create_conversation_with_state,
    update_conversation_state,
    update_conversation_name,
    save_temp_name,
    get_temp_name,
    clear_temp_name
)

logger = logging.getLogger(__name__)


# Mensagens padrão do fluxo
MESSAGES = {
    "welcome": (
        "Olá! 👋 Seja bem-vindo(a)!\n\n"
        "Para que eu possa te atender melhor, por favor, qual é o seu nome?"
    ),
    "invalid_name": (
        "Desculpe, não consegui identificar um nome válido. "
        "Por favor, me diga apenas seu nome:"
    ),
    "confirm_name": (
        "Prazer em te conhecer, {name}! 😊\n\n"
        "Está correto? Por favor, responda apenas:\n"
        "- \"Sim\" para confirmar\n"
        "- \"Não\" para corrigir"
    ),
    "name_saved": (
        "Ótimo, {name}! 🎉\n\n"
        "Agora podemos conversar. Como posso te ajudar?"
    ),
    "ask_name_again": (
        "Ok, por favor me diga seu nome correto:"
    ),
    "need_confirmation": (
        "Por favor, responda apenas 'Sim' para confirmar ou 'Não' para corrigir seu nome."
    ),
    "need_name_first": (
        "Desculpe, preciso que você me informe seu nome primeiro para podermos conversar.\n"
        "Por favor, qual é o seu nome?"
    )
}


def process_name_collection_flow(
    message_text: str,
    external_contact_id: str,
    user_id: Optional[str] = None
) -> Tuple[str, bool]:
    """
    Processa o fluxo de coleta de nome baseado no estado da conversa.
    
    Args:
        message_text: Mensagem enviada pelo usuário
        external_contact_id: ID externo do contato (número WhatsApp)
        user_id: ID do usuário (empresa) no sistema
        
    Returns:
        Tupla (response_message, should_continue_to_ai)
        - response_message: Mensagem para enviar ao usuário
        - should_continue_to_ai: True se deve processar com AI, False se já respondeu
        
    Example:
        >>> response, continue_to_ai = process_name_collection_flow("João", "+5511999999999")
        >>> print(response)
        "Prazer em te conhecer, João! 😊..."
        >>> print(continue_to_ai)
        False  # Não processa com AI, já respondeu
    """
    # Buscar ou criar conversa
    conversation = get_or_create_conversation_with_state(
        phone_number=external_contact_id,
        user_id=user_id,
        external_contact_id=external_contact_id
    )
    
    conversation_id = conversation['id']
    current_state = conversation.get('conversation_state', ConversationState.ACTIVE)
    
    logger.info(f"Processando mensagem no estado {current_state} para conversa {conversation_id}")
    
    # Estado: AWAITING_NAME - Aguardando nome do usuário
    if current_state == ConversationState.AWAITING_NAME:
        return _handle_awaiting_name(message_text, conversation_id)
    
    # Estado: CONFIRMING_NAME - Aguardando confirmação do nome
    elif current_state == ConversationState.CONFIRMING_NAME:
        return _handle_confirming_name(message_text, conversation_id)
    
    # Estado: ACTIVE - Conversa normal
    elif current_state == ConversationState.ACTIVE:
        # Conversa já tem nome, pode processar normalmente com AI
        return ("", True)
    
    # Estado desconhecido - tratar como ACTIVE
    else:
        logger.warning(f"Estado desconhecido: {current_state}, tratando como ACTIVE")
        return ("", True)


def _handle_awaiting_name(message_text: str, conversation_id: str) -> Tuple[str, bool]:
    """
    Trata mensagem no estado AWAITING_NAME.
    
    Args:
        message_text: Mensagem do usuário
        conversation_id: ID da conversa
        
    Returns:
        Tupla (response, should_continue)
    """
    # Normalizar e validar nome
    name = normalize_name(message_text)
    
    if not is_valid_name(name):
        logger.info(f"Nome inválido recebido: '{message_text}' -> '{name}'")
        return (MESSAGES["invalid_name"], False)
    
    # Nome válido - salvar temporariamente e pedir confirmação
    save_temp_name(conversation_id, name)
    update_conversation_state(conversation_id, ConversationState.CONFIRMING_NAME)
    
    logger.info(f"Nome '{name}' salvo temporariamente para conversa {conversation_id}")
    
    response = MESSAGES["confirm_name"].format(name=name)
    return (response, False)


def _handle_confirming_name(message_text: str, conversation_id: str) -> Tuple[str, bool]:
    """
    Trata mensagem no estado CONFIRMING_NAME.
    
    Args:
        message_text: Mensagem do usuário
        conversation_id: ID da conversa
        
    Returns:
        Tupla (response, should_continue)
    """
    # Verificar se é confirmação
    is_conf, is_positive = is_confirmation(message_text)
    
    if not is_conf:
        logger.info(f"Resposta não é confirmação: '{message_text}'")
        return (MESSAGES["need_confirmation"], False)
    
    temp_name = get_temp_name(conversation_id)
    
    if is_positive:
        # Confirmação positiva - salvar nome definitivamente
        update_conversation_name(conversation_id, temp_name)
        clear_temp_name(conversation_id)
        
        logger.info(f"Nome '{temp_name}' confirmado e salvo para conversa {conversation_id}")
        
        response = MESSAGES["name_saved"].format(name=temp_name)
        return (response, False)
    
    else:
        # Confirmação negativa - voltar para coletar nome
        update_conversation_state(conversation_id, ConversationState.AWAITING_NAME)
        clear_temp_name(conversation_id)
        
        logger.info(f"Nome '{temp_name}' rejeitado, voltando para AWAITING_NAME")
        
        return (MESSAGES["ask_name_again"], False)


def get_welcome_message() -> str:
    """
    Retorna a mensagem de boas-vindas para novo contato.
    
    Returns:
        Mensagem de boas-vindas
    """
    return MESSAGES["welcome"]
