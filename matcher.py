from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import numpy as np
import re
from typing import List, Dict

class ResumeJobMatcher:
    def __init__(self):
        """Initialize Sentence-BERT model and settings"""
        print("🔹 Initializing Sentence-BERT model for semantic similarity...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.results_history = []  # For adaptive learning

    # ----------------------------------------------
    # Basic Text Processing
    # ----------------------------------------------
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()

    # ----------------------------------------------
    # Keyword Extraction (simple heuristic)
    # ----------------------------------------------
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords by frequency"""
        words = [w for w in text.split() if w not in ENGLISH_STOP_WORDS and len(w) > 2]
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        sorted_keywords = sorted(freq, key=freq.get, reverse=True)
        return sorted_keywords[:50]  # top 50 keywords

    # ----------------------------------------------
    # Experience Extraction
    # ----------------------------------------------
    def extract_required_experience(self, text: str) -> int:
        """Extract years of experience required from JD"""
        text = text.lower()
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'at\s*least\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'(\d+)\s*to\s*\d+\s*years?',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    return int(matches[0])
                except:
                    continue
        return 0

    def calculate_experience_score(self, resume_exp: int, jd_exp: int) -> float:
        """Compute score for experience match"""
        if jd_exp == 0:
            return 0.8
        if resume_exp >= jd_exp * 1.5:
            return 1.0
        elif resume_exp >= jd_exp:
            return 0.9
        elif resume_exp >= jd_exp * 0.8:
            return 0.7
        elif resume_exp > 0:
            return 0.5
        else:
            return 0.0

    # ----------------------------------------------
    # Domain Detection
    # ----------------------------------------------
    def detect_job_domain(self, job_description: str) -> str:
        """Automatically detect job domain from JD keywords."""
        text = job_description.lower()

        domain_keywords = {
            "software": ["developer", "java", "python", "api", "software", "backend", "frontend", "full stack", "cloud"],
            "data": ["data", "machine learning", "ml", "ai", "analytics", "statistics", "deep learning", "model"],
            "marketing": ["seo", "campaign", "digital", "marketing", "brand", "social media", "advertising"],
            "finance": ["finance", "accounting", "budget", "investment", "tax", "auditing", "banking"],
            "hr": ["recruitment", "talent", "hiring", "employee", "human resources", "onboarding"],
            "design": ["ui", "ux", "design", "figma", "adobe", "illustrator", "photoshop", "creative"],
            "management": ["project", "manager", "leadership", "planning", "execution", "stakeholder"],
            "sales": ["sales", "customer", "lead", "target", "negotiation", "crm", "pipeline"],
        }

        detected_domain = "general"
        max_hits = 0

        for domain, keywords in domain_keywords.items():
            hits = sum(1 for kw in keywords if kw in text)
            if hits > max_hits:
                max_hits = hits
                detected_domain = domain

        print(f"🧭 Detected job domain: {detected_domain.upper()} ({max_hits} keyword matches)")
        return detected_domain

    # ----------------------------------------------
    # Self-Learning Heuristic Weight Tuning
    # ----------------------------------------------
    def auto_tune_weights(self):
        """Adjust scoring weights based on past results"""
        if not self.results_history:
            return 0.6, 0.3, 0.1  # Default

        top_scores = [r['combined_score'] for r in self.results_history[-5:]]
        avg_score = sum(top_scores) / len(top_scores)

        if avg_score < 0.4:
            print("⚙️ System detected low average scores → increasing semantic weight")
            return 0.7, 0.2, 0.1
        elif avg_score > 0.7:
            print("⚙️ High confidence → rebalancing toward keywords")
            return 0.55, 0.35, 0.1
        else:
            return 0.6, 0.3, 0.1

    # ----------------------------------------------
    # Core Matching Logic
    # ----------------------------------------------
    def calculate_similarity_score(self, resumes: List[Dict], job_description: str) -> List[Dict]:
        """Compute similarity using Sentence-BERT with domain-aware and adaptive scoring"""

        jd_clean = self.preprocess_text(job_description)
        jd_keywords = self.extract_keywords(jd_clean)
        jd_embedding = self.model.encode(jd_clean, convert_to_tensor=True)

        # 🧭 Detect job domain
        detected_domain = self.detect_job_domain(job_description)

        # 🧠 Auto-tuned base weights
        semantic_weight, keyword_weight, exp_weight = self.auto_tune_weights()

        # ⚙️ Adjust weights by JD length
        jd_word_count = len(jd_clean.split())
        if jd_word_count < 50:
            semantic_weight += 0.1
        elif jd_word_count > 150:
            keyword_weight += 0.05

        # ⚙️ Adjust by domain
        if detected_domain in ["software", "data"]:
            semantic_weight += 0.05
            keyword_weight += 0.1
        elif detected_domain in ["marketing", "sales"]:
            keyword_weight += 0.15
        elif detected_domain in ["finance", "hr"]:
            exp_weight += 0.1

        # Normalize weights
        total = semantic_weight + keyword_weight + exp_weight
        semantic_weight /= total
        keyword_weight /= total
        exp_weight /= total

        print(f"⚙️ Domain: {detected_domain} | Semantic: {semantic_weight:.2f}, Keyword: {keyword_weight:.2f}, Exp: {exp_weight:.2f}")

        results = []
        jd_word_freq = {w: jd_clean.count(w) for w in jd_keywords}

        for resume in resumes:
            if resume['error'] or not resume['clean_text']:
                continue

            resume_text = self.preprocess_text(resume['clean_text'])
            resume_keywords = self.extract_keywords(resume_text)
            resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)

            # --- Semantic similarity
            semantic_score = float(util.cos_sim(jd_embedding, resume_embedding)[0][0])

            # --- Keyword match (weighted)
            matching_keywords = set(resume_keywords).intersection(set(jd_keywords))
            keyword_weighted_score = sum(jd_word_freq.get(kw, 1) for kw in matching_keywords)
            keyword_score = keyword_weighted_score / (sum(jd_word_freq.values()) + 1e-6)

            # --- Experience relevance
            jd_exp = self.extract_required_experience(job_description)
            exp_score = self.calculate_experience_score(resume['experience_years'], jd_exp)

            # --- Final combined score
            combined_score = (
                semantic_score * semantic_weight +
                keyword_score * keyword_weight +
                exp_score * exp_weight
            )

            results.append({
                "filename": resume["filename"],
                "similarity_score": semantic_score,
                "keyword_score": keyword_score,
                "experience_score": exp_score,
                "combined_score": combined_score,
                "skills_found": resume["skills"],
                "experience_years": resume["experience_years"],
                "matching_keywords": list(matching_keywords),
            })

        results.sort(key=lambda x: x["combined_score"], reverse=True)
        self.results_history = results  # 🧠 store for adaptive tuning
        return results
