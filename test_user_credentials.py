"""
Test: Validate simulation mode uses user credentials instead of .env
"""
import sys
sys.path.insert(0, '.')

from src.services.ai_credentials_service import get_user_ai_credentials, validate_credentials

# User ID do frontend (mesmo usado anteriormente)
USER_ID = "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f"

print("=" * 70)
print("Test: User AI Credentials for Simulation Mode")
print("=" * 70)
print()

# STEP 1: Fetch user credentials
print("1. Buscando credenciais de IA do usuário...")
credentials = get_user_ai_credentials(USER_ID)

if credentials:
    print("✅ Credenciais encontradas!")
    print()
    print("Detalhes:")
    print(f"  - Provider: {credentials.get('provider')}")
    print(f"  - Model: {credentials.get('default_model')}")
    print(f"  - Temperature: {credentials.get('temperature')}")
    print(f"  - Base URL: {credentials.get('base_url') or 'None (padrão)'}")
    print(f"  - Organization ID: {credentials.get('organization_id') or 'None'}")
    print(f"  - Is Active: {credentials.get('is_active')}")
    
    # Mascarar API key
    api_key = credentials.get('api_key_encrypted')
    if api_key:
        masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
        print(f"  - API Key: {masked_key}")
    else:
        print(f"  - API Key: ❌ NÃO CONFIGURADA")
    
    print()
else:
    print("❌ Nenhuma credencial encontrada para este usuário")
    print()

# STEP 2: Validate credentials
print("2. Validando credenciais...")
is_valid = validate_credentials(credentials)

if is_valid:
    print("✅ Credenciais válidas!")
else:
    print("❌ Credenciais inválidas ou incompletas")

print()
print("=" * 70)

# STEP 3: Test with simulation endpoint
print()
print("3. Testando endpoint /simulation/chat...")
print()
print("💡 Agora o endpoint /simulation/chat deve:")
print("   - Buscar credenciais deste user_id no banco")
print("   - Usar a API key do usuário (não do .env)")
print("   - Usar o modelo configurado pelo usuário")
print("   - Usar a temperatura configurada pelo usuário")
print()
print("Para testar, envie uma requisição POST para:")
print("  http://localhost:8000/simulation/chat")
print()
print("Payload de exemplo:")
print("""
{
  "user_id": "e35af3a4-a7e6-422f-a483-bbcfc9d7c24f",
  "message": "Olá, estou testando o modo simulação"
}
""")
print()

# STEP 4: Compare with .env
print("=" * 70)
print("4. Comparação com .env local")
print("=" * 70)
print()

import os
from dotenv import load_dotenv
load_dotenv()

env_api_key = os.getenv("OPENAI_API_KEY", "")
env_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
env_temp = os.getenv("OPENAI_TEMPERATURE", "0.2")

if env_api_key:
    masked_env_key = f"{env_api_key[:10]}...{env_api_key[-4:]}" if len(env_api_key) > 14 else "***"
else:
    masked_env_key = "❌ NÃO CONFIGURADA"

print("Credenciais no .env:")
print(f"  - OPENAI_API_KEY: {masked_env_key}")
print(f"  - OPENAI_MODEL: {env_model}")
print(f"  - OPENAI_TEMPERATURE: {env_temp}")
print()

user_api_key = credentials.get('api_key_encrypted')
user_model = credentials.get('default_model')

if user_api_key and env_api_key:
    if user_api_key == env_api_key:
        print("⚠️  Usuário está usando a MESMA API key do .env")
    else:
        print("✅ Usuário está usando API key DIFERENTE do .env")

if user_model != env_model:
    print(f"✅ Modelo do usuário ({user_model}) é diferente do .env ({env_model})")
else:
    print(f"⚠️  Modelo do usuário é igual ao .env ({env_model})")

print()
print("=" * 70)
print("✅ Teste concluído!")
print("=" * 70)
