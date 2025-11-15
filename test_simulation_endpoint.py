"""
Test script for /simulation/chat endpoint
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# User ID real do banco (obtido de list_users.py)
USER_ID = "6bf0dab0-e895-4730-b5fa-cd8acff6de0c"

def test_simulation_chat():
    """Test simulation chat endpoint"""
    
    print("=" * 60)
    print("Testing POST /simulation/chat")
    print("=" * 60)
    
    payload = {
        "user_id": USER_ID,
        "message": "Olá! Estou testando o modo simulação. Quais são os produtos disponíveis?"
    }
    
    print(f"\nPayload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/simulation/chat",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": "test-simulation-123"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS!")
            print(f"Reply: {data.get('reply')}")
            print(f"Source: {data.get('source')}")
            print(f"Request ID: {data.get('request_id')}")
        else:
            print(f"\n❌ ERROR {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running on port 8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def test_multiple_messages():
    """Test multiple simulation messages in sequence"""
    
    print("\n" + "=" * 60)
    print("Testing Multiple Simulation Messages")
    print("=" * 60)
    
    messages = [
        "Olá, bom dia!",
        "Qual o horário de funcionamento?",
        "Quais formas de pagamento vocês aceitam?",
        "Obrigado pela ajuda!"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Message {i}/{len(messages)} ---")
        print(f"User: {message}")
        
        payload = {
            "user_id": USER_ID,
            "message": message
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/simulation/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Agent: {data.get('reply')}")
            else:
                print(f"❌ ERROR {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Test single message
    test_simulation_chat()
    
    # Test multiple messages
    test_multiple_messages()
    
    print("\n" + "=" * 60)
    print("Tests completed")
    print("=" * 60)
