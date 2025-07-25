#!/usr/bin/env python3

# OpenAI GPT-4o-mini pricing (July 2025)
INPUT_COST_PER_1M_TOKENS = 0.150  # $0.150 per 1M input tokens
OUTPUT_COST_PER_1M_TOKENS = 0.600  # $0.600 per 1M output tokens

# Actual usage from test results
RESUME_ANALYSIS_TOKENS = {
    'prompt_tokens': 867,
    'completion_tokens': 418,
    'total_tokens': 1285
}

# Estimated intent analysis tokens (when user provides comments)
INTENT_ANALYSIS_TOKENS = {
    'prompt_tokens': 300,
    'completion_tokens': 150,
    'total_tokens': 450
}

def calculate_cost(prompt_tokens, completion_tokens):
    input_cost = (prompt_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS
    output_cost = (completion_tokens / 1_000_000) * OUTPUT_COST_PER_1M_TOKENS
    return input_cost + output_cost

def main():
    print("ResumeRoast GPT Cost Calculator")
    print("=" * 40)
    
    # Basic resume analysis cost
    resume_cost = calculate_cost(
        RESUME_ANALYSIS_TOKENS['prompt_tokens'],
        RESUME_ANALYSIS_TOKENS['completion_tokens']
    )
    
    # Intent analysis cost (when comments provided)
    intent_cost = calculate_cost(
        INTENT_ANALYSIS_TOKENS['prompt_tokens'],
        INTENT_ANALYSIS_TOKENS['completion_tokens']
    )
    
    # Combined cost
    total_cost = resume_cost + intent_cost
    
    print(f"\nCost Breakdown:")
    print(f"Resume Analysis Only: ${resume_cost:.6f}")
    print(f"Intent Analysis Add-on: ${intent_cost:.6f}")
    print(f"Total with Comments: ${total_cost:.6f}")
    
    print(f"\nVolume Pricing:")
    volumes = [1, 10, 50, 100, 500, 1000, 5000]
    
    print(f"{'Volume':<10} {'Daily Cost':<12} {'Monthly Cost':<15} {'Annual Cost':<12}")
    print("-" * 55)
    
    for volume in volumes:
        daily_cost = volume * total_cost
        monthly_cost = daily_cost * 30
        annual_cost = daily_cost * 365
        
        print(f"{volume:<10} ${daily_cost:<11.4f} ${monthly_cost:<14.2f} ${annual_cost:<11.2f}")
    
    print(f"\nBusiness Model Examples:")
    print(f"If you charge $0.50 per evaluation:")
    print(f"  Cost: ${total_cost:.6f}")
    print(f"  Revenue: $0.50")
    print(f"  Profit: ${0.50 - total_cost:.6f}")
    print(f"  Margin: {((0.50 - total_cost) / 0.50) * 100:.2f}%")
    
    print(f"\nIf you charge $1.00 per evaluation:")
    print(f"  Cost: ${total_cost:.6f}")
    print(f"  Revenue: $1.00")
    print(f"  Profit: ${1.00 - total_cost:.6f}")
    print(f"  Margin: {((1.00 - total_cost) / 1.00) * 100:.2f}%")

if __name__ == "__main__":
    main()
