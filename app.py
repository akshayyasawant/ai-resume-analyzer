
import streamlit as st
import pandas as pd
from resume_parser import ResumeParser
from matcher import ResumeJobMatcher
from export_utils import ExportUtils
import plotly.graph_objects as go
import plotly.express as px
import setup_nltk

# Configure Streamlit page
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BEAUTIFUL BLACK/VIBRANT BLUE THEME
st.markdown("""
<style>
    /* Main app styling */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #ffffff;
    }
    
    /* Headers */
.main-header {
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 1rem;
}

/* Only apply gradient to the text inside span */
.gradient-text {
    background: linear-gradient(45deg, #00c6ff, #0072ff, #004cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(0, 198, 255, 0.3);
}

    .sub-header {
        font-size: 1.3rem;
        color: #b0b0b0;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        border-right: 2px solid #00c6ff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: #000000;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #0072ff, #004cff);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 198, 255, 0.4);
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: rgba(0, 198, 255, 0.1);
        border: 2px dashed #00c6ff;
        border-radius: 10px;
    }
    
    /* Text areas */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid #00c6ff;
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* Metrics */
    .metric-container {
        background: rgba(0, 198, 255, 0.1);
        border: 1px solid rgba(0, 198, 255, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(0, 198, 255, 0.1);
        border-radius: 5px;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(0, 198, 255, 0.2);
        border-left: 4px solid #00c6ff;
    }
    
    .stError {
        background: rgba(255, 69, 58, 0.2);
        border-left: 4px solid #ff453a;
    }
    
    /* Dividers */
    hr {
        border-color: #00c6ff;
        opacity: 0.3;
    }
    
    /* Container styling */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Chart backgrounds */
    .js-plotly-plot {
        background: transparent !important;
    }
    /* Job Description Box */
.job-description-box {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: white; /* plain white text */
}

/* Job Description text area */
textarea {
    background-color: rgba(255, 255, 255, 0.95) !important;
    color: black !important;
    font-size: 1.1rem !important;
    border-radius: 12px !important;
    border: 1px solid #ccc !important;
}

</style>
""", unsafe_allow_html=True)

def main():
    # Header with enhanced styling
# Header with enhanced styling
    st.markdown("""
    <h1 class="main-header">
    🤖 <span class="gradient-text">AI Resume Analyzer</span>
    </h1>
""", unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent resume analysis with advanced NLP and machine learning</p>', unsafe_allow_html=True)
    
    # Initialize components
    if 'parser' not in st.session_state:
        st.session_state.parser = ResumeParser()
        st.session_state.matcher = ResumeJobMatcher()
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("## 🎯 Quick Start Guide")
        st.markdown("""
        **Step 1:** Upload PDF resumes  
        **Step 2:** Enter job description  
        **Step 3:** Click Analyze  
        **Step 4:** Download results  
        """)
        
        st.markdown("---")
        st.markdown("## ⚡ Advanced Features")
        st.markdown("""
        ✨ **Smart Parsing** - PDF text extraction  
        🧠 **TF-IDF Analysis** - Semantic matching  
        🎯 **Keyword Scoring** - Skill alignment  
        📊 **Experience Weighting** - Years-based ranking  
        📈 **Visual Analytics** - Interactive charts  
        💾 **Multi-format Export** - Excel & CSV  
        """)
        
        
    
    # Main content area with enhanced layout
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📁 Upload Resumes")
        uploaded_files = st.file_uploader(
            "Drop your PDF files here or click to browse",
            type=['pdf'],
            accept_multiple_files=True,
            help="💡 Tip: Upload multiple resumes for batch processing"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} resume(s) ready for analysis")
            
            # Enhanced file preview
            with st.expander("📋 View uploaded files", expanded=True):
                for i, file in enumerate(uploaded_files, 1):
                    st.markdown(f"**{i}.** `{file.name}` ({file.size:,} bytes)")
    
    with col2:
        st.markdown("### 📝 Job Description")
        job_description = st.text_area(
            "Paste the complete job description",
            height=220,
            placeholder="""Example:
Python Developer Position
Requirements: 3+ years Python experience, Django or Flask framework, 
REST API development, SQL databases, Git version control, 
problem-solving skills, team collaboration...
            """,
            help="💡 Include all technical requirements and qualifications"
        )
    
    # Enhanced analysis button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🚀 Analyze Resumes", 
            type="primary", 
            use_container_width=True,
            help="Start intelligent resume analysis"
        )
    
    if analyze_button:
        if not uploaded_files:
            st.error("⚠️ Please upload at least one resume")
        elif not job_description.strip():
            st.error("⚠️ Please enter a job description")
        else:
            analyze_resumes(uploaded_files, job_description)

