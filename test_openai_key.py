#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.abspath('.'))

import openai
from config.settings import settings

def test_openai_key():
    print("Testing OpenAI API Key...")
    print(f"API Key: {settings.openai_api_key[:20]}...")
    
    try:
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in Chinese (Traditional)"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API Key is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except openai.APIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_key()
    sys.exit(0 if success else 1)