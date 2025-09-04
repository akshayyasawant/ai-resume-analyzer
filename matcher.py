from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
import re

class ResumeJobMatcher:
    def __init__(self):
        """Initialize the matcher"""
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=3000,
            ngram_range=(1, 3),  # Include 1-3 word phrases
            min_df=1,
            max_df=0.95,
            token_pattern=r'\b\w+(?:\.\w+)*\b'  # Handle things like "node.js"
        )
    
    def preprocess_job_description(self, job_desc: str) -> str:
        """Preprocess job description for better matching"""
        # Clean and normalize text
        job_desc = re.sub(r'[^\w\s\-\+\#\.]', ' ', job_desc)
        job_desc = re.sub(r'\s+', ' ', job_desc)
        return job_desc.lower().strip()
    
    def extract_keywords_from_job(self, job_desc: str) -> Dict:
        """Extract important keywords from job description - IMPROVED"""
        clean_job = self.preprocess_job_description(job_desc)
        
        # Enhanced keyword patterns for the Python Developer job
        tech_keywords = []
        
        # Programming languages
        if re.search(r'\bpython\b', clean_job):
            tech_keywords.append('python')
        if re.search(r'\bjava(?!script)\b', clean_job):
            tech_keywords.append('java')
        if re.search(r'\bjavascript\b', clean_job):
            tech_keywords.append('javascript')
        
        # Frameworks - MORE SPECIFIC TO JOB
        if re.search(r'\bdjango\b', clean_job):
            tech_keywords.append('django')
        if re.search(r'\bflask\b', clean_job):
            tech_keywords.append('flask')
        
        # API Development
        if re.search(r'\brest\s*api\b|\brestful\b|\bapi\s*development\b', clean_job):
            tech_keywords.append('rest api')
            tech_keywords.append('api')
        
        # Databases
        if re.search(r'\bsql\b|\bdatabase\b', clean_job):
            tech_keywords.append('sql')
        if re.search(r'\bmysql\b', clean_job):
            tech_keywords.append('mysql')
        if re.search(r'\bpostgresql\b', clean_job):
            tech_keywords.append('postgresql')
        
        # Version Control
        if re.search(r'\bgit\b', clean_job):
            tech_keywords.append('git')
        
        # Soft skills
        if re.search(r'\bproblem.solving\b|\bproblem\s*solving\b', clean_job):
            tech_keywords.append('problem solving')
        if re.search(r'\bteam\s*collaboration\b|\bcollaboration\b|\bteam\s*work\b', clean_job):
            tech_keywords.append('collaboration')
        
        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*python',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        required_experience = 0
        for pattern in exp_patterns:
            matches = re.findall(pattern, clean_job)
            if matches:
                try:
                    required_experience = max(required_experience, int(matches[0]))
                except:
                    pass
        
        return {
            'keywords': tech_keywords,
            'required_experience': required_experience
        }
    
    def calculate_similarity_score(self, resumes: List[Dict], job_description: str) -> List[Dict]:
        """Calculate similarity scores - COMPLETELY REVAMPED"""
        
        job_keywords = self.extract_keywords_from_job(job_description)
        job_text = self.preprocess_job_description(job_description)
        
        print(f"Job keywords extracted: {job_keywords['keywords']}")
        print(f"Required experience: {job_keywords['required_experience']} years")
        
        resume_texts = []
        valid_resumes = []
        
        for resume in resumes:
            if resume['error'] is None and resume['clean_text']:
                resume_texts.append(resume['clean_text'])
                valid_resumes.append(resume)
        
        if not resume_texts:
            return []
        
        try:
            # Prepare all texts for TF-IDF
            all_texts = [job_text] + resume_texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            job_vector = tfidf_matrix[0:1]
            resume_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(job_vector, resume_vectors)[0]
            
            results = []
            for i, (resume, similarity) in enumerate(zip(valid_resumes, similarities)):
                
                print(f"\n--- Processing {resume['filename']} ---")
                print(f"Skills in resume: {resume['skills']}")
                print(f"Experience: {resume['experience_years']} years")
                
                # Enhanced scoring system
                keyword_score = self.calculate_enhanced_keyword_score(
                    resume, job_keywords['keywords']
                )
                
                experience_score = self.calculate_enhanced_experience_score(
                    resume['experience_years'], job_keywords['required_experience']
                )
                
                framework_bonus = self.calculate_framework_bonus(
                    resume['skills'], job_keywords['keywords']
                )
                
                # NEW SCORING WEIGHTS - More differentiated
                base_similarity = float(similarity)
                keyword_weight = 0.35
                experience_weight = 0.25
                framework_weight = 0.15
                similarity_weight = 0.25
                
                combined_score = (
                    base_similarity * similarity_weight +
                    keyword_score * keyword_weight +
                    experience_score * experience_weight +
                    framework_bonus * framework_weight
                )
                
                # Apply experience multiplier for Python specifically
                python_multiplier = self.get_python_experience_multiplier(
                    resume, job_keywords['required_experience']
                )
                combined_score *= python_multiplier
                
                print(f"Scores - Similarity: {base_similarity:.3f}, Keyword: {keyword_score:.3f}, "
                      f"Experience: {experience_score:.3f}, Framework: {framework_bonus:.3f}")
                print(f"Python multiplier: {python_multiplier:.3f}")
                print(f"Final combined score: {combined_score:.3f}")
                
                results.append({
                    'filename': resume['filename'],
                    'similarity_score': base_similarity,
                    'keyword_score': keyword_score,
                    'experience_score': experience_score,
                    'framework_score': framework_bonus,
                    'combined_score': combined_score,
                    'skills_found': resume['skills'],
                    'experience_years': resume['experience_years'],
                    'matching_keywords': self.find_matching_keywords(
                        resume['skills'], job_keywords['keywords']
                    )
                })
            
            # Sort by combined score
            results.sort(key=lambda x: x['combined_score'], reverse=True)
            return results
            
        except Exception as e:
            print(f"Error in similarity calculation: {str(e)}")
            return []
    
    def calculate_enhanced_keyword_score(self, resume: Dict, job_keywords: List[str]) -> float:
        """Enhanced keyword matching with weighted importance"""
        if not job_keywords:
            return 0.0
        
        resume_skills_lower = [skill.lower() for skill in resume['skills']]
        matches = 0
        total_weight = 0
        
        # Weighted keyword matching
        keyword_weights = {
            'python': 3.0,      # Most important
            'django': 2.5,      # Very important
            'flask': 2.5,       # Very important
            'rest api': 2.0,    # Important
            'api': 1.8,         # Important
            'sql': 2.0,         # Important
            'git': 1.5,         # Somewhat important
            'problem solving': 1.2,
            'collaboration': 1.0
        }
        
        for keyword in job_keywords:
            weight = keyword_weights.get(keyword, 1.0)
            total_weight += weight
            
            if keyword in resume_skills_lower:
                matches += weight
            elif keyword == 'rest api' and ('rest' in resume_skills_lower or 'api' in resume_skills_lower):
                matches += weight * 0.7  # Partial match
        
        return matches / total_weight if total_weight > 0 else 0.0
    
    def calculate_enhanced_experience_score(self, resume_exp: int, required_exp: int) -> float:
        """Enhanced experience scoring with better differentiation"""
        if required_exp == 0:
            return 0.8  # Some base score when no requirement specified
        
        if resume_exp >= required_exp * 1.5:
            return 1.0  # Significantly exceeds requirement
        elif resume_exp >= required_exp:
            return 0.9  # Meets requirement
        elif resume_exp >= required_exp * 0.8:
            return 0.7  # Close to requirement
        elif resume_exp >= required_exp * 0.5:
            return 0.5  # Somewhat close
        elif resume_exp > 0:
            return 0.3  # Some experience
        else:
            return 0.0  # No experience
    
    def calculate_framework_bonus(self, resume_skills: List[str], job_keywords: List[str]) -> float:
        """Bonus points for having both Django and Flask"""
        skills_lower = [skill.lower() for skill in resume_skills]
        
        has_django = 'django' in skills_lower
        has_flask = 'flask' in skills_lower
        has_both = has_django and has_flask
        
        django_in_job = 'django' in job_keywords
        flask_in_job = 'flask' in job_keywords
        
        if has_both and (django_in_job or flask_in_job):
            return 1.0  # Has both frameworks
        elif has_django and django_in_job:
            return 0.8
        elif has_flask and flask_in_job:
            return 0.8
        elif has_django or has_flask:
            return 0.4  # Has one framework
        else:
            return 0.0
    
    def get_python_experience_multiplier(self, resume: Dict, required_exp: int) -> float:
        """Multiplier based on Python experience vs requirement"""
        python_exp = resume['experience_years']
        
        if required_exp == 0:
            return 1.0
        
        if python_exp >= required_exp * 2:
            return 1.2  # Bonus for extensive experience
        elif python_exp >= required_exp:
            return 1.1  # Small bonus for meeting requirement
        elif python_exp >= required_exp * 0.6:
            return 1.0  # No penalty for being reasonably close
        else:
            return 0.8  # Penalty for being significantly under
    
    def find_matching_keywords(self, resume_skills: List[str], job_keywords: List[str]) -> List[str]:
        """Find matching keywords"""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        matches = []
        
        for keyword in job_keywords:
            if keyword.lower() in resume_skills_lower:
                matches.append(keyword)
        
        return matches
