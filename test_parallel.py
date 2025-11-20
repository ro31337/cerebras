#!/usr/bin/env python3
"""Test fallback with parallel requests"""

from openai import OpenAI
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

def make_request(num):
    """Make a single request"""
    try:
        start = time.time()
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[{"role": "user", "content": f"Count to {num}"}],
            max_tokens=5
        )
        elapsed = time.time() - start
        return {
            'num': num,
            'status': '✓',
            'model': response.model,
            'time': elapsed
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'num': num,
            'status': '✗',
            'model': 'ERROR',
            'time': elapsed,
            'error': str(e)[:80]
        }

print("=" * 60)
print("Testing Fallback: 20 PARALLEL requests")
print("=" * 60)
print("\nSending 20 requests in parallel to exceed 10/min limit...\n")

# Send 20 requests in parallel
with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(make_request, range(1, 21)))

# Sort by num
results.sort(key=lambda x: x['num'])

# Print results
for r in results:
    print(f"{r['status']} Request {r['num']:2d}: {r['model']:30s} ({r['time']:.2f}s)")
    if 'error' in r:
        print(f"   Error: {r['error']}")

print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)

cerebras_count = sum(1 for r in results if 'cerebras' in r['model'])
zai_count = sum(1 for r in results if 'openai' in r['model'] or (r['model'] != 'ERROR' and 'cerebras' not in r['model']))
error_count = sum(1 for r in results if r['model'] == 'ERROR')

print(f"Cerebras responses: {cerebras_count}")
print(f"Z.AI responses:     {zai_count}")
print(f"Errors:             {error_count}")

if zai_count > 0:
    print("\n✓✓✓ Fallback to Z.AI IS WORKING! ✓✓✓")
else:
    print("\n⚠ No Z.AI responses detected")
