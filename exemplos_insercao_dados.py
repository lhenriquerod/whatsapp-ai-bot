"""
Exemplos práticos de inserção de dados de personalidade e base de conhecimento
Execute este script para popular seu banco de dados com exemplos variados
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================
# Substitua pelo seu user_id real do Supabase auth.users
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 70)
print("Exemplos de Inserção de Dados - RAG-E")
print("=" * 70)
print()
print(f"User ID: {USER_ID}")
print()

# =====================================================================
# EXEMPLO 1: Personalidade Formal (Banco/Jurídico)
# =====================================================================
print("1. Personalidade FORMAL (Banco/Jurídico)")
print("-" * 70)

personalidade_formal = {
    "user_id": USER_ID,
    "nome": "Dr. Assistente Juridico",
    "nivel_personalidade": 2,  # Formal
    "tom_voz": "formal",
    "forma_tratamento": "senhor",
    "apresentacao_inicial": "Bom dia. Como posso auxiliá-lo?"
}

print(f"Nome: {personalidade_formal['nome']}")
print(f"Nivel: {personalidade_formal['nivel_personalidade']} (Formal)")
print(f"Tom: {personalidade_formal['tom_voz']}")
print(f"Tratamento: {personalidade_formal['forma_tratamento']}")
print()

# =====================================================================
# EXEMPLO 2: Personalidade Amigável (E-commerce/Loja)
# =====================================================================
print("2. Personalidade AMIGÁVEL (E-commerce/Loja)")
print("-" * 70)

personalidade_amigavel = {
    "user_id": USER_ID,
    "nome": "Luna",
    "nivel_personalidade": 6,  # Equilibrado tendendo ao casual
    "tom_voz": "amigavel",
    "forma_tratamento": "voce",
    "apresentacao_inicial": "Oi! Que bom te ver por aqui! Como posso ajudar hoje? 😊"
}

print(f"Nome: {personalidade_amigavel['nome']}")
print(f"Nivel: {personalidade_amigavel['nivel_personalidade']} (Amigavel)")
print(f"Tom: {personalidade_amigavel['tom_voz']}")
print()

# =====================================================================
# EXEMPLO 3: Personalidade Descontraída (Startup Tech)
# =====================================================================
print("3. Personalidade DESCONTRAÍDA (Startup Tech)")
print("-" * 70)

personalidade_descontraida = {
    "user_id": USER_ID,
    "nome": "Bot da Galera",
    "nivel_personalidade": 8,  # Animado e entusiasmado
    "tom_voz": "descontraido",
    "forma_tratamento": "informal",
    "apresentacao_inicial": "E aí! Beleza? Bora resolver isso juntos! 🚀"
}

print(f"Nome: {personalidade_descontraida['nome']}")
print(f"Nivel: {personalidade_descontraida['nivel_personalidade']} (Animado)")
print(f"Tom: {personalidade_descontraida['tom_voz']}")
print()

# =====================================================================
# EXEMPLO 4: Personalidade Técnica (SaaS/Software)
# =====================================================================
print("4. Personalidade TÉCNICA (SaaS/Software)")
print("-" * 70)

personalidade_tecnica = {
    "user_id": USER_ID,
    "nome": "TechSupport AI",
    "nivel_personalidade": 10,  # Técnico e especialista
    "tom_voz": "objetivo",
    "forma_tratamento": "voce",
    "apresentacao_inicial": "Olá. Especialista técnico à disposição. Em que posso auxiliar?"
}

print(f"Nome: {personalidade_tecnica['nome']}")
print(f"Nivel: {personalidade_tecnica['nivel_personalidade']} (Tecnico)")
print(f"Tom: {personalidade_tecnica['tom_voz']}")
print()

# =====================================================================
# ESCOLHA UMA PERSONALIDADE
# =====================================================================
print("=" * 70)
print("Escolha qual personalidade usar:")
print("=" * 70)
print("1 - Formal (Banco/Jurídico)")
print("2 - Amigável (E-commerce/Loja)")
print("3 - Descontraída (Startup Tech)")
print("4 - Técnica (SaaS/Software)")
print()

escolha = input("Digite o número (1-4) ou Enter para usar Amigável: ").strip()

if escolha == "1":
    personalidade = personalidade_formal
elif escolha == "3":
    personalidade = personalidade_descontraida
elif escolha == "4":
    personalidade = personalidade_tecnica
else:
    personalidade = personalidade_amigavel

print()
print(f"✅ Usando personalidade: {personalidade['nome']}")
print()

# Limpar personalidade antiga
try:
    _client.table("personalidade_agente").delete().eq("user_id", USER_ID).execute()
    print("🗑️  Personalidade antiga removida")
except:
    pass

# Inserir nova personalidade
try:
    _client.table("personalidade_agente").insert(personalidade).execute()
    print(f"✅ Personalidade '{personalidade['nome']}' inserida com sucesso!")
except Exception as e:
    print(f"❌ Erro ao inserir personalidade: {e}")
    sys.exit(1)

print()

# =====================================================================
# BASE DE CONHECIMENTO - EXEMPLOS POR CATEGORIA
# =====================================================================
print("=" * 70)
print("Inserindo Base de Conhecimento")
print("=" * 70)
print()

# Limpar base antiga
try:
    _client.table("base_conhecimento").delete().eq("user_id", USER_ID).execute()
    print("🗑️  Base de conhecimento antiga removida")
except:
    pass

conhecimento = []

# ---------------------------------------------------------------------
# PRODUTO 1: SaaS com múltiplos planos
# ---------------------------------------------------------------------
conhecimento.append({
    "user_id": USER_ID,
    "categoria": "produto",
    "dados": {
        "nome": "CloudFlow Pro",
        "tipo_produto": "assinatura_multiplos_planos",
        "descricao": "Plataforma completa de automação de workflows com IA",
        "categoria": "Software",
        "planos": [
            {
                "nome": "Starter",
                "preco_mensal": "99",
                "preco_anual": "990",
                "desconto_anual": "2 meses grátis",
                "beneficios": [
                    "Até 100 workflows/mês",
                    "2 GB de armazenamento",
                    "Integrações básicas",
                    "Suporte por email"
                ],
                "limite_usuarios": "3 usuários",
                "limite_conversas": "100 workflows/mês",
                "ideal_para": "Freelancers e pequenos times"
            },
            {
                "nome": "Business",
                "preco_mensal": "299",
                "preco_anual": "2990",
                "desconto_anual": "2 meses grátis",
                "beneficios": [
                    "Workflows ilimitados",
                    "50 GB de armazenamento",
                    "Todas as integrações",
                    "Suporte prioritário",
                    "API dedicada",
                    "Analytics avançado"
                ],
                "limite_usuarios": "20 usuários",
                "limite_conversas": "Ilimitado",
                "ideal_para": "Empresas em crescimento"
            },
            {
                "nome": "Enterprise",
                "preco_mensal": "999",
                "preco_anual": "9990",
                "desconto_anual": "2 meses grátis + Onboarding personalizado",
                "beneficios": [
                    "Tudo do Business",
                    "Armazenamento ilimitado",
                    "SSO e SAML",
                    "Gerente de conta dedicado",
                    "SLA 99.9%",
                    "Compliance LGPD/SOC2"
                ],
                "limite_usuarios": "Ilimitado",
                "limite_conversas": "Ilimitado",
                "ideal_para": "Grandes corporações"
            }
        ]
    }
})

# ---------------------------------------------------------------------
# PRODUTO 2: Produto único (e-commerce)
# ---------------------------------------------------------------------
conhecimento.append({
    "user_id": USER_ID,
    "categoria": "produto",
    "dados": {
        "nome": "Fone Bluetooth Premium",
        "tipo_produto": "produto_unico",
        "descricao": "Fone de ouvido bluetooth com cancelamento de ruído ativo",
        "categoria": "Eletrônicos",
        "preco": "399",
        "preco_promocional": "299",
        "caracteristicas": [
            "Bateria 40h",
            "Cancelamento de ruído ANC",
            "Bluetooth 5.3",
            "Resistente à água IPX7"
        ]
    }
})

# ---------------------------------------------------------------------
# SERVIÇO: Consultoria
# ---------------------------------------------------------------------
conhecimento.append({
    "user_id": USER_ID,
    "categoria": "servico",
    "dados": {
        "nome": "Consultoria em Transformação Digital",
        "descricao": "Implementação completa de soluções de IA e automação para seu negócio",
        "preco": "8500",
        "duracao": "3 meses",
        "entregaveis": [
            "Análise de processos atuais",
            "Roadmap de implementação",
            "Setup de ferramentas",
            "Treinamento da equipe",
            "3 meses de suporte pós-projeto"
        ]
    }
})

# ---------------------------------------------------------------------
# FAQs
# ---------------------------------------------------------------------
faqs = [
    {
        "pergunta": "Qual o horário de atendimento?",
        "resposta": "Nosso time está disponível de segunda a sexta, das 9h às 18h. O assistente virtual funciona 24/7!",
        "categoria_faq": "Atendimento"
    },
    {
        "pergunta": "Vocês oferecem período de teste?",
        "resposta": "Sim! Todos os planos têm 14 dias de teste gratuito, sem necessidade de cartão de crédito.",
        "categoria_faq": "Comercial"
    },
    {
        "pergunta": "Como funciona o cancelamento?",
        "resposta": "Você pode cancelar a qualquer momento. Em planos mensais, não há cobrança no próximo mês. Em planos anuais, fazemos reembolso proporcional.",
        "categoria_faq": "Comercial"
    },
    {
        "pergunta": "Vocês oferecem treinamento?",
        "resposta": "Sim! Planos Business e Enterprise incluem onboarding completo. Plano Starter tem tutoriais em vídeo.",
        "categoria_faq": "Suporte"
    },
    {
        "pergunta": "Meus dados estão seguros?",
        "resposta": "Sim! Somos certificados SOC2 e LGPD compliant. Todos os dados são criptografados em repouso e em trânsito.",
        "categoria_faq": "Segurança"
    }
]

for faq in faqs:
    conhecimento.append({
        "user_id": USER_ID,
        "categoria": "faq",
        "dados": faq
    })

# ---------------------------------------------------------------------
# INFORMAÇÕES DA EMPRESA
# ---------------------------------------------------------------------
empresas = [
    {
        "tipo": "Sobre a empresa",
        "titulo": "Nossa História",
        "descricao": "Fundada em 2020, somos especialistas em automação inteligente. Já ajudamos mais de 500 empresas a economizar milhares de horas através de IA e automação.",
        "informacoes_adicionais": "Time de 50+ profissionais distribuídos pelo Brasil"
    },
    {
        "tipo": "Contato",
        "titulo": "Como nos encontrar",
        "descricao": "Email: contato@cloudflow.com.br\nTelefone: (11) 98765-4321\nWhatsApp: (11) 98765-4321",
        "informacoes_adicionais": "Matriz em São Paulo - SP"
    },
    {
        "tipo": "Politica",
        "titulo": "Política de Devolução",
        "descricao": "Reembolso de 100% em até 30 dias para qualquer plano, sem perguntas.",
        "informacoes_adicionais": "Processamento em até 5 dias úteis"
    }
]

for empresa in empresas:
    conhecimento.append({
        "user_id": USER_ID,
        "categoria": "empresa",
        "dados": empresa
    })

# Inserir tudo
try:
    result = _client.table("base_conhecimento").insert(conhecimento).execute()
    print(f"✅ {len(conhecimento)} itens inseridos na base de conhecimento:")
    print(f"   - 2 produtos (1 SaaS multi-plano + 1 produto físico)")
    print(f"   - 1 serviço (consultoria)")
    print(f"   - {len(faqs)} FAQs")
    print(f"   - {len(empresas)} informações da empresa")
except Exception as e:
    print(f"❌ Erro ao inserir base de conhecimento: {e}")
    sys.exit(1)

print()

# =====================================================================
# RESUMO FINAL
# =====================================================================
print("=" * 70)
print("✅ CONFIGURAÇÃO CONCLUÍDA!")
print("=" * 70)
print()
print("Próximos passos:")
print()
print("1. Inicie o servidor (se não estiver rodando):")
print("   uvicorn app:app --reload")
print()
print("2. Teste via API:")
print()
print("   curl -X POST http://localhost:8000/simulation/chat \\")
print("     -H 'Content-Type: application/json' \\")
print(f"     -d '{{\"user_id\": \"{USER_ID}\", \"message\": \"Quais planos vocês têm?\"}}'")
print()
print("3. Experimente diferentes perguntas:")
print("   - 'Quais são os planos disponíveis?'")
print("   - 'Qual a diferença entre Business e Enterprise?'")
print("   - 'Vocês oferecem teste grátis?'")
print("   - 'Qual o horário de atendimento?'")
print("   - 'Como funciona o cancelamento?'")
print("   - 'Conte sobre a empresa'")
print("   - 'Quanto custa a consultoria?'")
print()
print("=" * 70)
