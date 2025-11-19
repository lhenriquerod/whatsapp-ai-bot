"""
Script para listar users existentes ou criar um user de teste
"""
from src.services.supabase_service import _client

print("=" * 60)
print("Consultando usuários existentes...")
print("=" * 60)

try:
    # List users from the `users` table (actual fields: full_name, email, phone, plan, status, is_admin, etc.)
    result = _client.table("users").select("id, full_name, email, phone, plan, status").limit(5).execute()
    
    if result.data and len(result.data) > 0:
        print(f"\n✅ Found {len(result.data)} users:")
        for user in result.data:
            print(f"   - ID: {user['id']}")
            print(f"     Name: {user.get('full_name', 'N/A')}")
            print(f"     Email: {user.get('email', 'N/A')}")
            print(f"     Phone: {user.get('phone', 'N/A')}")
            print(f"     Plan: {user.get('plan', 'N/A')}")
            print(f"     Status: {user.get('status', 'N/A')}")
            print()
        
        # Use the first user for quick testing
        first_user_id = result.data[0]['id']
        print(f"💡 Use this user_id for tests: {first_user_id}")
        
    else:
        print("\n⚠️ No users found in the 'users' table")
        print("\nYou need to:")
        print("1. Create a user through Supabase Auth (signup)")
        print("2. Or insert directly into the 'users' table (if allowed)")
        
except Exception as e:
    print(f"\n❌ Error querying users: {e}")
    print("\nTrying to query auth.users...")
    
    try:
        # Some setups may have direct access to auth.users
        result = _client.rpc('get_auth_users').execute()
        print(result.data)
    except:
        print("❌ Could not access auth.users directly")
        print("\n💡 Solution: Create a user through Supabase Dashboard")
        print("   Authentication → Users → Add user")

print("\n" + "=" * 60)
