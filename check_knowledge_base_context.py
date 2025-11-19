"""
Verifica se a base de conhecimento está sendo carregada corretamente
"""
from src.services.supabase_service import get_context, _client

# User ID do sistema
USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"

print("=" * 60)
print("DIAGNÓSTICO: Base de Conhecimento")
print("=" * 60)
print()

# 1. Verificar se existem dados na tabela knowledge_base
print("1. Verificando dados na tabela knowledge_base...")
try:
    result = _client.table("knowledge_base") \
        .select("id, category, data") \
        .eq("user_id", USER_ID) \
        .execute()
    
    print(f"   Registros encontrados: {len(result.data)}")
    
    if result.data:
        for idx, item in enumerate(result.data, 1):
            print(f"\n   Item {idx}:")
            print(f"   - ID: {item['id']}")
            print(f"   - Categoria: {item['category']}")
            print(f"   - Dados: {str(item['data'])[:100]}...")
    else:
        print("   ❌ Nenhum dado encontrado!")
        print("   Você precisa cadastrar produtos/serviços no frontend")
        
except Exception as e:
    print(f"   ❌ Erro ao buscar: {e}")

print()

# 2. Testar função get_context
print("2. Testando função get_context()...")
try:
    context = get_context(owner_id=USER_ID)
    
    print(f"   Tamanho do contexto: {len(context)} caracteres")
    print()
    print("   Contexto gerado:")
    print("   " + "-" * 56)
    print(context[:500])  # Primeiros 500 caracteres
    print("   " + "-" * 56)
    
    if "Nenhuma base de conhecimento" in context:
        print("\n   ❌ Base de conhecimento vazia!")
    else:
        print("\n   ✅ Contexto gerado com sucesso!")
        
except Exception as e:
    print(f"   ❌ Erro ao gerar contexto: {e}")

print()

# 3. Verificar configuração de KB_TABLE e KB_FIELDS
print("3. Verificando configuração...")
from src.utils.config import KB_TABLE, KB_FIELDS, KB_OWNER_COL

print(f"   KB_TABLE: {KB_TABLE}")
print(f"   KB_FIELDS: {KB_FIELDS}")
print(f"   KB_OWNER_COL: {KB_OWNER_COL}")

if KB_TABLE != "knowledge_base":
    print(f"   ⚠️  KB_TABLE deveria ser 'knowledge_base'!")
    
if KB_FIELDS != "category,data":
    print(f"   ⚠️  KB_FIELDS deveria ser 'category,data'!")

print()
print("=" * 60)
