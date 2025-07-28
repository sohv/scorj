import streamlit as st
import requests
import json
from typing import List
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def score_resume(resume_file, job_url: str = None, job_description: str = None, user_comments: str = None):
    try:
        # Prepare files and data for the request
        files = {"resume": (resume_file.name, resume_file.getvalue(), resume_file.type)}
        data = {}
        if job_url:
            data["job_url"] = job_url.strip()
        if job_description:
            data["job_description"] = job_description.strip()
        if user_comments:
            data["user_comments"] = user_comments.strip()
        
        response = requests.post(
            f"{API_URL}/resume/score",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.text else 'Unknown error'
            st.error(f"Error scoring resume: {error_detail}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server. Please make sure the backend server is running.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def test_backend_connection():
    try:
        response = requests.get(f"{API_URL}/")
        is_connected = response.status_code == 200
        if is_connected:
            print(f"Connected to backend server at {API_URL}")
        else:
            print(f"Backend server returned status {response.status_code}")
        return is_connected
    except Exception as e:
        print(f"Cannot connect to backend server at {API_URL}: {e}")
        return False

def chat_with_ai(question: str, context: str = None):
    try:
        data = {
            "question": question
        }
        if context:
            data["context"] = context
            
        response = requests.post(
            f"{API_URL}/ai/chat",
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.text else 'Unknown error'
            st.error(f"Error in AI chat: {error_detail}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server. Please make sure the backend server is running.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

# Streamlit UI
st.title("Scorj")
st.write("**Score your resume against job descriptions**")

# Test backend connection (silently)
backend_connected = test_backend_connection()

# Resume upload
st.write("### Upload Resume")
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if resume_file:
    st.success(f"Resume uploaded: {resume_file.name}")

# Single job scoring
st.write("### Score the job")
job_input_method = st.radio("Choose input method:", ("LinkedIn URL", "Paste Job Description"))

job_url = None
job_description = None

if job_input_method == "LinkedIn URL":
    job_url = st.text_input("Enter LinkedIn job URL", placeholder="https://www.linkedin.com/jobs/view/...")
else:
    job_description = st.text_area("Paste the job description here:", height=200, placeholder="Paste the full job description...")

# User comments section
st.write("### Additional Context")
st.write("**Share your intentions and motivations to get personalized bonus points:**")

# Create expandable sections for guidance
with st.expander("How AI analyzes your intentions"):
    st.markdown("""
    **Our AI understands the meaning behind your words, not just keywords:**
    
    **Work Style Preferences:** 
    - "I thrive in collaborative office environments" → onsite preference
    - "I'm most productive working from home" → remote preference
    
    **Availability & Motivation:**
    - "I'm excited to start immediately" → high urgency score
    - "Looking to grow my career in AI" → learning motivation bonus
    
    **Professional Confidence:**
    - "I have extensive experience leading teams" → confidence boost
    - "Eager to relocate for the right opportunity" → flexibility bonus
    
    **The AI focuses on genuine intent and passion rather than keyword matching.**
    """)

user_comments = st.text_area(
    "Describe your motivations, preferences, and career goals:",
    height=120,
    placeholder="""Examples of meaningful context:
• I'm passionate about machine learning and excited to contribute to AI innovation
• I thrive in remote environments and have a proven track record of self-management  
• Ready to start immediately and looking to grow my technical leadership skills
• Willing to relocate to San Francisco for the right growth opportunity
• I love collaborative problem-solving and mentoring junior developers""",
    help="Our AI analyzes the genuine intent and motivation in your words to provide context-aware bonus points (up to 15+ points possible)."
)

# Initialize session state for scoring results
if "scoring_result" not in st.session_state:
    st.session_state.scoring_result = None

if st.button("Score Resume", disabled=not (resume_file and (job_url or job_description))):
    with st.spinner("Analyzing resume..."):
        result = score_resume(resume_file, job_url=job_url, job_description=job_description, user_comments=user_comments)
        if result:
            # Store result in session state to persist across reruns
            st.session_state.scoring_result = result

# Display results if we have them (either from current run or session state)
if st.session_state.scoring_result:
    result = st.session_state.scoring_result
    st.write("---")
    st.subheader("AI Resume Analysis Results")
    
    # Get feedback from result
    feedback = result.get('feedback', {})
    structured_analysis = feedback.get('structured_analysis', {})
    
    # Show intent analysis if available
    structured_comments = feedback.get('structured_comments', {})
    if user_comments and user_comments.strip():
        st.write("### Intent Analysis")
        
        if structured_comments:
            intent_analysis = structured_comments.get('intent_analysis', {})
            structured_feedback = structured_comments.get('structured_feedback', '')
            context_bonus = structured_comments.get('total_bonus', 0)
            
            if structured_feedback and structured_feedback != "No context provided":
                st.info(f"**AI-Detected Intentions:** {structured_feedback}")
            
            if context_bonus > 0:
                st.success(f"**Intent Bonus Applied:** +{context_bonus:.1f} points for genuine motivations and alignment")
                
                # Show breakdown if available
                adjustments = structured_comments.get('scoring_adjustments', {})
                if adjustments:
                    with st.expander("See bonus breakdown"):
                        for adj_type, value in adjustments.items():
                            if value > 0:
                                adj_name = adj_type.replace('_', ' ').title()
                                st.write(f"• {adj_name}: +{value:.1f} points")
            else:
                st.info("**Intent processed** - consider expressing stronger preferences or motivations for bonus points")
        else:
            st.info("**User context included:** " + user_comments.strip()[:100] + ("..." if len(user_comments.strip()) > 100 else ""))
    
    # Extract scores from analysis
    final_score = feedback.get('final_score', result.get('score', 0))
    
    # Display final score with color coding
    if final_score >= 80:
        st.success(f"Excellent Match: {final_score}/100")
    elif final_score >= 60:
        st.warning(f"Good Match: {final_score}/100")
    else:
        st.error(f"Needs Improvement: {final_score}/100")
    
    # Display job info
    st.write("### Job Information")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Job Title", result.get('job_title', 'N/A'))
    with col2:
        st.metric("Company", result.get('company', 'N/A'))
    
    # Display transparency info
    transparency = feedback.get('transparency', {})
    if transparency:
        st.write("### Analysis Transparency")
        
        col1, col2 = st.columns(2)
        with col1:
            methodology = transparency.get('methodology', 'Unknown')
            st.info(f"**Methodology:** {methodology}")
            
            processing_time = transparency.get('processing_time_seconds', 0)
            st.info(f"**Processing Time:** {processing_time:.2f} seconds")
        
        with col2:
            st.info(f"**AI Model:** OpenAI GPT-4o-mini")
            st.info(f"**Analysis Quality:** High Precision")
    
    # Display detailed feedback
    st.write("### Detailed Analysis")
    
    # Score breakdown
    score_breakdown = feedback.get('score_breakdown', {})
    if score_breakdown:
        st.write("**Score Breakdown:**")
        breakdown_cols = st.columns(4)
        breakdown_items = [
            ("Skills", score_breakdown.get('skills_score', 0)),
            ("Experience", score_breakdown.get('experience_score', 0)),
            ("Education", score_breakdown.get('education_score', 0)),
            ("Domain", score_breakdown.get('domain_score', 0))
        ]
        
        for i, (category, score) in enumerate(breakdown_items):
            with breakdown_cols[i]:
                st.metric(category, f"{score}/100")
    
    # Key insights
    col1, col2 = st.columns(2)
    
    with col1:
        strengths = feedback.get('strengths', [])
        if strengths:
            st.write("**Key Strengths:**")
            for strength in strengths[:5]:  # Show top 5
                st.write(f"• {strength}")
        
        matching_skills = feedback.get('matching_skills', [])
        if matching_skills:
            st.write("**Matching Skills:**")
            for skill in matching_skills[:8]:  # Show top 8
                st.write(f"• {skill}")
    
    with col2:
        concerns = feedback.get('concerns', [])
        if concerns:
            st.write("**Areas of Concern:**")
            for concern in concerns[:5]:  # Show top 5
                st.write(f"• {concern}")
        
        missing_skills = feedback.get('missing_skills', [])
        if missing_skills:
            st.write("**Missing Skills:**")
            for skill in missing_skills[:8]:  # Show top 8
                st.write(f"• {skill}")
    
    # Summary and recommendations
    summary = feedback.get('summary', '')
    if summary:
        st.write("**Executive Summary:**")
        st.write(summary)
    
    recommendations = feedback.get('recommendations', [])
    if recommendations:
        st.write("**Improvement Recommendations:**")
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            st.write(f"{i}. {rec}")
    
    # Show raw data in expander for debugging
    with st.expander("Raw Analysis Data (for debugging)"):
        st.json(feedback)

    # AI Chat Interface
    st.write("---")
    st.write("### Ask AI About This Scoring")
    st.write("Chat with the AI models to understand the scoring decisions, get career advice, or ask follow-up questions.")
    
    # Create a container with border for the entire chat interface
    with st.container(border=True):
        # Initialize chat history if not exists
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        st.info("**AI Chat**")
        
        # Create scoring context for AI
        scoring_context = f"""
        Recent resume scoring results:
        - Overall Score: {final_score}/100
        - Job Title: {result.get('job_title', 'N/A')}
        - Company: {result.get('company', 'N/A')}
        - Model Used: {result.get('model_used', 'N/A')}
        - Key Strengths: {', '.join(feedback.get('strengths', [])[:3])}
        - Main Concerns: {', '.join(feedback.get('concerns', [])[:3])}
        - Missing Skills: {', '.join(feedback.get('missing_skills', [])[:3])}
        """
        
        # Display chat history first (above input)
        if st.session_state.chat_history:
            st.write("**Chat History:**")
            
            # Create a scrollable container for chat history
            chat_container = st.container(height=300)
            with chat_container:
                # Show most recent chats first
                for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 chats
                    # User message
                    with st.chat_message("user"):
                        st.write(f"*{chat['timestamp']}*")
                        st.write(chat['question'])
                    
                    # AI response
                    model_name = "OpenAI" if chat['model'] == "openai" else "Gemini"
                    with st.chat_message("assistant"):
                        st.write(f"*{model_name}*")
                        st.write(chat['answer'])
        
        # Chat input at the bottom
        user_question = st.chat_input("Ask your question: Why did I get this score? How can I improve?")
        
        # Clear chat history button
        if st.button("Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Process AI chat when user submits a question
        if user_question and user_question.strip():
            with st.spinner("Getting AI response..."):
                chat_response = chat_with_ai(user_question, scoring_context)
                
                if chat_response and chat_response.get('success'):
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": user_question,
                        "answer": chat_response.get('response', ''),
                        "model": chat_response.get('model_used', 'openai'),
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Rerun to update chat display
                    st.rerun()

#footer
# st.write("---") --- IGNORE ---
st.caption("NOTE : make sure the LinkedIn job URLs in the format: https://www.linkedin.com/jobs/view/[job_id]")