"""
Test script for Agent Personality Integration
Tests the complete flow: personality config + knowledge base → AI context
"""
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.supabase_service import _client
from src.services.personality_service import (
    get_agent_personality,
    format_personality_context,
    build_system_prompt_with_personality
)
from src.services.supabase_service import get_context

# User ID for testing (replace with your actual user_id from auth.users)
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 70)
print("Test: Agent Personality Integration")
print("=" * 70)
print()

# =====================================================================
# STEP 1: Clean up old data
# =====================================================================
print("1. Limpando dados antigos...")

try:
    # Delete old personality
    _client.table("agent_personality").delete().eq("user_id", USER_ID).execute()
    
    # Delete old knowledge base
    _client.table("knowledge_base").delete().eq("user_id", USER_ID).execute()
    
    print("✅ Dados removidos")
except Exception as e:
    print(f"⚠️  Erro ao limpar dados: {e}")

print()

# =====================================================================
# STEP 2: Insert personality configuration
# =====================================================================
print("2. Inserindo configuração de personalidade...")

personality_data = {
    "user_id": USER_ID,
    "name": "RAG-E Assistant",
    "personality_level": 7,  # Casual
    "voice_tone": "friendly",
    "address_form": "you_informal",
    "initial_message": "Oi! Sou o RAG-E, seu assistente inteligente. Como posso te ajudar hoje? 😊"
}

try:
    result = _client.table("agent_personality").insert(personality_data).execute()
    print("✅ Personalidade inserida")
    print(f"   - Nome: {personality_data['nome']}")
    print(f"   - Nível: {personality_data['nivel_personalidade']} (Casual)")
    print(f"   - Tom: {personality_data['tom_voz']}")
    print(f"   - Tratamento: {personality_data['forma_tratamento']}")
except Exception as e:
    print(f"❌ Erro ao inserir personalidade: {e}")
    sys.exit(1)

print()

# =====================================================================
# STEP 3: Insert knowledge base items
# =====================================================================
print("3. Inserindo itens na base de conhecimento...")

knowledge_items = [
    # Product with multiple plans
    {
        "user_id": USER_ID,
        "category": "product",
        "data": {
            "name": "RAG-E",
            "tipo_produto": "assinatura_multiplos_planos",
            "descricao": "Plataforma de atendimento inteligente com IA para automatizar conversations via WhatsApp e web",
            "category": "Software",
            "planos": [
                {
                    "name": "Essencial",
                    "preco_mensal": "260",
                    "preco_anual": "2600",
                    "desconto_anual": "2 meses Grátis",
                    "beneficios": [
                        "Atendimento com IA por messages de texto",
                        "Base de conhecimento personalizada",
                        "Integração WhatsApp",
                        "Painel web completo"
                    ],
                    "limite_usuarios": "5 usuários",
                    "limite_conversations": "1000 conversations/mês",
                    "ideal_para": "Pequenos negócios"
                },
                {
                    "name": "Profissional",
                    "preco_mensal": "520",
                    "preco_anual": "5200",
                    "desconto_anual": "2 meses Grátis",
                    "beneficios": [
                        "Todos os recursos do Essencial",
                        "Múltiplos canais de atendimento",
                        "Relatórios avançados",
                        "Suporte prioritário"
                    ],
                    "limite_usuarios": "15 usuários",
                    "limite_conversations": "5000 conversations/mês",
                    "ideal_para": "Médias empresas"
                }
            ]
        }
    },
    # FAQ
    {
        "user_id": USER_ID,
        "category": "faq",
        "data": {
            "pergunta": "Qual o horário de atendimento?",
            "resposta": "Nosso time está disponível de segunda a sexta, das 9h às 18h. Fora desse horário, o assistente virtual continua funcionando 24/7!",
            "categoria_faq": "Atendimento"
        }
    },
    # Company info
    {
        "user_id": USER_ID,
        "category": "company",
        "data": {
            "type": "Sobre a empresa",
            "title": "Nossa Missão",
            "descricao": "Revolucionar o atendimento ao cliente através de IA acessível e personalizada",
            "informacoes_adicionais": "Fundada em 2025, já atendemos mais de 100 empresas"
        }
    }
]