def analyze_resumes(uploaded_files, job_description):
    """Enhanced analysis function with better progress tracking"""
    
    # Create progress tracking
    progress_container = st.container()
    with progress_container:
        st.markdown("### 🔄 Analysis in Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        step_info = st.empty()
    
    try:
        # Step 1: Parse resumes
        status_text.success("📄 Parsing resumes...")
        step_info.info(f"Processing {len(uploaded_files)} resume(s)")
        parsed_resumes = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            uploaded_file.seek(0)
            
            try:
                parsed_resume = st.session_state.parser.parse_resume(
                    uploaded_file, uploaded_file.name
                )
                parsed_resumes.append(parsed_resume)
            except Exception as e:
                st.error(f"❌ Error parsing {uploaded_file.name}: {str(e)}")
                # We can't continue if a file fails to parse.
                return
            
            progress = (i + 1) / len(uploaded_files) * 0.6
            progress_bar.progress(progress)
            step_info.info(f"Parsed: {uploaded_file.name}")
        
        # Step 2: Calculate similarity scores
        status_text.success("🧮 Calculating similarity scores...")
        step_info.info("Running TF-IDF analysis and keyword matching")
        results = st.session_state.matcher.calculate_similarity_score(
            parsed_resumes, job_description
        )
        progress_bar.progress(1.0)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        step_info.empty()
        
        if not results:
            st.error("❌ No valid resumes found for analysis")
            return
        
        # Display results with enhanced styling
        display_enhanced_results(results, job_description)
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.exception(e)
        progress_bar.empty()
        status_text.empty()
        step_info.empty()

def display_enhanced_results(results, job_description):
    """Display results with beautiful styling and enhanced metrics"""
    
    st.markdown("---")
    st.markdown("# 🏆 Analysis Results")
    
    # Enhanced summary statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📊 Total Candidates", 
            len(results),
            help="Number of resumes analyzed"
        )
    
    with col2:
        avg_score = sum(r['combined_score'] for r in results) / len(results)
        st.metric(
            "📈 Average Score", 
            f"{avg_score:.3f}",
            help="Mean combined score across all candidates"
        )
    
    with col3:
        top_score = results[0]['combined_score'] if results else 0
        st.metric(
            "🥇 Highest Score", 
            f"{top_score:.3f}",
            help="Best performing candidate score"
        )
    
    with col4:
        qualified_candidates = len([r for r in results if r['combined_score'] > 0.7])
        st.metric(
            "✅ Highly Qualified", 
            qualified_candidates,
            help="Candidates with score > 0.7"
        )
    
    with col5:
        score_range = max(r['combined_score'] for r in results) - min(r['combined_score'] for r in results)
        st.metric(
            "📊 Score Range", 
            f"{score_range:.3f}",
            help="Difference between highest and lowest scores"
        )
    
    # Enhanced visualization
    st.markdown("### 📈 Interactive Score Analysis")
    
    # Create enhanced bar chart
    fig = go.Figure()
    
    candidate_names = [r['filename'].replace('.pdf', '') for r in results]
    scores = [r['combined_score'] for r in results]
    
    # Color gradient based on score
    colors = []
    for score in scores:
        if score >= 0.8:
            colors.append('#00c6ff')  # Vibrant blue for excellent
        elif score >= 0.6:
            colors.append('#0072ff')  # Medium blue for good
        elif score >= 0.4:
            colors.append('#ffd700')  # Yellow for average
        else:
            colors.append('#ff6b6b')  # Red for below average
    
    fig.add_trace(go.Bar(
        x=candidate_names,
        y=scores,
        marker_color=colors,
        text=[f"{score:.3f}" for score in scores],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>',
        marker_line=dict(color='rgba(0, 198, 255, 0.6)', width=2)
    ))
    
    fig.update_layout(
        title={
            'text': "🎯 Resume Ranking Scores",
            'font': {'size': 24, 'color': '#00c6ff'},
            'x': 0.5
        },
        xaxis_title="Candidates",
        yaxis_title="Combined Score",
        xaxis_tickangle=-45,
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        xaxis=dict(gridcolor='rgba(0, 198, 255, 0.2)'),
        yaxis=dict(gridcolor='rgba(0, 198, 255, 0.2)')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results with enhanced styling
    st.markdown("### 🏅 Detailed Candidate Rankings")
    
    for i, result in enumerate(results):
        # Color coding based on rank
        if i == 0:
            rank_color = "🥇"
            container_class = "gold"
        elif i == 1:
            rank_color = "🥈"
            container_class = "silver"
        elif i == 2:
            rank_color = "🥉"
            container_class = "bronze"
        else:
            rank_color = f"#{i+1}"
            container_class = "default"
        
        with st.container():
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(0, 198, 255, 0.1), rgba(0, 114, 255, 0.05));
                border: 1px solid rgba(0, 198, 255, 0.3);
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 20px rgba(0, 198, 255, 0.1);
            ">
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {rank_color} {result['filename'].replace('.pdf', '')}")
                
                # Enhanced score breakdown
                score_col1, score_col2, score_col3, score_col4 = st.columns(4)
                with score_col1:
                    st.metric("🎯 Combined", f"{result['combined_score']:.3f}")
                with score_col2:
                    st.metric("🔍 Similarity", f"{result['similarity_score']:.3f}")
                with score_col3:
                    st.metric("🎪 Keywords", f"{result['keyword_score']:.3f}")
                with score_col4:
                    st.metric("⚡ Framework", f"{result.get('framework_score', 0):.3f}")
                
                # Skills and keywords with better formatting
                if result['matching_keywords']:
                    keywords_str = " • ".join([f"`{kw}`" for kw in result['matching_keywords']])
                    st.markdown(f"**🎯 Matching Keywords:** {keywords_str}")
                else:
                    st.markdown("**🎯 Matching Keywords:** *None found*")
                
                if result['skills_found']:
                    skills_str = " • ".join([f"`{skill}`" for skill in result['skills_found'][:10]])
                    st.markdown(f"**🛠️ Skills Found:** {skills_str}")
                    if len(result['skills_found']) > 10:
                        st.markdown(f"*...and {len(result['skills_found']) - 10} more*")
                else:
                    st.markdown("**🛠️ Skills Found:** *None detected*")
            
            with col2:
                st.markdown("**📊 Experience**")
                st.markdown(f"**{result['experience_years']}** years")
                
                st.markdown("**📈 Score Progress**")
                st.progress(min(result['combined_score'], 1.0))
                
                # Quality indicator
                score = result['combined_score']
                if score >= 0.8:
                    st.success("Excellent Match")
                elif score >= 0.6:
                    st.info("Good Match")
                elif score >= 0.4:
                    st.warning("Average Match")
                else:
                    st.error("Poor Match")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        if i < len(results) - 1:  # Don't add divider after last item
            st.markdown("---")
    
    # Enhanced export section
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        excel_data = ExportUtils.export_to_excel(results)
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_data,
            file_name="resume_rankings.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Complete analysis in Excel format"
        )
    
    with col2:
        csv_data = ExportUtils.export_to_csv(results)
        st.download_button(
            label="📄 Download CSV Data",
            data=csv_data,
            file_name="resume_rankings.csv",
            mime="text/csv",
            use_container_width=True,
            help="Raw data in CSV format"
        )
    
    with col3:
        # Generate summary report
        summary_report = generate_summary_report(results, job_description)
        st.download_button(
            label="📋 Download Summary",
            data=summary_report,
            file_name="analysis_summary.txt",
            mime="text/plain",
            use_container_width=True,
            help="Executive summary report"
        )

