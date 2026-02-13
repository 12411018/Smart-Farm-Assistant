#!/usr/bin/env python
"""Direct test of model and API without uvicorn complexity"""

import sys
sys.path.insert(0, r"c:\ENGINEERING\HACKATHON\MY_AGRI\backend")

from main import generate_reply

print("\n" + "="*60)
print("Testing Model Inference Directly")
print("="*60 + "\n")

# Test 1: General farming question
print("Test 1: Wheat Yield Question")
print("-" * 40)
reply1 = generate_reply(i
    user_message="How can I increase my wheat yield?",
    context="I farm in Maharashtra with 5 acres, using traditional methods"
)
print(f"Question: How can I increase my wheat yield?")
print(f"Context: I farm in Maharashtra with 5 acres, using traditional methods")
print(f"Answer: {reply1}\n")

# Test 2: Soil question
print("Test 2: Soil Fertility Question")
print("-" * 40)
reply2 = generate_reply(
    user_message="What can I do to improve soil fertility?",
    context="My soil is clayey with low organic matter"
)
print(f"Question: What can I do to improve soil fertility?")
print(f"Context: My soil is clayey with low organic matter")
print(f"Answer: {reply2}\n")

# Test 3: Water management
print("Test 3: Irrigation Schedule Question")
print("-" * 40)
reply3 = generate_reply(
    user_message="What is the best irrigation schedule for rice?",
    context="Growing rice in North India during monsoon season"
)
print(f"Question: What is the best irrigation schedule for rice?")
print(f"Context: Growing rice in North India during monsoon season")
print(f"Answer: {reply3}\n")

print("="*60)
print("Model Testing Complete!")
print("="*60)
