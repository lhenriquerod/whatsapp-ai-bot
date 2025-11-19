"""
Script para verificar a estrutura COMPLETA do campo data na knowledge_base
"""
import sys
sys.path.insert(0, '.')

import json
from src.services.supabase_service import _client

USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"

print("=" * 70)
print("Estrutura COMPLETA do campo 'data' na knowledge_base")
print("=" * 70)
print()

try:
    result = _client.table("knowledge_base") \
        .select("*") \
        .eq("user_id", USER_ID) \
        .execute()
    
    if result.data:
        print(f"✅ {len(result.data)} registro(s) encontrado(s)")
        print()
        
        for idx, item in enumerate(result.data, 1):
            print(f"{'=' * 70}")
            print(f"Registro {idx}:")
            print(f"{'=' * 70}")
            print(f"ID: {item.get('id')}")
            print(f"Categoria: {item.get('category')}")
            print()
            print("Campo 'data' COMPLETO:")
            print("-" * 70)
            
            data = item.get('data', {})
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            print("-" * 70)
            print()
            
            # Listar todos os campos do data
            print("Campos presentes no 'data':")
            for key in data.keys():
                value = data[key]
                if isinstance(value, list):
                    print(f"  - {key}: [lista com {len(value)} itens]")
                elif isinstance(value, dict):
                    print(f"  - {key}: [dicionário com {len(value)} chaves]")
                else:
                    print(f"  - {key}: {type(value).__name__}")
            
            print()
            
            # Se for produto com planos, mostrar campos de cada plano
            if 'planos' in data and isinstance(data['planos'], list):
                print("Campos dos PLANOS:")
                for plan_idx, plan in enumerate(data['planos'], 1):
                    print(f"  Plano {plan_idx}: {plan.get('nome', 'Sem nome')}")
                    for plan_key in plan.keys():
                        print(f"    - {plan_key}")
                print()
    else:
        print("❌ Nenhum registro encontrado")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("=" * 70)
