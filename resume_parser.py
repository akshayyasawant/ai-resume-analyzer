import nltk

# Ensure stopwords are available for RAKE
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

from rake_nltk import Rake
import PyPDF2
import re
from typing import List, Dict

class ResumeParser:
    def __init__(self):
        """Generic Resume Parser using RAKE (keyword extraction)"""
        self.rake = Rake()  # for automatic keyword extraction

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\+\#\.\(\)]', ' ', text)
        return text.lower().strip()

    def extract_skills(self, text: str) -> List[str]:
        """Generic automatic keyword extraction using RAKE"""
        try:
            self.rake.extract_keywords_from_text(text)
            key_phrases = self.rake.get_ranked_phrases()
            # keep top 20 phrases, single or 2-word only
            filtered = [k.lower() for k in key_phrases if len(k.split()) <= 3][:20]
            return list(set(filtered))
        except Exception:
            return []

    def extract_experience_years(self, text: str) -> int:
        """Extract total experience years"""
        text = text.lower()
        years = []
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?',
            r'(\d+)\s*to\s*\d+\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?'
        ]
        for pattern in patterns:
            for m in re.findall(pattern, text):
                try:
                    y = int(m)
                    if 0 <= y <= 50:
                        years.append(y)
                except:
                    pass
        return max(years) if years else 0

    def parse_resume(self, pdf_file, filename: str) -> Dict:
        """Parse and structure resume information"""
        try:
            raw_text = self.extract_text_from_pdf(pdf_file)
            if raw_text.startswith("Error"):
                return {'filename': filename, 'error': raw_text}

            clean = self.clean_text(raw_text)
            skills = self.extract_skills(clean)
            exp = self.extract_experience_years(clean)

            return {
                'filename': filename,
                'raw_text': raw_text,
                'clean_text': clean,
                'skills': skills,
                'experience_years': exp,
                'error': None
            }
        except Exception as e:
            return {'filename': filename, 'error': str(e)}
