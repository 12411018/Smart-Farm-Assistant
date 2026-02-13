#!/usr/bin/env python
"""Crop Seek Model Test - Comprehensive evaluation"""

import sys
sys.path.insert(0, r'c:\ENGINEERING\HACKATHON\MY_AGRI\backend')

from main import generate_reply

print("\n" + "="*70)
print("CROP SEEK - MODEL ACCURACY & QUALITY TEST")
print("="*70 + "\n")

test_cases = [
    {
        "query": "Which crop should I grow?",
        "context": "Black soil, good irrigation, Maharashtra",
        "expected_keywords": ["cotton", "soybean", "sugarcane", "soil"]
    },
    {
        "query": "crop seek for sandy soil",
        "context": "Low water availability, Rajasthan",
        "expected_keywords": ["groundnut", "bajra", "sesame", "water"]
    },
    {
        "query": "What crops can I grow with low water?",
        "context": "Desert region, minimal rainfall",
        "expected_keywords": ["millet", "bajra", "jowar", "drought"]
    },
    {
        "query": "crop recommendation for monsoon",
        "context": "Good rainfall, clayey soil, farmer in West Bengal",
        "expected_keywords": ["paddy", "rice", "tur", "pulses"]
    },
    {
        "query": "best seed selection for my farm",
        "context": "Want high yield certified seeds",
        "expected_keywords": ["certified", "seed", "treatment", "germination"]
    },
    {
        "query": "What crop should I plant in rabi season?",
        "context": "North India, moderate soil fertility",
        "expected_keywords": ["wheat", "gram", "mustard", "rabi"]
    }
]

results = []

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}: Crop Seek Query")
    print("-" * 70)
    print(f"Query: {test['query']}")
    print(f"Context: {test['context']}")
    print()
    
    reply = generate_reply(test['query'], test['context'])
    
    print(f"Answer: {reply}")
    print()
    
    # Evaluate answer quality
    answer_lower = reply.lower()
    matching_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in answer_lower]
    quality_score = len(matching_keywords) / len(test['expected_keywords']) * 100
    
    # Check relevance criteria
    is_long_enough = len(reply) > 50
    is_specific = any(word in answer_lower for word in ["soil", "water", "season", "crop", "seed", "grow"])
    is_practical = any(word in answer_lower for word in ["tonnes", "kg", "hectare", "irrigation", "sowing", "treatment"])
    
    quality = "GOOD" if quality_score >= 50 and is_long_enough and is_specific else "FAIR" if is_long_enough else "POOR"
    
    print(f"Quality Assessment:")
    print(f"  - Matched Keywords: {matching_keywords} ({quality_score:.0f}%)")
    print(f"  - Length OK: {is_long_enough}")
    print(f"  - Relevant Content: {is_specific}")
    print(f"  - Practical Advice: {is_practical}")
    print(f"  - Overall Grade: {quality}")
    print()
    
    results.append({
        "query": test['query'],
        "quality": quality,
        "score": quality_score
    })

print("="*70)
print("SUMMARY")
print("="*70)
print()

good_count = sum(1 for r in results if r['quality'] == 'GOOD')
fair_count = sum(1 for r in results if r['quality'] == 'FAIR')
poor_count = sum(1 for r in results if r['quality'] == 'POOR')
avg_score = sum(r['score'] for r in results) / len(results)

print(f"Good Answers:  {good_count}/{len(results)}")
print(f"Fair Answers:  {fair_count}/{len(results)}")
print(f"Poor Answers:  {poor_count}/{len(results)}")
print(f"Average Score: {avg_score:.1f}%")
print()

if avg_score >= 70 and good_count >= 4:
    print("VERDICT: Crop Seek Model is PRODUCTION READY")
    print("The knowledge base provides accurate, practical agriculture advice.")
elif avg_score >= 50:
    print("VERDICT: Crop Seek Model is ACCEPTABLE")
    print("Good coverage with some refinement needed.")
else:
    print("VERDICT: Crop Seek Model needs IMPROVEMENT")
    print("Consider expanding knowledge base with more crop-specific data.")

print()
print("="*70)