def generate_summary_report(results, job_description):
    """Generate a text summary report"""
    report = f"""
RESUME ANALYSIS SUMMARY REPORT
==============================

Job Description Analysis:
- Total candidates analyzed: {len(results)}
- Average score: {sum(r['combined_score'] for r in results) / len(results):.3f}
- Top performer: {results[0]['filename'].replace('.pdf', '')} (Score: {results[0]['combined_score']:.3f})

TOP 5 CANDIDATES:
"""
    
    for i, result in enumerate(results[:5]):
        report += f"""
{i+1}. {result['filename'].replace('.pdf', '')}
   Combined Score: {result['combined_score']:.3f}
   Experience: {result['experience_years']} years
   Key Skills: {', '.join(result['skills_found'][:5])}
   Matching Keywords: {', '.join(result['matching_keywords'])}
"""
    
    report += f"""

ANALYSIS INSIGHTS:
- Highly qualified candidates (>0.7): {len([r for r in results if r['combined_score'] > 0.7])}
- Good candidates (0.5-0.7): {len([r for r in results if 0.5 <= r['combined_score'] <= 0.7])}
- Average candidates (<0.5): {len([r for r in results if r['combined_score'] < 0.5])}

Generated by AI Resume Screener
"""
    
    return report

if __name__ == "__main__":
    main()
