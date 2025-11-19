"""
Simple test for company info formatting
"""
import sys
sys.path.insert(0, '.')

from src.services.supabase_service import _client, get_context

USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

# Clean old data
_client.table("knowledge_base").delete().eq("user_id", USER_ID).execute()

# Insert company info
company_data = {
    "user_id": USER_ID,
    "category": "company",
    "data": {
        "type": "Sobre a empresa",
        "title": "Nossa Missao",
        "descricao": "Revolucionar o atendimento ao cliente atraves de IA acessivel e personalizada",
        "informacoes_adicionais": "Fundada em 2025, ja atendemos mais de 100 empresas"
    }
}

_client.table("knowledge_base").insert(company_data).execute()
print("Dados inseridos")

# Get formatted context
context = get_context(USER_ID)
print("\nContexto formatado:")
print("=" * 70)
print(context)
print("=" * 70)
