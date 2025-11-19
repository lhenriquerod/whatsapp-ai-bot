"""
Supabase Service
Provides interface to fetch knowledge base context from Supabase.

This service queries the 'knowledge_base' table which stores knowledge items
in a flexible JSONB structure organized by categories:
- product: Products with name, description, price, characteristics
- service: Services with name, description, duration, price
- company: Company info with topic and content
- faq: Frequently asked questions with question/answer pairs
- custom: Custom knowledge items with flexible fields

The get_context() function formats these items into a readable string
that is injected into the AI's system prompt for contextual responses.
"""
import logging
from typing import List, Dict, Any

from supabase import create_client, Client
from src.utils.config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    KB_TABLE,
    KB_OWNER_COL,
    KB_FIELDS,
    KB_LIMIT
)

logger = logging.getLogger(__name__)

# Initialize Supabase client (singleton)
_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_context(owner_id: str, fields: str = KB_FIELDS, limit: int = KB_LIMIT) -> str:
    """
    Fetch knowledge base context for a specific owner from Supabase.
    
    Queries the knowledge_base table for all active knowledge entries
    belonging to the specified user and formats them into a readable context string.
    
    Args:
        owner_id: User/owner identifier to filter knowledge base (user_id in knowledge_base)
        fields: Comma-separated field names to retrieve (default: from config)
        limit: Maximum number of records to fetch (default: from config)
        
    Returns:
        Formatted context string with knowledge items, or default message if empty
        
    Example:
        >>> get_context("6bf0dab0-e895-4730-b5fa-cd8acff6de0c")
        "Knowledge Base:\\n\\n- FAQ: Question: What time? | Answer: 9am to 6pm\\n\\n- Product: Item X | Description: ... | Price: R$ 50"
    """
    try:
        logger.debug("Fetching knowledge base for owner_id=%s", owner_id[-4:] if len(owner_id) > 4 else "***")
        
        # Query Supabase table filtered by user_id
        query = _client.table(KB_TABLE).select(fields).eq(KB_OWNER_COL, owner_id)
        
        # If 'ativo' field exists, filter only active entries (future-proofing)
        # For now, we fetch all entries since 'ativo' field doesn't exist yet
        
        response = query.limit(limit).execute()
        
        rows: List[Dict[str, Any]] = response.data or []
        
        if not rows:
            logger.info("No knowledge base entries found for owner=%s", owner_id[-4:] if len(owner_id) > 4 else "***")
            return "Nenhuma base de conhecimento cadastrada para este usuário."
        
        # Format rows into readable context
        def format_row(row: Dict[str, Any]) -> str:
            """
            Format a single row from knowledge_base into readable text.
            Handles JSONB 'data' field based on 'category'.
            
            Supports multiple product types including products with pricing plans.
            """
            category = row.get("category", "").lower()
            data = row.get("data", {})
            
            # If data is not a dict (edge case), return raw
            if not isinstance(data, dict):
                return f"{category.capitalize()}: {str(data)}"
            
            # Format based on category
            if category == "product":
                return format_produto(data)
            
            elif category == "service":
                return format_servico(data)
            
            elif category == "company":
                return format_empresa(data)
            
            elif category == "faq":
                return format_faq(data)
            
            elif category == "custom":
                return format_personalizado(data)
            
            else:
                # Unknown category - just stringify the data
                return f"{category.capitalize()}: {str(data)}"
        
        def format_produto(dados: Dict[str, Any]) -> str:
            """Format product data, including products with multiple pricing plans."""
            lines = []
            
            # Header
            nome = dados.get("nome", "Produto sem nome")
            lines.append(f"PRODUTO: {nome}")
            
            # Basic info - Include ALL top-level fields
            if dados.get("categoria_produto"):
                lines.append(f"Categoria: {dados['categoria_produto']}")
            elif dados.get("categoria"):
                lines.append(f"Categoria: {dados['categoria']}")
            
            if dados.get("tipo_produto"):
                tipo = dados['tipo_produto']
                tipo_label = {
                    "produto_unico": "Produto Único",
                    "assinatura_plano_unico": "Assinatura (Plano Único)",
                    "assinatura_multiplos_planos": "Assinatura (Múltiplos Planos)",
                    "pacote_combo": "Pacote/Combo",
                    "sob_consulta": "Sob Consulta"
                }.get(tipo, tipo)
                lines.append(f"Tipo: {tipo_label}")
            
            if dados.get("descricao"):
                lines.append(f"Descrição: {dados['descricao']}")
            
            # IMPORTANT: Include trial period if exists
            if dados.get("periodo_trial"):
                trial = dados['periodo_trial']
                lines.append(f"Período de teste grátis: {trial} dias")
            
            # IMPORTANT: Include payment methods if exists
            if dados.get("formas_pagamento"):
                lines.append(f"Formas de pagamento: {dados['formas_pagamento']}")
            
            # Include any other top-level fields that are simple values
            # Skip known complex fields (planos, beneficios, etc.) as they're handled below
            skip_fields = {
                "nome", "categoria", "categoria_produto", "tipo_produto", "descricao",
                "periodo_trial", "formas_pagamento", "planos", "beneficios",
                "preco_mensal", "preco_anual", "desconto_anual", "preco",
                "caracteristicas", "itens_inclusos", "limite_usuarios", "limite_conversas", "ideal_para"
            }
            
            for key, value in dados.items():
                if key not in skip_fields and value and isinstance(value, (str, int, float, bool)):
                    # Format key (convert snake_case to Title Case)
                    formatted_key = key.replace('_', ' ').title()
                    lines.append(f"{formatted_key}: {value}")
            
            # Handle different pricing structures
            tipo_produto = dados.get("tipo_produto", "")
            
            if tipo_produto == "assinatura_multiplos_planos" and dados.get("planos"):
                # Multiple pricing plans
                lines.append("")
                lines.append("Planos disponíveis:")
                lines.append("")
                
                for plano in dados["planos"]:
                    lines.append(f"Plano {plano.get('nome', 'Sem nome')}:")
                    
                    if plano.get("preco_mensal"):
                        lines.append(f"  Preço mensal: R$ {plano['preco_mensal']}")
                    
                    if plano.get("preco_anual"):
                        desconto = f" ({plano['desconto_anual']})" if plano.get("desconto_anual") else ""
                        lines.append(f"  Preço anual: R$ {plano['preco_anual']}{desconto}")
                    
                    if plano.get("beneficios") and isinstance(plano["beneficios"], list):
                        lines.append("  Benefícios:")
                        for beneficio in plano["beneficios"]:
                            lines.append(f"    • {beneficio}")
                    
                    if plano.get("limite_usuarios"):
                        lines.append(f"  Limite de usuários: {plano['limite_usuarios']}")
                    
                    if plano.get("limite_conversas"):
                        lines.append(f"  Limite de conversas: {plano['limite_conversas']}")
                    
                    if plano.get("ideal_para"):
                        lines.append(f"  Ideal para: {plano['ideal_para']}")
                    
                    # Include any other plan-specific fields
                    plan_skip_fields = {
                        "nome", "preco_mensal", "preco_anual", "desconto_anual",
                        "beneficios", "limite_usuarios", "limite_conversas", "ideal_para"
                    }
                    for key, value in plano.items():
                        if key not in plan_skip_fields and value and isinstance(value, (str, int, float, bool)):
                            formatted_key = key.replace('_', ' ').title()
                            lines.append(f"  {formatted_key}: {value}")
                    
                    lines.append("")  # Blank line between plans
            
            elif tipo_produto == "assinatura_plano_unico":
                # Single subscription plan
                if dados.get("preco_mensal"):
                    lines.append(f"Preço mensal: R$ {dados['preco_mensal']}")
                
                if dados.get("preco_anual"):
                    desconto = f" ({dados['desconto_anual']})" if dados.get("desconto_anual") else ""
                    lines.append(f"Preço anual: R$ {dados['preco_anual']}{desconto}")
                
                if dados.get("beneficios") and isinstance(dados["beneficios"], list):
                    lines.append("Benefícios:")
                    for beneficio in dados["beneficios"]:
                        lines.append(f"  • {beneficio}")
            
            elif tipo_produto == "produto_unico":
                # Single product with simple pricing
                if dados.get("preco"):
                    lines.append(f"Preço: R$ {dados['preco']}")
                
                if dados.get("caracteristicas"):
                    if isinstance(dados["caracteristicas"], list):
                        lines.append("Características:")
                        for carac in dados["caracteristicas"]:
                            lines.append(f"  • {carac}")
                    else:
                        lines.append(f"Características: {dados['caracteristicas']}")
            
            elif tipo_produto == "pacote_combo":
                # Package/combo
                if dados.get("preco"):
                    lines.append(f"Preço do pacote: R$ {dados['preco']}")
                
                if dados.get("itens_inclusos") and isinstance(dados["itens_inclusos"], list):
                    lines.append("Itens inclusos:")
                    for item in dados["itens_inclusos"]:
                        lines.append(f"  • {item}")
            
            elif tipo_produto == "sob_consulta":
                lines.append("Preço: Sob consulta")
            
            else:
                # Fallback for old structure or unknown type
                if dados.get("preco"):
                    lines.append(f"Preço: {dados['preco']}")
                
                if dados.get("caracteristicas"):
                    lines.append(f"Características: {dados['caracteristicas']}")
            
            return "\n".join(lines)
        
        def format_servico(dados: Dict[str, Any]) -> str:
            """Format service data."""
            lines = []
            
            if dados.get("nome"):
                lines.append(f"SERVIÇO: {dados['nome']}")
            
            if dados.get("descricao"):
                lines.append(f"Descrição: {dados['descricao']}")
            
            if dados.get("duracao"):
                lines.append(f"Duração: {dados['duracao']}")
            
            if dados.get("preco"):
                lines.append(f"Preço: {dados['preco']}")
            
            if dados.get("beneficios") and isinstance(dados["beneficios"], list):
                lines.append("Benefícios:")
                for beneficio in dados["beneficios"]:
                    lines.append(f"  • {beneficio}")
            
            return "\n".join(lines) if lines else f"Serviço: {str(dados)}"
        
        def format_empresa(dados: Dict[str, Any]) -> str:
            """Format company/business info."""
            lines = []
            
            # Support both old and new field names
            titulo = dados.get("titulo") or dados.get("topico")
            conteudo = dados.get("descricao") or dados.get("conteudo")
            
            if titulo:
                lines.append(f"INFORMAÇÃO: {titulo}")
            
            if conteudo:
                lines.append(conteudo)
            
            if dados.get("informacoes_adicionais"):
                lines.append(dados["informacoes_adicionais"])
            
            return "\n".join(lines) if lines else f"Empresa: {str(dados)}"
        
        def format_faq(dados: Dict[str, Any]) -> str:
            """Format FAQ entry."""
            lines = []
            
            if dados.get("pergunta"):
                lines.append(f"FAQ: {dados['pergunta']}")
            
            if dados.get("resposta"):
                lines.append(f"Resposta: {dados['resposta']}")
            
            return "\n".join(lines) if lines else f"FAQ: {str(dados)}"
        
        def format_personalizado(dados: Dict[str, Any]) -> str:
            """Format custom knowledge entries."""
            lines = []
            
            # Try to find a title/header field
            titulo = dados.get("titulo") or dados.get("nome") or dados.get("topico")
            if titulo:
                lines.append(f"INFORMAÇÃO: {titulo}")
            
            # Add other fields
            for key, value in dados.items():
                if key not in ["titulo", "nome", "topico"] and value:
                    if isinstance(value, list):
                        lines.append(f"{key.capitalize()}:")
                        for item in value:
                            lines.append(f"  • {item}")
                    else:
                        lines.append(f"{key.capitalize()}: {value}")
            
            return "\n".join(lines) if lines else f"Personalizado: {str(dados)}"
        
        # Build context with header
        context_lines = ["=== BASE DE CONHECIMENTO ===", ""]
        
        for row in rows:
            formatted = format_row(row)
            context_lines.append(formatted)
            context_lines.append("")  # Blank line between entries
        
        context = "\n".join(context_lines)
        
        logger.info("Retrieved %d KB entries for owner=%s", len(rows), owner_id[-4:] if len(owner_id) > 4 else "***")
        
        return context
        
    except Exception as e:
        logger.exception("Failed to fetch context from Supabase for owner=%s: %s", 
                        owner_id[-4:] if len(owner_id) > 4 else "***", e)
        return "Nenhuma base de conhecimento cadastrada para este usuário."
