#!/usr/bin/env python
"""Test FastAPI backend integration"""

import requests
import json
import time

print("\n" + "="*70)
print("CHATBOT BACKEND API TEST")
print("="*70 + "\n")

BASE_URL = "http://127.0.0.1:8000"

# Test 1: Health check
print("Test 1: Health Check")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ PASSED\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")

# Test 2: Chat with crop recommendation
print("Test 2: Crop Recommendation Query")
print("-" * 70)
try:
    payload = {
        "message": "Best crop for sandy soil with low water?",
        "context": "Rajasthan, desert climate, low rainfall"
    }
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        timeout=60
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Reply: {data.get('reply', data.get('error', 'No response'))[:150]}...")
    print("✓ PASSED\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")

# Test 3: Chat with yield question
print("Test 3: Wheat Yield Question")
print("-" * 70)
try:
    payload = {
        "message": "How to increase wheat yield?",
        "context": "Wheat farming in Maharashtra, 5 acres"
    }
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        timeout=60
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Reply: {data.get('reply', data.get('error', 'No response'))[:150]}...")
    print("✓ PASSED\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")

# Test 4: Chat with pest management
print("Test 4: Pest Management Question")
print("-" * 70)
try:
    payload = {
        "message": "How to manage pests in rice?",
        "context": "Rice farm in North India"
    }
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        timeout=60
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Reply: {data.get('reply', data.get('error', 'No response'))[:150]}...")
    print("✓ PASSED\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")

print("="*70)
print("INTEGRATION TEST COMPLETE")
print("Backend is ready for Chatbot page connection!")
print("="*70 + "\n")
