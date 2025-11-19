"""
Agent Personality Service
Handles fetching and formatting agent personality configuration from Supabase.
"""
import logging
from typing import Optional, Dict, Any

from src.services.supabase_service import _client

logger = logging.getLogger(__name__)

# Personality level mapping
PERSONALITY_LEVELS = {
    1: "Extremely formal",
    2: "Formal",
    3: "Slightly formal",
    4: "Balanced towards formal",
    5: "Balanced (professional and friendly)",
    6: "Balanced towards casual",
    7: "Casual",
    8: "Excited and enthusiastic",
    9: "Very enthusiastic",
    10: "Technical and expert"
}

# Voice tone instructions
VOICE_TONE_INSTRUCTIONS = {
    "formal": "Use formal language, avoid slang and contractions",
    "friendly": "Use conversational tone, be warm and accessible",
    "objective": "Be direct and concise, focus on facts",
    "casual": "Use casual language, slang is welcome"
}

# Treatment form instructions
ADDRESS_FORM_INSTRUCTIONS = {
    "you_informal": "Address customer informally (você)",
    "you_formal": "Address customer formally (senhor/senhora)",
    "sir_madam": "Use informal treatment like 'tu' if appropriate"
}

# Default personality fallback
DEFAULT_PERSONALITY = {
    "name": "Virtual Assistant",
    "personality_level": 5,
    "voice_tone": "friendly",
    "address_form": "you_informal",
    "initial_message": "Hello! How can I help you?"
}


def get_agent_personality(user_id: str) -> Dict[str, Any]:
    """
    Fetch agent personality configuration from agent_personality table.
    
    Args:
        user_id: User UUID
        
    Returns:
        Dictionary with personality configuration. Returns default values if not found.
        
    Keys returned:
        - name: Agent name
        - personality_level: Personality level (1-10)
        - voice_tone: Voice tone (formal|friendly|objective|casual)
        - address_form: Treatment form (you_informal|you_formal|sir_madam)
        - initial_message: Initial greeting message
        
    Example:
        >>> personality = get_agent_personality("uuid-here")
        >>> print(personality["name"])
        "RAG-E Assistant"
    """
    try:
        result = _client.table("agent_personality") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        
        if result.data:
            logger.info(f"Personality found for user_id={user_id[-4:]}")
            return result.data
        
        logger.warning(f"No personality found for user_id={user_id[-4:]}, using defaults")
        return DEFAULT_PERSONALITY.copy()
        
    except Exception as e:
        logger.warning(f"Error fetching personality for user_id={user_id[-4:]}: {e}. Using defaults")
        return DEFAULT_PERSONALITY.copy()


def format_personality_context(personality: Dict[str, Any]) -> str:
    """
    Format personality configuration into readable context for AI.
    
    Args:
        personality: Personality dictionary from get_agent_personality()
        
    Returns:
        Formatted personality context string
        
    Example output:
        === PERSONALIDADE DO AGENTE ===
        Nome: RAG-E Assistant
        Nível de Personalidade: 5 (Equilibrado - profissional e amigável)
        Tom de Voz: amigavel
        Forma de Tratamento: voce
        Mensagem Inicial: "Olá! Como posso ajudar você hoje?"
        
        Instruções de comportamento:
        - Use tom conversacional, seja caloroso e acessível
        - Trate o cliente por 'você'
    """
    lines = []
    
    lines.append("=== AGENT PERSONALITY ===")
    lines.append(f"Name: {personality.get('name', 'Virtual Assistant')}")
    
    # Personality level with description
    level = personality.get("personality_level", 5)
    level_desc = PERSONALITY_LEVELS.get(level, "Balanced")
    lines.append(f"Personality Level: {level} ({level_desc})")
    
    lines.append(f"Voice Tone: {personality.get('voice_tone', 'friendly')}")
    lines.append(f"Address Form: {personality.get('address_form', 'you_informal')}")
    
    # Initial greeting
    initial_message = personality.get("initial_message", "Hello! How can I help?")
    lines.append(f"Initial Message: \"{initial_message}\"")
    lines.append("")
    
    # Behavioral instructions
    lines.append("Behavioral Instructions:")
    
    voice_tone = personality.get("voice_tone", "friendly")
    if voice_tone in VOICE_TONE_INSTRUCTIONS:
        lines.append(f"- {VOICE_TONE_INSTRUCTIONS[voice_tone]}")
    
    address_form = personality.get("address_form", "you_informal")
    if address_form in ADDRESS_FORM_INSTRUCTIONS:
        lines.append(f"- {ADDRESS_FORM_INSTRUCTIONS[address_form]}")
    
    # Add personality-level specific instructions
    if level <= 3:
        lines.append("- Maintain extreme formality and professional distance")
    elif level >= 8:
        lines.append("- Show enthusiasm and energy in responses")
        lines.append("- Use emojis when appropriate to convey emotion")
    
    lines.append("")
    
    return "\n".join(lines)