try:
    result = _client.table("knowledge_base").insert(knowledge_items).execute()
    print(f"✅ {len(knowledge_items)} itens inseridos")
    print("   - 1 produto (RAG-E com 2 planos)")
    print("   - 1 FAQ (horário de atendimento)")
    print("   - 1 informação da empresa")
except Exception as e:
    print(f"❌ Erro ao inserir base de conhecimento: {e}")
    sys.exit(1)

print()

# =====================================================================
# STEP 4: Test get_agent_personality()
# =====================================================================
print("=" * 70)
print("4. Testando get_agent_personality()")
print("=" * 70)
print()

personality = get_agent_personality(USER_ID)

print("📋 Personalidade recuperada:")
print(f"   Nome: {personality['nome']}")
print(f"   Nível: {personality['nivel_personalidade']}")
print(f"   Tom de voz: {personality['tom_voz']}")
print(f"   Tratamento: {personality['forma_tratamento']}")
print(f"   Apresentação: {personality['apresentacao_inicial']}")
print()

# =====================================================================
# STEP 5: Test format_personality_context()
# =====================================================================
print("=" * 70)
print("5. Testando format_personality_context()")
print("=" * 70)
print()

personality_context = format_personality_context(personality)
print("📄 Contexto de personalidade formatado:")
print("-" * 70)
print(personality_context)
print("-" * 70)
print()

# =====================================================================
# STEP 6: Test get_context() (knowledge base)
# =====================================================================
print("=" * 70)
print("6. Testando get_context() - Base de conhecimento")
print("=" * 70)
print()

kb_context = get_context(USER_ID)
print("📚 Base de conhecimento formatada:")
print("-" * 70)
print(kb_context)
print("-" * 70)
print()

# =====================================================================
# STEP 7: Test complete system prompt
# =====================================================================
print("=" * 70)
print("7. Testando build_system_prompt_with_personality()")
print("=" * 70)
print()

complete_prompt = build_system_prompt_with_personality(kb_context, personality)

print("🤖 SYSTEM PROMPT COMPLETO:")
print("=" * 70)
print(complete_prompt)
print("=" * 70)
print()

# =====================================================================
# STEP 8: Statistics and summary
# =====================================================================
print("=" * 70)
print("📊 Estatísticas do prompt gerado")
print("=" * 70)
print(f"   - Total de linhas: {len(complete_prompt.split(chr(10)))}")
print(f"   - Total de caracteres: {len(complete_prompt)}")
print(f"   - Planos de produto: 2")
print(f"   - FAQs: 1")
print(f"   - Informações da empresa: 1")
print()

# =====================================================================
# STEP 9: Test with non-existent user (fallback to defaults)
# =====================================================================
print("=" * 70)
print("8. Testando fallback com usuário inexistente")
print("=" * 70)
print()

fake_user_id = "00000000-0000-0000-0000-000000000000"
default_personality = get_agent_personality(fake_user_id)

print("📋 Personalidade padrão (fallback):")
print(f"   Nome: {default_personality['nome']}")
print(f"   Nível: {default_personality['nivel_personalidade']}")
print(f"   Tom de voz: {default_personality['tom_voz']}")
print()

# =====================================================================
# SUCCESS
# =====================================================================
print("=" * 70)
print("✅ TESTE CONCLUÍDO COM SUCESSO!")
print("=" * 70)
print()
print("Próximos passos:")
print("  1. Inicie o servidor: uvicorn app:app --reload")
print("  2. Teste via API:")
print()
print("     curl -X POST http://localhost:8000/simulation/chat \\")
print(f"       -H 'Content-Type: application/json' \\")
print(f"       -d '{{\"user_id\": \"{USER_ID}\", \"message\": \"Quais planos vocês oferecem?\"}}'")
print()
print("  3. Experimente diferentes messages:")
print("     - 'Qual o horário de atendimento?'")
print("     - 'Qual a diferença entre os planos?'")
print("     - 'Me fale sobre a empresa'")
print()
print("=" * 70)
