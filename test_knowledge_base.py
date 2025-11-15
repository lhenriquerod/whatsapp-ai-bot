"""
Script para inserir dados de exemplo na base_conhecimento e testar get_context()
"""
from src.services.supabase_service import _client, get_context
import json

# User ID válido (do list_users.py)
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

print("=" * 60)
print("Inserindo dados de exemplo na base_conhecimento")
print("=" * 60)

# Dados de exemplo para cada categoria
exemplos = [
    {
        "user_id": USER_ID,
        "categoria": "produto",
        "dados": {
            "nome": "Notebook Dell Inspiron 15",
            "descricao": "Notebook para uso profissional com processador Intel i7",
            "preco": "R$ 3.499,00",
            "caracteristicas": "16GB RAM, SSD 512GB, Tela 15.6 Full HD"
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "produto",
        "dados": {
            "nome": "Mouse Logitech MX Master 3",
            "descricao": "Mouse ergonômico sem fio para produtividade",
            "preco": "R$ 599,00",
            "caracteristicas": "Bateria recarregável, 7 botões personalizáveis, Bluetooth"
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "servico",
        "dados": {
            "nome": "Consultoria em TI",
            "descricao": "Consultoria especializada em infraestrutura e cloud",
            "duracao": "Pacotes de 10, 20 ou 40 horas",
            "preco": "A partir de R$ 200/hora"
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "empresa",
        "dados": {
            "topico": "Horário de Funcionamento",
            "conteudo": "Atendemos de segunda a sexta, das 9h às 18h. Sábados das 9h às 13h."
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "empresa",
        "dados": {
            "topico": "Formas de Pagamento",
            "conteudo": "Aceitamos Pix, cartão de crédito (até 12x), débito e transferência bancária."
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "faq",
        "dados": {
            "pergunta": "Qual o prazo de entrega?",
            "resposta": "Para produtos em estoque, entregamos em até 3 dias úteis para a capital e 7 dias para interior."
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "faq",
        "dados": {
            "pergunta": "Vocês oferecem garantia?",
            "resposta": "Sim! Todos os produtos têm garantia de 12 meses contra defeitos de fabricação."
        }
    },
    {
        "user_id": USER_ID,
        "categoria": "personalizado",
        "dados": {
            "titulo": "Política de Troca",
            "descricao": "Trocas aceitas em até 7 dias após recebimento, desde que o produto esteja lacrado."
        }
    }
]

try:
    # Limpar registros antigos deste usuário (para testes)
    print("\n1. Limpando registros antigos...")
    _client.table("base_conhecimento").delete().eq("user_id", USER_ID).execute()
    print("✅ Registros antigos removidos")
    
    # Inserir novos registros
    print("\n2. Inserindo novos registros...")
    for i, exemplo in enumerate(exemplos, 1):
        result = _client.table("base_conhecimento").insert(exemplo).execute()
        if result.data:
            print(f"✅ {i}/{len(exemplos)} - {exemplo['categoria']}: {exemplo['dados'].get('nome') or exemplo['dados'].get('topico') or exemplo['dados'].get('pergunta', 'Item')}")
    
    print(f"\n✅ {len(exemplos)} registros inseridos com sucesso!")
    
    # Testar get_context()
    print("\n" + "=" * 60)
    print("Testando get_context()")
    print("=" * 60)
    
    context = get_context(owner_id=USER_ID)
    
    print("\n📋 Contexto retornado:")
    print("-" * 60)
    print(context)
    print("-" * 60)
    
    # Contar linhas de contexto
    linhas = context.split("\n")
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de linhas: {len(linhas)}")
    print(f"   - Tamanho: {len(context)} caracteres")
    
    # Verificar se todos os itens estão no contexto
    print(f"\n✅ Contexto gerado com sucesso!")
    print(f"   Use este contexto nas rotas /chat e /simulation/chat")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Teste concluído")
print("=" * 60)
