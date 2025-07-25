# GPT Cost Analysis for ResumeRoast

## Current Usage Analysis (Based on Test Results)

### Token Usage per Resume Evaluation:
- **Prompt Tokens**: 867
- **Completion Tokens**: 418
- **Total Tokens**: 1,285
- **Processing Time**: 10.49 seconds

### OpenAI GPT-4o-mini Pricing (as of July 2025):
- **Input Tokens**: $0.150 per 1M tokens
- **Output Tokens**: $0.600 per 1M tokens

## Cost Breakdown

### Cost per Resume Evaluation:

**Input Cost:**
- 867 prompt tokens × $0.150 / 1,000,000 = **$0.00013**

**Output Cost:**
- 418 completion tokens × $0.600 / 1,000,000 = **$0.00025**

**Total Cost per Evaluation**: **$0.00038** (~$0.0004)

## Volume Analysis

| Volume | Daily Cost | Monthly Cost | Annual Cost |
|--------|------------|--------------|-------------|
| 10 resumes/day | $0.004 | $0.12 | $1.44 |
| 50 resumes/day | $0.019 | $0.57 | $6.84 |
| 100 resumes/day | $0.038 | $1.14 | $13.68 |
| 500 resumes/day | $0.19 | $5.70 | $68.40 |
| 1,000 resumes/day | $0.38 | $11.40 | $136.80 |

## Intent Analysis Additional Cost

### With New GPT-based Intent Analysis:
When users provide comments, there's an additional GPT call for intent analysis.

**Estimated additional usage per comment analysis:**
- **Prompt Tokens**: ~300 (user comment + job context + instructions)
- **Completion Tokens**: ~150 (structured JSON response)
- **Total Additional Tokens**: ~450

**Additional Cost per Comment Analysis:**
- Input: 300 × $0.150 / 1,000,000 = **$0.000045**
- Output: 150 × $0.600 / 1,000,000 = **$0.00009**
- **Total Additional**: **$0.000135** (~$0.00014)

### Combined Cost (Resume + Intent Analysis):
**Total per evaluation with comments**: **$0.00038 + $0.00014 = $0.00052** (~$0.0005)

## Cost Optimization Strategies

### 1. Token Efficiency
- **Current prompt is well-optimized** at 867 tokens
- Could reduce by ~10-15% with more concise instructions
- **Completion tokens (418) are reasonable** for comprehensive analysis

### 2. Caching Strategies
- **Job description caching**: Reuse parsed job data for multiple candidates
- **Skills taxonomy caching**: Pre-process common skills patterns
- **Template responses**: Cache common feedback patterns

### 3. Conditional Processing
- **Basic analysis first**: Use structured analysis for obvious mismatches
- **GPT only for edge cases**: When structured confidence < 80%
- **Comment analysis**: Only when user provides meaningful input (>20 chars)

## Business Model Implications

### Pricing Strategy Options:

**Option 1: Cost-Plus Model**
- Cost: $0.0005 per evaluation
- Markup: 1000x 
- **Price**: $0.50 per resume analysis

**Option 2: Volume Tiers**
- 1-10 evaluations: $1.00 each
- 11-50 evaluations: $0.75 each  
- 51+ evaluations: $0.50 each

**Option 3: Subscription Model**
- Basic: $9.99/month (up to 50 evaluations)
- Pro: $29.99/month (up to 200 evaluations)
- Enterprise: $99.99/month (unlimited)

### Break-even Analysis:
- **Cost**: $0.0005 per evaluation
- **Break-even at $0.50**: 1000x markup (99.9% profit margin)
- **Break-even at $0.10**: 200x markup (99.5% profit margin)

## Recommendations

### 1. Current Implementation is Cost-Effective ✅
- **Extremely low cost** per evaluation ($0.0005)
- **High-quality results** with comprehensive analysis
- **Room for significant markup** while remaining affordable

### 2. Monitor Usage Patterns
- Track token usage trends
- Identify optimization opportunities
- Monitor OpenAI pricing changes

### 3. Implement Smart Batching
- **Batch job parsing**: Process multiple resumes against same job
- **Parallel processing**: Handle multiple evaluations simultaneously
- **Queue management**: Optimize API call patterns

### 4. Consider Hybrid Approach
- **Basic scoring**: Use local algorithms for clear cases
- **GPT enhancement**: For complex analysis and edge cases
- **Progressive disclosure**: Offer basic free, premium GPT-powered

## Conclusion

**GPT cost is negligible** for ResumeRoast:
- **$0.0005 per complete evaluation** (including intent analysis)
- **Scales efficiently** even to thousands of daily evaluations
- **Enables premium pricing** with excellent profit margins
- **Quality justifies cost** - sophisticated AI analysis worth the investment

The implementation is **production-ready from a cost perspective** 🚀
