"""
Simple script to test Ollama connectivity
Run this on Windows to diagnose the issue
"""
import requests
import sys

def test_ollama_connection():
    """Test if Ollama is accessible"""
    print("=" * 60)
    print("Testing Ollama Connectivity")
    print("=" * 60)

    # Test 1: Check if Ollama API is accessible
    print("\n1. Testing Ollama API endpoint...")
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Ollama API is accessible!")
            print(f"   Version: {response.json()}")
        else:
            print(f"   ❌ Ollama API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection refused - Ollama is not running!")
        print("\n   Please start Ollama in another terminal:")
        print("      ollama serve")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Connection timeout - Ollama is not responding!")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 2: Check if llama3.2 model is available
    print("\n2. Testing llama3.2 model availability...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]

            if any('llama3.2' in name for name in model_names):
                print("   ✅ llama3.2 model is installed!")
                for name in model_names:
                    if 'llama3.2' in name:
                        print(f"      Found: {name}")
            else:
                print("   ❌ llama3.2 model not found!")
                print("\n   Available models:")
                for name in model_names:
                    print(f"      - {name}")
                print("\n   To install llama3.2:")
                print("      ollama pull llama3.2")
                return False
        else:
            print(f"   ❌ Failed to get model list: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking models: {e}")
        return False

    # Test 3: Test actual generation
    print("\n3. Testing Ollama generation with llama3.2...")
    try:
        payload = {
            "model": "llama3.2",
            "prompt": "Say 'Hello' and nothing else.",
            "stream": False
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Ollama generation works!")
            print(f"   Response: {result.get('response', '')[:100]}...")
        else:
            print(f"   ❌ Generation failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error during generation: {e}")
        return False

    # Test 4: Test with langchain-ollama
    print("\n4. Testing langchain-ollama integration...")
    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model="llama3.2",
            temperature=0,
        )
        print("   ✅ ChatOllama object created!")

        # Try to invoke it
        response = llm.invoke("Say 'test' and nothing else")
        print(f"   ✅ ChatOllama invoke works!")
        print(f"   Response: {response.content[:100]}...")

    except ImportError:
        print("   ❌ langchain-ollama not installed!")
        print("      pip install langchain-ollama")
        return False
    except Exception as e:
        print(f"   ❌ ChatOllama error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"\n   Full traceback:")
        print(traceback.format_exc())
        return False

    print("\n" + "=" * 60)
    print("✅ All tests passed! Ollama is working correctly.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_ollama_connection()
    sys.exit(0 if success else 1)
