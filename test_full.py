#!/usr/bin/env python3
"""Full test of LiteLLM proxy"""

from openai import OpenAI
import json

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

print("=" * 60)
print("Testing LiteLLM Proxy - Cerebras GLM-4.6 + Z.AI Fallback")
print("=" * 60)

try:
    response = client.chat.completions.create(
        model="glm-4.6",
        messages=[{"role": "user", "content": "Say: hello world"}],
        max_tokens=50
    )

    print(f"\n✓ SUCCESS!")
    print(f"\nModel: {response.model}")
    print(f"ID: {response.id}")
    print(f"\n--- Response ---")

    # Check all possible response fields
    message = response.choices[0].message
    print(f"Role: {message.role}")

    if hasattr(message, 'content') and message.content:
        print(f"Content: {message.content}")

    if hasattr(message, 'reasoning'):
        print(f"Reasoning: {message.reasoning}")

    # Print raw response
    print(f"\n--- Full Response Object ---")
    print(json.dumps(response.model_dump(), indent=2, default=str))

    print(f"\n--- Usage ---")
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
