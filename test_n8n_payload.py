"""
Test script to reproduce n8n error with exact payload
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_upsert_conversation():
    """Test upsert conversation endpoint with typical n8n payload"""
    
    # Typical payload from n8n/WhatsApp integration
    # IMPORTANTE: Use um user_id válido que existe na tabela usuarios
    payload = {
        "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",  # User ID real do seu Supabase
        "external_contact_id": "5511999998888",  # Phone number
        "contact_name": "João Silva",
        "source": "whatsapp",
        "status": "open",
        "started_at_ts": 1704067200  # 2024-01-01 00:00:00 UTC
    }
    
    print(f"Testing POST {BASE_URL}/conversations/upsert")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/conversations/upsert",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS!")
            print(f"Conversation ID: {data.get('conversation_id')}")
            print(f"Created: {data.get('created')}")
        else:
            print(f"\n❌ ERROR {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error detail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error body: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running on port 8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def test_create_message():
    """Test create message endpoint"""
    
    payload = {
        "user_id": "6bf0dab0-e895-4730-b5fa-cd8acff6de0c",  # User ID real
        "external_contact_id": "5511999998888",
        "contact_name": "João Silva",
        "source": "whatsapp",
        "direction": "inbound",
        "type": "user",
        "text": "Olá, preciso de ajuda!",
        "metadata": {
            "message_id": "wamid.123456",
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    print(f"\nTesting POST {BASE_URL}/messages")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            print("\n✅ SUCCESS!")
            print(f"Message ID: {data.get('message_id')}")
            print(f"Conversation ID: {data.get('conversation_id')}")
        else:
            print(f"\n❌ ERROR {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error detail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error body: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running on port 8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing n8n Integration Endpoints")
    print("=" * 60)
    
    # Test conversation upsert
    test_upsert_conversation()
    
    # Test message creation
    test_create_message()
    
    print("\n" + "=" * 60)
    print("Tests completed")
    print("=" * 60)
