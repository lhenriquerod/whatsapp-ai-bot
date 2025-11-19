"""
Script para migrar automaticamente todos os arquivos de teste
de português para inglês (nomes de tabelas e campos)
"""
import os
import glob

# Mapeamento de substituições
REPLACEMENTS = {
    # Tabelas
    '.table("conversas")': '.table("conversations")',
    '.table("mensagens")': '.table("messages")',
    '.table("base_conhecimento")': '.table("knowledge_base")',
    '.table("personalidade_agente")': '.table("agent_personality")',
    '.table("configuracao_empresa")': '.table("company_settings")',
    
    # Campos - conversas/conversations
    '"titulo"': '"title"',
    '"iniciada_em"': '"started_at"',
    '"finalizada_em"': '"ended_at"',
    '"total_mensagens"': '"total_messages"',
    '"canal"': '"channel"',
    
    # Campos - mensagens/messages
    '"conversa_id"': '"conversation_id"',
    '"tipo"': '"type"',
    '"mensagem"': '"message"',
    
    # Campos - base_conhecimento/knowledge_base
    '"categoria"': '"category"',
    '"dados"': '"data"',
    
    # Campos - personalidade_agente/agent_personality
    '"nome"': '"name"',
    '"nivel_personalidade"': '"personality_level"',
    '"tom_voz"': '"voice_tone"',
    '"forma_tratamento"': '"address_form"',
    '"apresentacao_inicial"': '"initial_message"',
    
    # Valores ENUM - categoria/category
    '"produto"': '"product"',
    '"servico"': '"service"',
    '"empresa"': '"company"',
    '"personalizado"': '"custom"',
    
    # Valores ENUM - tipo/type  
    '"usuario"': '"user"',
    '"agente"': '"agent"',
    '"sistema"': '"system"',
    
    # Valores ENUM - status
    '"ativa"': '"open"',
    '"finalizada"': '"closed"',
    '"arquivada"': '"archived"',
    
    # Valores ENUM - tom_voz/voice_tone
    '"amigavel"': '"friendly"',
    '"objetivo"': '"objective"',
    '"descontraido"': '"casual"',
    
    # Valores ENUM - forma_tratamento/address_form
    '"voce"': '"you_informal"',
    '"senhor"': '"you_formal"',
    
    # Comentários e strings em português (casos específicos)
    'base_conhecimento': 'knowledge_base',
    'mensagens antigas': 'old messages',
    'conversas': 'conversations',
    'mensagens': 'messages',
}

def migrate_file(filepath):
    """Migra um arquivo aplicando todas as substituições"""
    print(f"Migrando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    for old, new in REPLACEMENTS.items():
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes += count
            if count > 0:
                print(f"  - {old} → {new} ({count}x)")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {changes} substituições em {filepath}\n")
        return changes
    else:
        print(f"⏭️  Nenhuma mudança necessária em {filepath}\n")
        return 0

def main():
    """Migra todos os arquivos test_*.py"""
    print("=" * 60)
    print("MIGRAÇÃO DE ARQUIVOS DE TESTE: PORTUGUÊS → INGLÊS")
    print("=" * 60)
    print()
    
    # Encontrar todos os arquivos test_*.py
    test_files = glob.glob("test_*.py")
    
    if not test_files:
        print("❌ Nenhum arquivo test_*.py encontrado")
        return
    
    print(f"Arquivos encontrados: {len(test_files)}")
    print()
    
    total_changes = 0
    
    for filepath in sorted(test_files):
        changes = migrate_file(filepath)
        total_changes += changes
    
    print("=" * 60)
    print(f"✅ MIGRAÇÃO CONCLUÍDA")
    print(f"Total de arquivos processados: {len(test_files)}")
    print(f"Total de substituições: {total_changes}")
    print("=" * 60)

if __name__ == "__main__":
    main()
