#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

import openai
from config.settings import settings

def test_language_prompt():
    print("Testing language-specific prompts...")
    
    client = openai.OpenAI(api_key=settings.openai_api_key)
    
    # Test prompts with different languages
    prompts = {
        "en": "Please respond in English. Analyze AAPL stock and give a buy/hold/sell recommendation.",
        "zh-TW": "請用繁體中文回答。分析 AAPL 股票並給出買入/持有/賣出建議。",
        "zh-CN": "请用简体中文回答。分析 AAPL 股票并给出买入/持有/卖出建议。"
    }
    
    for lang, prompt in prompts.items():
        try:
            print(f"\n--- Testing {lang} ---")
            print(f"Prompt: {prompt}")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            print(f"Response: {result}")
            
        except Exception as e:
            print(f"Error with {lang}: {e}")

if __name__ == "__main__":
    test_language_prompt()