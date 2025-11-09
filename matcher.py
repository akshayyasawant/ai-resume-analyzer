from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rake_nltk import Rake
import numpy as np
import re
from typing import List, Dict

class ResumeJobMatcher:
    def __init__(self):
        """Generic Matcher using TF-IDF + RAKE keyword extraction"""
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)
        self.rake = Rake()

    def preprocess(self, text: str) -> str:
        text = re.sub(r'[^\w\s\-\+\#\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()

    def extract_keywords(self, text: str) -> List[str]:
        """Automatically extract key terms from any job description"""
        self.rake.extract_keywords_from_text(text)
        keywords = [kw.lower() for kw in self.rake.get_ranked_phrases() if len(kw.split()) <= 3]
        return list(set(keywords[:20]))

    def get_required_experience(self, text: str) -> int:
        """Extract required years of experience"""
        text = text.lower()
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'at\s*least\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'over\s*(\d+)\s*years?'
        ]
        years = []
        for p in exp_patterns:
            for m in re.findall(p, text):
                try:
                    years.append(int(m))
                except:
                    pass
        return max(years) if years else 0

    def calculate_similarity_score(self, resumes: List[Dict], job_desc: str) -> List[Dict]:
        job_desc_clean = self.preprocess(job_desc)
        jd_keywords = self.extract_keywords(job_desc_clean)
        required_exp = self.get_required_experience(job_desc_clean)

        valid_resumes = [r for r in resumes if not r.get('error')]
        if not valid_resumes:
            return []

        # Vectorize JD + resumes
        texts = [job_desc_clean] + [r['clean_text'] for r in valid_resumes]
        tfidf = self.vectorizer.fit_transform(texts)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:])[0]

        results = []
        for res, sim in zip(valid_resumes, sims):
            keyword_score = self.keyword_match_score(res['skills'], jd_keywords)
            exp_score = self.experience_score(res['experience_years'], required_exp)
            combined = (sim * 0.4) + (keyword_score * 0.4) + (exp_score * 0.2)

            results.append({
                'filename': res['filename'],
                'similarity_score': sim,
                'keyword_score': keyword_score,
                'experience_score': exp_score,
                'combined_score': combined,
                'skills_found': res['skills'],
                'experience_years': res['experience_years'],
                'matching_keywords': self.matching_keywords(res['skills'], jd_keywords)
            })

        results.sort(key=lambda x: x['combined_score'], reverse=True)
        return results

    def keyword_match_score(self, resume_skills: List[str], jd_keywords: List[str]) -> float:
        if not jd_keywords:
            return 0.0
        resume_lower = [s.lower() for s in resume_skills]
        matches = sum(1 for k in jd_keywords if k in resume_lower)
        return matches / len(jd_keywords)

    def experience_score(self, resume_exp: int, required_exp: int) -> float:
        if required_exp == 0:
            return 0.8
        if resume_exp >= required_exp:
            return 1.0
        elif resume_exp >= 0.75 * required_exp:
            return 0.8
        elif resume_exp >= 0.5 * required_exp:
            return 0.6
        elif resume_exp > 0:
            return 0.4
        else:
            return 0.0

    def matching_keywords(self, resume_skills: List[str], jd_keywords: List[str]) -> List[str]:
        resume_lower = [s.lower() for s in resume_skills]
        return [kw for kw in jd_keywords if kw in resume_lower]
