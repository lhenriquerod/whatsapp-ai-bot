"""
Chunking Service
Splits text into overlapping chunks for vector embeddings.
"""
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def split_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Tries to break at sentence boundaries for better semantic coherence.
    
    Args:
        text: Full text to split
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Overlap between chunks to maintain context
    
    Returns:
        List of text chunks
        
    Example:
        >>> text = "First sentence. Second sentence. Third sentence."
        >>> chunks = split_into_chunks(text, chunk_size=30, chunk_overlap=10)
        >>> len(chunks)
        2
    """
    if not text or not text.strip():
        return []
    
    text = text.strip()
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If not at the end, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings: ". ", ".\n", "! ", "? "
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('.\n', start, end),
                text.rfind('! ', start, end),
                text.rfind('? ', start, end)
            )
            
            if sentence_end > start:
                end = sentence_end + 1  # Include the period
        
        chunk = text[start:end].strip()
        
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - chunk_overlap
        
        # Prevent infinite loop - if we've already passed the end
        if end >= len(text):
            break
    
    logger.debug(f"Split text ({len(text)} chars) into {len(chunks)} chunks")
    
    return chunks


def prepare_knowledge_for_chunking(knowledge_entry: Dict[str, Any]) -> str:
    """
    Prepare a knowledge_base entry for chunking.
    Combines relevant fields into a single formatted text.
    
    Args:
        knowledge_entry: Dict with fields from knowledge_base table:
            {
                "category": "product",
                "data": {
                    "nome": "RAG-E",
                    "descricao": "...",
                    ...
                }
            }
    
    Returns:
        Formatted text ready for chunking
        
    Example:
        >>> entry = {
        ...     "category": "product",
        ...     "data": {
        ...         "nome": "Essential Plan",
        ...         "descricao": "Perfect for small teams",
        ...         "preco": "R$ 99/mês"
        ...     }
        ... }
        >>> text = prepare_knowledge_for_chunking(entry)
        >>> "Essential Plan" in text
        True
    """
    parts = []
    
    category = knowledge_entry.get("category", "").lower()
    data = knowledge_entry.get("data", {})
    
    if not isinstance(data, dict):
        # If data is not a dict, just stringify it
        return str(data)
    
    # Add category label
    if category:
        parts.append(f"Categoria: {category.upper()}")
    
    # Format based on category
    if category == "product":
        if data.get("nome"):
            parts.append(f"Produto: {data['nome']}")
        
        if data.get("descricao"):
            parts.append(f"Descrição: {data['descricao']}")
        
        if data.get("tipo_produto"):
            parts.append(f"Tipo: {data['tipo_produto']}")
        
        # Include pricing info
        if data.get("preco"):
            parts.append(f"Preço: {data['preco']}")
        elif data.get("preco_mensal"):
            parts.append(f"Preço mensal: R$ {data['preco_mensal']}")
        
        if data.get("periodo_trial"):
            parts.append(f"Período de teste grátis: {data['periodo_trial']} dias")
        
        if data.get("formas_pagamento"):
            parts.append(f"Formas de pagamento: {data['formas_pagamento']}")
        
        # Include plans if multiple
        if data.get("planos") and isinstance(data["planos"], list):
            parts.append("Planos disponíveis:")
            for plano in data["planos"]:
                plano_parts = []
                if plano.get("nome"):
                    plano_parts.append(f"- {plano['nome']}")
                if plano.get("preco_mensal"):
                    plano_parts.append(f"R$ {plano['preco_mensal']}/mês")
                if plano.get("beneficios"):
                    plano_parts.append(f"Benefícios: {', '.join(plano['beneficios'])}")
                parts.append(" ".join(plano_parts))
    
    elif category == "faq":
        if data.get("pergunta"):
            parts.append(f"Pergunta: {data['pergunta']}")
        
        if data.get("resposta"):
            parts.append(f"Resposta: {data['resposta']}")
    
    elif category == "company":
        titulo = data.get("titulo") or data.get("topico")
        conteudo = data.get("descricao") or data.get("conteudo")
        
        if titulo:
            parts.append(f"Assunto: {titulo}")
        
        if conteudo:
            parts.append(conteudo)
    
    elif category == "service":
        if data.get("nome"):
            parts.append(f"Serviço: {data['nome']}")
        
        if data.get("descricao"):
            parts.append(f"Descrição: {data['descricao']}")
        
        if data.get("preco"):
            parts.append(f"Preço: {data['preco']}")
        
        if data.get("duracao"):
            parts.append(f"Duração: {data['duracao']}")
    
    else:
        # Generic handling for custom or unknown categories
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                parts.append(f"{key}: {', '.join(str(v) for v in value)}")
    
    result = "\n\n".join(parts)
    
    logger.debug(f"Prepared knowledge entry (category: {category}, length: {len(result)})")
    
    return result if result else "Sem conteúdo disponível"
