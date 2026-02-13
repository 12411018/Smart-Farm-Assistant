"""Agriculture knowledge base for reliable, accurate responses"""

AGRICULTURE_KB = {
    "wheat yield": [
        "To increase wheat yield, focus on: (1) Timely sowing between October-November for optimal temperature conditions, (2) Quality seeds and proper seed treatment with fungicides, (3) Balanced fertilization: 120 kg N, 60 kg P, 40 kg K per hectare, (4) Timely irrigation - typically 4-5 irrigations for wheat, (5) Weed management through herbicides or manual weeding, (6) Protection from pest and diseases like loose smut and Septoria.",
        "Wheat yield can be improved by: Using certified seeds of high-yielding varieties like HD2733, PBW343, or DBW17 suitable for your region. Apply irrigation at 30-35 days and 50-55 days after sowing. Maintain proper plant population of 100-120 plants/m2. Use 10-12 tonnes farmyard manure per hectare before sowing.",
        "For wheat in traditional farming: Implement crop rotation with legumes to maintain soil nitrogen. Add compost or farm manure 2-3 weeks before sowing. Practice minimum tillage to conserve soil moisture. Use neem-based pesticides for organic pest control. Mulching helps retain soil moisture during dry periods."
    ],
    
    "soil fertility": [
        "To improve soil fertility, especially in clayey soil with low organic matter: (1) Add 10-15 tonnes of compost or farmyard manure per hectare, (2) Practice crop rotation with legumes (pulses) which fix atmospheric nitrogen, (3) Use green manuring - plow in legume crops before flowering, (4) Apply phosphate-solubilizing bacteria and mycorrhizal fungi, (5) Avoid continuous monoculture, (6) Mulch to conserve moisture and add organic matter.",
        "For clayey soils: Improve drainage by adding sand (25-30%) and organic matter. Create raised beds for better water management. Apply gypsum (500-1000 kg/ha) to improve soil structure and reduce alkalinity if present. Add nitrogen-fixing legumes like gram, moong, or urad to improve nitrogen naturally.",
        "Organic soil improvement: Composting agricultural waste, cattle manure, and crop residues adds nutrients and improves soil structure. Earthworms further improve soil porosity. For low organic matter soils, aim to increase organic matter content from 0.5-1% to 2-3% over 3-5 years through consistent addition of organic materials."
    ],
    
    "rice irrigation": [
        "For rice irrigation schedule during monsoon season in North India: (1) Initial flooding 5-7 days after transplanting with 5 cm water depth, (2) Maintain 5 cm standing water during growing season, (3) Reduce water to 2-3 cm during panicle initiation and flowering for better grain filling, (4) Drain completely 15-20 days before harvest. During monsoon, reduce supplementary irrigation frequency due to rainfall.",
        "Optimal rice irrigation: Apply first irrigation 8-10 days after transplanting. Maintain continuous flooding of 5 cm during vegetative phase. During flowering and grain filling, reduce to 2-3 cm intermittently (alternate wetting and drying). This saves 20-30% water while maintaining yields. Post-monsoon, 4-5 irrigations are typically needed.",
        "Water management in rice during monsoon: Monitor rainfall and reduce irrigation accordingly. Excess water can cause disease (blast, brown leaf spot). Use field channels for drainage to prevent waterlogging. Alternate wetting and drying (AWD) technique saves 25% water and reduces methane emissions. Install check basins for better water distribution."
    ],
    
    "pest management": [
        "Integrated Pest Management (IPM) for crops: (1) Use resistant varieties, (2) Monitor fields regularly for pests, (3) Mechanical removal - hand-picking, light traps for nocturnal insects, (4) Biological control - encourage natural predators and parasitoids, (5) Chemical pesticides only when pest population exceeds economic threshold, (6) Use neem-based pesticides as safer alternative.",
        "Common pests and organic solutions: For aphids/mites - spray neem oil or insecticidal soap. For caterpillars - use Bacillus thuringiensis (Bt) or hand-pick. For beetles - install light traps and use deep plowing. For stem borers in rice - pheromone traps and parasitoid wasps. Crop rotation breaks pest cycles.",
        "Disease management: Preventive measures include crop rotation, proper spacing for air circulation, removing infected plants, using certified seeds, and timely sowing to avoid disease pressure. Fungal diseases can be managed with sulfur or copper sulfate sprays. Viral diseases require removing infected plants immediately."
    ],
    
    "fertilizer": [
        "Balanced fertilization guide: Most crops need NPK (Nitrogen, Phosphorus, Potassium) in different ratios. For wheat: 120-150 kg N, 60 kg P, 40 kg K per hectare. For rice: 120 kg N, 60 kg P, 40-60 kg K. Apply phosphorus and potassium before sowing. Split nitrogen application: 50% at sowing, 25% at tillering, 25% at panicle initiation for better utilization.",
        "Organic fertilizer alternatives: Cow dung compost (10-12 tonnes/ha), poultry manure (5 tonnes/ha), vermicompost (2-3 tonnes/ha), neem cake (500 kg/ha) for pest control, bone meal for phosphorus, wood ash for potassium. Legume intercropping fixes 100-150 kg N per hectare naturally.",
        "Micronutrient deficiency: Apply zinc sulfate (25 kg/ha) for zinc deficiency, borax (10 kg/ha) for boron, ferrous sulfate (10 kg/ha) for iron. Deficiency symptoms include yellowing leaves, stunted growth, abnormal flower/fruit development. Foliar spray of micronutrients (2% solution) corrects deficiencies faster than soil application."
    ],
    
    "crop rotation": [
        "Importance of crop rotation: Breaks pest and disease cycles, improves soil structure, reduces fertilizer requirement through legume nitrogen fixation, and increases overall productivity. A good rotation for India: Cereal (wheat/rice) → Legume (gram/moong) → Oilseed (mustard/groundnut) → back to Cereal. Avoid planting same family crops consecutively.",
        "Rotation for different regions: North India (wheat zone) - wheat → gram → mustard. South India (rice zone) - rice → pulses (redgram/chickpea) → oilseeds. Avoid rotating rice-rice continuously. Include legumes every 2-3 years to naturally replenish soil nitrogen.",
        "Benefits: 2-3 year rotations reduce fertilizer costs by 25-30%, reduce pest damage by 40-50%, and improve soil health. Farmers often see yield increases of 10-20% after establishing proper rotations for 2-3 years."
    ],
    
    "water conservation": [
        "Water conservation techniques: (1) Mulching reduces evaporation by 20-30%, (2) Drip irrigation saves 50% water compared to flood irrigation, (3) Raised bed farming improves water retention in dry regions, (4) Crop selection - choose drought-tolerant varieties, (5) Soil moisture conservation through organic matter addition, (6) Rainwater harvesting and storage.",
        "Irrigation efficiency: Use drip or sprinkler systems for vegetables and fruits. For field crops, furrow irrigation is more efficient than flood irrigation. Irrigate during early morning or evening to reduce evaporation. Soil moisture sensors help apply water exactly when needed. Mulching reduces water requirement by 25-30%.",
        "In drought-prone areas: Grow millet (bajra, jowar), groundnut, or pulses which are drought-resistant. Use conservation agriculture practices - zero tillage, crop residue retention. Harvest and store rainwater in farm ponds. Choose land races and traditional varieties adapted to local climate."
    ],
    
    "organic farming": [
        "Transitioning to organic farming: Takes 2-3 years to certify, during which yields may dip 10-20%. Use FYM/compost (10 tonnes/ha), neem cake, bone meal, rock phosphate. Maintain soil health through legume incorporation. Manage pests through biological methods. Keep detailed records for certification. Initially, produce may command 20-30% price premium.",
        "Organic inputs: Replace chemical NPK with organic sources - legume residue, compost, vermicompost, bone meal, wood ash, seaweed extracts. For pest management, use neem oil, turmeric-chili spray, pheromone traps. For disease, use sulfur dust, copper fungicide, Trichoderma. Crop rotation is essential to maintain soil health.",
        "Benefits of organic farming: Lower input costs after establishment, premium prices (20-30% higher), sustainable soil health, reduced pollution, biodiversity increase, and better long-term productivity. Most Indian states offer subsidies for organic farming adoption."
    ],

    "crop recommendation": [
        "Crop recommendation depends on season, soil, and water availability. For kharif in Maharashtra: soybean, cotton, tur, bajra, or maize. For rabi: wheat, gram, mustard. For low water areas: millets (bajra, jowar) and pulses. For black soil with irrigation: cotton and soybean perform well.",
        "If you want crop suggestions, share location, soil type, and irrigation. Example: Sandy soil with low water -> groundnut, bajra, sesame. Clayey soil with good water -> paddy, sugarcane. Red soil -> millets, pulses, groundnut.",
        "Seed selection: choose certified seeds of locally recommended varieties. Use seed treatment (fungicide + biofertilizer) before sowing to improve germination and early growth."
    ]
}


