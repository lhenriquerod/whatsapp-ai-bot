"""
Script para testar produto com múltiplos planos de assinatura
"""
from src.services.supabase_service import _client, get_context

# User ID válido
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 70)
print("Inserindo produto RAG-E com múltiplos planos")
print("=" * 70)

# Produto RAG-E com estrutura completa de planos
produto_rage = {
    "user_id": USER_ID,
    "categoria": "produto",
    "dados": {
        "nome": "RAG-E",
        "tipo_produto": "assinatura_multiplos_planos",
        "descricao": "Plataforma de atendimento inteligente com IA para automatizar conversas via WhatsApp e web",
        "categoria": "Software",
        "planos": [
            {
                "nome": "Essencial",
                "preco_mensal": "260",
                "preco_anual": "2600",
                "desconto_anual": "2 meses Grátis",
                "beneficios": [
                    "Atendimento com IA por mensagens de texto (WhatsApp + painel web)",
                    "Respostas baseadas na base de conhecimento cadastrada pelo cliente",
                    "Cadastro e organização de conteúdos (produtos, serviços, FAQs, empresas, etc.)",
                    "Configuração da personalidade e estilo de resposta do assistente"
                ],
                "limite_usuarios": "5 usuários",
                "limite_conversas": "1000 conversas/mês",
                "ideal_para": "Pequenos negócios e startups"
            },
            {
                "nome": "Profissional",
                "preco_mensal": "520",
                "preco_anual": "5200",
                "desconto_anual": "2 meses Grátis",
                "beneficios": [
                    "Todos os benefícios do plano Essencial",
                    "Integração com múltiplos canais (WhatsApp Business API)",
                    "Relatórios e análises de atendimento",
                    "Suporte prioritário",
                    "Personalização avançada do agente"
                ],
                "limite_usuarios": "15 usuários",
                "limite_conversas": "5000 conversas/mês",
                "ideal_para": "Médias empresas em crescimento"
            },
            {
                "nome": "Enterprise",
                "preco_mensal": "1200",
                "preco_anual": "12000",
                "desconto_anual": "2 meses Grátis + Onboarding dedicado",
                "beneficios": [
                    "Todos os benefícios do plano Profissional",
                    "Usuários e conversas ilimitados",
                    "Integração com CRM e ferramentas empresariais",
                    "API dedicada para integrações customizadas",
                    "Gerente de conta dedicado",
                    "SLA garantido de 99,9%"
                ],
                "limite_usuarios": "Ilimitado",
                "limite_conversas": "Ilimitado",
                "ideal_para": "Grandes empresas e corporações"
            }
        ]
    }
}

# FAQ relacionado
faq_preco = {
    "user_id": USER_ID,
    "categoria": "faq",
    "dados": {
        "pergunta": "Como funciona a cobrança anual?",
        "resposta": "No pagamento anual você ganha 2 meses grátis, pagando apenas 10 meses. O valor é cobrado à vista no início do período."
    }
}

faq_upgrade = {
    "user_id": USER_ID,
    "categoria": "faq",
    "dados": {
        "pergunta": "Posso fazer upgrade do plano depois?",
        "resposta": "Sim! Você pode fazer upgrade a qualquer momento. O valor será ajustado proporcionalmente ao tempo restante do seu período de cobrança."
    }
}

# Info da empresa
info_suporte = {
    "user_id": USER_ID,
    "categoria": "empresa",
    "dados": {
        "topico": "Suporte e Atendimento",
        "conteudo": "Nossa equipe de suporte está disponível de segunda a sexta, das 9h às 18h. Clientes Enterprise têm suporte 24/7."
    }
}

try:
    # Limpar registros antigos
    print("\n1. Limpando registros antigos...")
    _client.table("base_conhecimento").delete().eq("user_id", USER_ID).execute()
    print("✅ Registros removidos")
    
    # Inserir novo conteúdo
    print("\n2. Inserindo novo conteúdo...")
    
    items = [
        ("Produto RAG-E", produto_rage),
        ("FAQ - Cobrança anual", faq_preco),
        ("FAQ - Upgrade", faq_upgrade),
        ("Info - Suporte", info_suporte)
    ]
    
    for nome, item in items:
        result = _client.table("base_conhecimento").insert(item).execute()
        if result.data:
            print(f"✅ {nome}")
    
    print(f"\n✅ {len(items)} itens inseridos!")
    
    # Testar get_context()
    print("\n" + "=" * 70)
    print("Testando get_context() com produto de múltiplos planos")
    print("=" * 70)
    
    context = get_context(owner_id=USER_ID)
    
    print("\n📋 CONTEXTO FORMATADO:")
    print("=" * 70)
    print(context)
    print("=" * 70)
    
    # Estatísticas
    linhas = context.split("\n")
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de linhas: {len(linhas)}")
    print(f"   - Tamanho: {len(context)} caracteres")
    print(f"   - Planos encontrados: {context.count('Plano ')}")
    print(f"   - FAQs encontrados: {context.count('FAQ:')}")
    
    print("\n✅ Teste concluído com sucesso!")
    print("\nAgora teste via API:")
    print('  python test_simulation_endpoint.py')
    print('  Ou: curl -X POST http://localhost:8000/simulation/chat \\')
    print('       -H "Content-Type: application/json" \\')
    print(f'       -d \'{{"user_id": "{USER_ID}", "message": "Quais planos?"}}\'')
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
