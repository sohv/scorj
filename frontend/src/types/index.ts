export interface ScoringResult {
  score: number;
  feedback: {
    final_score: number;
    confidence_level: string;
    score_breakdown: {
      skills_score: number;
      experience_score: number;
      education_score: number;
      domain_score: number;
    };
    match_category: string;
    summary: string;
    strengths: string[];
    concerns: string[];
    missing_skills: string[];
    matching_skills: string[];
    recommendations: string[];
    structured_analysis?: {
      skills_analysis?: {
        match_percentage: number;
        matching_skills: string[];
        total_job_skills: number;
        total_matched: number;
      };
      experience_analysis?: {
        total_years: number;
        relevant_years: number;
        relevance_score: number;
      };
      education_analysis?: {
        highest_degree: string;
        degree_level_score: number;
      };
    };
    structured_comments?: {
      structured_feedback: string;
      total_bonus: number;
      scoring_adjustments: Record<string, number>;
    };
    transparency?: {
      methodology: string;
      processing_time_seconds: number;
      score_components: {
        openai_base_score: number;
        context_bonus: number;
        final_score: number;
      };
    };
  };
  job_title: string;
  company: string;
  model_used: string;
}

export interface JobInput {
  type: 'url' | 'text';
  value: string;
}

export type ScoringState = 'idle' | 'analyzing' | 'completed' | 'error';

export interface ChatMessage {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
  model: string;
}