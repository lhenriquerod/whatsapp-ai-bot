"""
Agent Personality Service
Handles fetching and formatting agent personality configuration from Supabase.
"""
import logging
from typing import Optional, Dict, Any

from src.services.supabase_service import _client

logger = logging.getLogger(__name__)

# Personality level mapping
NIVEIS_PERSONALIDADE = {
    1: "Extremamente formal",
    2: "Formal",
    3: "Levemente formal",
    4: "Equilibrado tendendo ao formal",
    5: "Equilibrado (profissional e amigável)",
    6: "Equilibrado tendendo ao casual",
    7: "Casual",
    8: "Animado e entusiasmado",
    9: "Muito entusiasmado",
    10: "Técnico e especialista"
}

# Voice tone instructions
TOM_VOZ_INSTRUCOES = {
    "formal": "Use linguagem formal, evite gírias e contrações",
    "amigavel": "Use tom conversacional, seja caloroso e acessível",
    "objetivo": "Seja direto e conciso, foque nos fatos",
    "descontraido": "Use linguagem casual, gírias são bem-vindas"
}

# Treatment form instructions
FORMA_TRATAMENTO_INSTRUCOES = {
    "voce": "Trate o cliente por 'você'",
    "senhor": "Trate o cliente por 'senhor' ou 'senhora'",
    "informal": "Use tratamento informal como 'tu' se apropriado"
}

# Default personality fallback
DEFAULT_PERSONALITY = {
    "nome": "Assistente Virtual",
    "nivel_personalidade": 5,
    "tom_voz": "amigavel",
    "forma_tratamento": "voce",
    "apresentacao_inicial": "Olá! Como posso ajudar?"
}


def get_agent_personality(user_id: str) -> Dict[str, Any]:
    """
    Fetch agent personality configuration from personalidade_agente table.
    
    Args:
        user_id: User UUID
        
    Returns:
        Dictionary with personality configuration. Returns default values if not found.
        
    Keys returned:
        - nome: Agent name
        - nivel_personalidade: Personality level (1-10)
        - tom_voz: Voice tone (formal|amigavel|objetivo|descontraido)
        - forma_tratamento: Treatment form (voce|senhor|informal)
        - apresentacao_inicial: Initial greeting message
        
    Example:
        >>> personality = get_agent_personality("uuid-here")
        >>> print(personality["nome"])
        "RAG-E Assistant"
    """
    try:
        result = _client.table("personalidade_agente") \
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
    
    lines.append("=== PERSONALIDADE DO AGENTE ===")
    lines.append(f"Nome: {personality.get('nome', 'Assistente Virtual')}")
    
    # Personality level with description
    nivel = personality.get("nivel_personalidade", 5)
    nivel_desc = NIVEIS_PERSONALIDADE.get(nivel, "Equilibrado")
    lines.append(f"Nível de Personalidade: {nivel} ({nivel_desc})")
    
    lines.append(f"Tom de Voz: {personality.get('tom_voz', 'amigavel')}")
    lines.append(f"Forma de Tratamento: {personality.get('forma_tratamento', 'voce')}")
    
    # Initial greeting
    apresentacao = personality.get("apresentacao_inicial", "Olá! Como posso ajudar?")
    lines.append(f"Mensagem Inicial: \"{apresentacao}\"")
    lines.append("")
    
    # Behavioral instructions
    lines.append("Instruções de comportamento:")
    
    tom_voz = personality.get("tom_voz", "amigavel")
    if tom_voz in TOM_VOZ_INSTRUCOES:
        lines.append(f"- {TOM_VOZ_INSTRUCOES[tom_voz]}")
    
    forma_tratamento = personality.get("forma_tratamento", "voce")
    if forma_tratamento in FORMA_TRATAMENTO_INSTRUCOES:
        lines.append(f"- {FORMA_TRATAMENTO_INSTRUCOES[forma_tratamento]}")
    
    # Add personality-level specific instructions
    if nivel <= 3:
        lines.append("- Mantenha extrema formalidade e distância profissional")
    elif nivel >= 8:
        lines.append("- Demonstre entusiasmo e energia nas respostas")
        lines.append("- Use emojis quando apropriado para transmitir emoção")
    
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
