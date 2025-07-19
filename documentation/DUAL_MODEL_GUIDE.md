# Dual-Model Scoring System

## Overview

The ResumeRoast system now features **dual-model AI scoring** using both OpenAI GPT-4o-mini and Google Gemini 1.5-pro for comprehensive resume analysis. This approach provides:

- **Enhanced Accuracy**: Two independent AI models provide cross-validation
- **Consensus Analysis**: Compare scores and identify agreement levels
- **Reliability**: Fallback mechanisms ensure scoring works even if one model fails
- **Transparency**: Full visibility into how scores are calculated

## How It Works

### 1. Structured Analysis
- Extracts and analyzes skills, experience, education
- Calculates baseline compatibility scores
- Provides fallback scoring if AI models fail

### 2. Dual AI Analysis
- **OpenAI GPT-4o-mini**: Primary analysis with structured prompting
- **Google Gemini 1.5-pro**: Secondary analysis with optimized prompts
- Both models analyze the same data independently

### 3. Score Combination
- Combines scores from both models
- Calculates consensus level and score variance
- Provides final weighted score

### 4. Transparency Features
- Shows individual model scores
- Displays agreement analysis
- Provides processing metadata
- Includes fallback information

## API Response Format

```json
{
  "final_score": 85,
  "overall_score": 85,
  "confidence_level": "High",
  "ai_comparison": {
    "openai_score": 87,
    "gemini_score": 83,
    "score_variance": 4,
    "consensus_level": "High",
    "agreement_analysis": {
      "score_agreement": "High",
      "qualitative_agreement": {...}
    }
  },
  "dual_model_results": {
    "openai": {
      "result": {...},
      "processing_info": {...}
    },
    "gemini": {
      "result": {...},
      "processing_info": {...}
    }
  },
  "transparency": {
    "methodology": "Dual AI (OpenAI + Gemini) + Structured Analysis",
    "processing_time_seconds": 3.45,
    "validation": {
      "models_agreement": "High",
      "both_models_available": true,
      "fallback_used": false
    }
  },
  "score_breakdown": {
    "skills_score": 88,
    "experience_score": 85,
    "education_score": 80,
    "domain_score": 87
  },
  "strengths": [...],
  "concerns": [...],
  "recommendations": [...]
}
```

## Frontend Features

The Streamlit interface now displays:

### Dual Model Comparison
- Individual scores from OpenAI and Gemini
- Consensus level indicator
- Score variance analysis

### Enhanced Transparency
- Processing methodology details
- Model availability status
- Processing time metrics

### Detailed Breakdown
- Category-wise scoring (Skills, Experience, Education, Domain)
- Key strengths and concerns
- Matching vs missing skills
- Actionable recommendations

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
```

### Model Settings
- **OpenAI**: GPT-4o-mini with temperature 0.1
- **Gemini**: 1.5-pro with temperature 0.1
- **Fallback**: Structured analysis for reliability

## Benefits

1. **Higher Accuracy**: Cross-validation between two leading AI models
2. **Reliability**: System works even if one AI service is down
3. **Transparency**: Users can see how scores are calculated
4. **Confidence Indicators**: Agreement levels help assess result reliability
5. **Comprehensive Analysis**: Both quantitative and qualitative insights

## Testing

Run the dual-model test:
```bash
python test_dual_model.py
```

This will demonstrate:
- Model initialization
- Dual scoring process
- Result comparison
- Transparency features