def get_knowledge_answer(question: str) -> str | None:
    """Get answer from knowledge base based on keywords"""
    question_lower = question.lower()

    # Priority 1: Crop-specific keywords (highest priority)
    crop_keywords = {
        "crop": "crop recommendation",
        "crop recommendation": "crop recommendation",
        "crop seek": "crop recommendation",
        "crop seed": "crop recommendation",
        "crop suggestion": "crop recommendation",
        "which crop": "crop recommendation",
        "what crop": "crop recommendation",
        "seed selection": "crop recommendation",
        "seed": "crop recommendation",
        "sandy soil": "crop recommendation",
        "drought": "crop recommendation",
        "low water": "crop recommendation",
        "monsoon": "crop recommendation",
        "kharif": "crop recommendation",
        "rabi": "crop recommendation",
        "grow": "crop recommendation",
        "plant": "crop recommendation",
    }

    for keyword, kb_key in crop_keywords.items():
        if keyword in question_lower:
            return AGRICULTURE_KB[kb_key][0]

    # Priority 2: Yield and fertility keywords
    yield_keywords = {
        "wheat": "wheat yield",
        "increase yield": "wheat yield",
        "yield": "wheat yield",
    }

    for keyword, kb_key in yield_keywords.items():
        if keyword in question_lower and kb_key in AGRICULTURE_KB:
            return AGRICULTURE_KB[kb_key][0]

    # Priority 3: Soil-specific keywords
    soil_keywords = {
        "soil": "soil fertility",
        "fertility": "soil fertility",
        "improve soil": "soil fertility",
    }

    for keyword, kb_key in soil_keywords.items():
        if keyword in question_lower and kb_key in AGRICULTURE_KB:
            return AGRICULTURE_KB[kb_key][0]

    # Priority 4: Other keywords (lower priority to avoid collision)
    other_keywords = {
        "irrigation": "rice irrigation",
        "rice": "rice irrigation",
        "pest": "pest management",
        "disease": "pest management",
        "fertilizer": "fertilizer",
        "fertiliz": "fertilizer",
        "npk": "fertilizer",
        "crop rotation": "crop rotation",
        "rotation": "crop rotation",
        "conservation": "water conservation",
        "water conservation": "water conservation",
        "organic": "organic farming",
    }

    for keyword, kb_key in other_keywords.items():
        if keyword in question_lower and kb_key in AGRICULTURE_KB:
            return AGRICULTURE_KB[kb_key][0]

    # Fallback: check direct KB key matches
    for keyword, answers in AGRICULTURE_KB.items():
        if keyword in question_lower:
            return answers[0]

    return None


def get_hybrid_response(user_question: str) -> str | None:
    """Get response from knowledge base first, then fall back to model if needed"""
    return get_knowledge_answer(user_question)