def build_system_prompt_with_personality(
    knowledge_base_context: str,
    personality: Dict[str, Any]
) -> str:
    """
    Build complete system prompt combining personality and knowledge base.
    
    Args:
        knowledge_base_context: Formatted knowledge base from get_context()
        personality: Personality dict from get_agent_personality()
        
    Returns:
        Complete system prompt for AI
        
    Example:
        >>> kb_context = get_context(user_id)
        >>> personality = get_agent_personality(user_id)
        >>> prompt = build_system_prompt_with_personality(kb_context, personality)
    """
    # Format personality section
    personality_context = format_personality_context(personality)
    
    # Combine all sections
    prompt_parts = [
        personality_context,
        knowledge_base_context,
        "",
        "=== INSTRUÇÕES ===",
        "Você é o assistente virtual configurado acima. Use APENAS as informações fornecidas na base de conhecimento para responder.",
        "Se não souber a resposta, seja honesto e ofereça ajuda para entrar em contato com um humano.",
        "Mantenha a personalidade e tom de voz especificados.",
        "Responda sempre em português brasileiro.",
        "",
        "=== REGRAS IMPORTANTES SOBRE O FLUXO DE CONVERSA ===",
        "⚠️ CRÍTICO - LEIA COM ATENÇÃO:",
        "",
        "1. RESPEITE O SISTEMA DE PERGUNTAS E RESPOSTAS:",
        "   - Faça UMA pergunta por vez",
        "   - Aguarde a resposta do usuário antes de fazer nova pergunta",
        "   - NÃO envie múltiplas mensagens consecutivas",
        "   - Se o usuário responder com múltiplas informações, processe uma de cada vez",
        "",
        "2. USO DO NOME DO CONTATO:",
        "   - Sempre que disponível, use o nome do contato para personalizar a conversa",
        "   - Exemplo: 'Olá, {{contact_name}}! Como posso ajudar?'",
        "   - Use o nome de forma natural, sem exageros",
        "",
        "3. FORMATO DE RESPOSTA:",
        "   - Mantenha respostas concisas e objetivas",
        "   - Use no máximo 2-3 parágrafos por mensagem",
        "   - Se precisar coletar múltiplas informações, faça em etapas separadas",
        "",
        "4. EXEMPLO DE FLUXO CORRETO:",
        "   ✅ CORRETO:",
        "   Agente: 'Qual tipo de produto você busca?'",
        "   [AGUARDA RESPOSTA]",
        "   Usuário: 'Busco um shampoo'",
        "   Agente: 'Ótimo! Para qual tipo de cabelo?'",
        "   [AGUARDA RESPOSTA]",
        "   ",
        "   ❌ INCORRETO (NÃO FAÇA ISSO):",
        "   Agente: 'Qual tipo de produto você busca?'",
        "   Agente: 'Temos várias opções disponíveis!'",
        "   Agente: 'Posso te ajudar a escolher?'",
        "",
        "5. TRATAMENTO DE CONTEXTO:",
        "   - Use o histórico da conversa para manter contexto",
        "   - Se o usuário mudar de assunto, adapte-se mas continue respeitando o fluxo",
        "   - Uma mensagem por interação é a regra de ouro",
        "",
        "=== FORMATAÇÃO DE RESPOSTAS ===",
        "Ao apresentar produtos ou planos:",
        "1. Use quebras de linha para separar seções",
        "2. Use negrito (*texto*) para destacar nomes de planos e preços principais",
        "3. Liste benefícios com marcadores (• ou -) um por linha",
        "4. Agrupe informações relacionadas",
        "5. Evite parágrafos longos - prefira listas e tópicos",
        "6. Para múltiplos planos, apresente um de cada vez com espaçamento claro",
        "7. Use emojis com moderação para melhorar a visualização (💰 para preços, ✨ para destaques, 👥 para público-alvo)",
        "",
        "✅ BOM - Exemplo de formatação clara:",
        "*Plano Essencial*",
        "💰 R$ 260/mês ou R$ 2.600/ano (2 meses grátis)",
        "",
        "O que está incluído:",
        "• Atendimento com IA",
        "• Base de conhecimento personalizada",
        "• Integração WhatsApp",
        "",
        "👥 Ideal para: Pequenos negócios",
        "",
        "❌ EVITE - Formatação confusa:",
        "Plano Essencial: Preço mensal: R$ 260 Preço anual: R$ 2600 (2 meses grátis) Benefícios: Atendimento com IA por mensagens...",
    ]
    
    return "\n".join(prompt_parts)
