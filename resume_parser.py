# import fitz  # PyMuPDF
# import re
# from typing import List, Dict


# class ResumeParser:
#     def __init__(self):
#         """Smart Resume Parser - domain-independent"""
#         pass

#     # =============================
#     # TEXT EXTRACTION
#     # =============================
#     def extract_text_from_pdf(self, pdf_file) -> str:
#         """Extract text from PDF using PyMuPDF (handles layouts, avoids junk)"""
#         try:
#             pdf_bytes = pdf_file.read()
#             with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
#                 text = ""
#                 for page in doc:
#                     text += page.get_text("text") + "\n"
#             return text.strip()
#         except Exception as e:
#             return f"Error reading PDF: {str(e)}"

#     # =============================
#     # TEXT CLEANING
#     # =============================
#     def clean_text(self, text: str) -> str:
#         """Clean and normalize text"""
#         text = re.sub(r'\s+', ' ', text)
#         text = re.sub(r'[^A-Za-z0-9\+\#\.\-\(\) ]', ' ', text)
#         text = re.sub(r'(?<=\w)([A-Z])', r' \1', text)  # Split CamelCase words
#         return text.lower().strip()

#     # =============================
#     # SKILL EXTRACTION (multi-domain)
#     # =============================
#     def extract_skills(self, text: str) -> List[str]:
#         """Extract keywords & skills from resume text (generic, multi-domain)"""
#         text_lower = text.lower()

#         # --- Universal Skills List ---
#         skills = {
#             # 🧩 Programming Languages
#             "python", "java", "javascript", "typescript", "c++", "c#", "go", "swift", "kotlin", "php", "r", "scala",

#             # ⚙️ Frameworks / Libraries
#             "django", "flask", "fastapi", "spring", "hibernate", "react", "angular", "vue", "node", "express", ".net", "dotnet",
#             "nextjs", "laravel", "tailwind", "bootstrap",

#             # 🤖 AI / ML / Data
#             "machine learning", "deep learning", "data science", "artificial intelligence", "nlp",
#             "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
#             "seaborn", "keras", "huggingface", "openai", "transformers",

#             # 🧮 Databases
#             "mysql", "postgresql", "mongodb", "oracle", "sqlite", "sql server", "redis", "nosql", "elasticsearch",

#             # ☁️ Cloud / DevOps
#             "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",
#             "git", "github", "gitlab", "ci/cd", "linux", "bash", "shell scripting",

#             # 📊 Data / BI Tools
#             "excel", "tableau", "power bi", "snowflake", "hadoop", "spark", "bigquery", "databricks",

#             # 🧠 Testing / Automation
#             "selenium", "pytest", "unittest", "junit", "cypress", "postman", "api testing",

#             # 💼 Project Management & Soft Skills
#             "agile", "scrum", "jira", "communication", "leadership", "collaboration",
#             "problem solving", "teamwork", "time management", "analytical thinking",
#         }

#         found = [skill for skill in skills if skill in text_lower]
#         return list(set(found))

#     # =============================
#     # EXPERIENCE DETECTION
#     # =============================
#     def extract_experience_years(self, text: str) -> int:
#         """Extracts years of experience using regex"""
#         text_lower = text.lower()
#         patterns = [
#             r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
#             r'(\d+)\s*-\s*(\d+)\s*years?',
#             r'at\s*least\s*(\d+)\s*years?',
#             r'more\s*than\s*(\d+)\s*years?',
#         ]
#         years = []

#         for pattern in patterns:
#             matches = re.findall(pattern, text_lower)
#             for match in matches:
#                 try:
#                     if isinstance(match, tuple):
#                         start, end = map(int, match)
#                         years.append(end - start)
#                     else:
#                         years.append(int(match))
#                 except:
#                     continue

#         valid = [y for y in years if 0 <= y <= 40]
#         return max(valid) if valid else 0

#     # =============================
#     # MAIN PARSER
#     # =============================
#     def parse_resume(self, pdf_file, filename: str) -> Dict:
#         """Main function to process resume"""
#         try:
#             raw_text = self.extract_text_from_pdf(pdf_file)
#             if raw_text.startswith("Error"):
#                 return {
#                     "filename": filename,
#                     "raw_text": "",
#                     "clean_text": "",
#                     "skills": [],
#                     "experience_years": 0,
#                     "error": raw_text
#                 }

#             clean_text = self.clean_text(raw_text)
#             skills = self.extract_skills(clean_text)
#             experience = self.extract_experience_years(clean_text)

#             print(f"Parsed: {filename} | Skills: {skills} | Experience: {experience} yrs")

#             return {
#                 "filename": filename,
#                 "raw_text": raw_text,
#                 "clean_text": clean_text,
#                 "skills": skills,
#                 "experience_years": experience,
#                 "error": None
#             }

#         except Exception as e:
#             return {
#                 "filename": filename,
#                 "raw_text": "",
#                 "clean_text": "",
#                 "skills": [],
#                 "experience_years": 0,
#                 "error": f"Error parsing resume: {str(e)}"
#             }


import fitz  # PyMuPDF
import re
from typing import List, Dict
import nltk

# 🧠 Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class ResumeParser:
    """Universal Resume Parser using PyMuPDF for clean text extraction"""

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        print("✅ ResumeParser initialized successfully with NLTK stopwords.")

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF using PyMuPDF (more accurate than PyPDF2)"""
        text = ""
        try:
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
            for page in pdf_document:
                text += page.get_text("text") + "\n"
            pdf_document.close()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
        return text.strip()

    def clean_text(self, text: str) -> str:
        """Basic cleaning: remove extra spaces, normalize"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\+\#\.\(\)]', ' ', text)
        text = text.lower().strip()
        return text

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract potential technical and soft skills dynamically.
        This is a generalized extractor for all domains.
        """
        text = text.lower()
        tokens = [t for t in word_tokenize(text) if t.isalpha() and t not in self.stop_words]

        # Common technical terms and soft skills (expandable list)
        possible_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'sql', 'mysql', 'mongodb', 'html', 'css', 'react',
            'nodejs', 'angular', 'aws', 'azure', 'docker', 'flask', 'django', 'git', 'linux',
            'machine learning', 'data analysis', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
            'excel', 'powerbi', 'tableau', 'jira', 'project management', 'leadership', 'communication',
            'problem solving', 'teamwork', 'collaboration', 'design', 'testing', 'debugging', 'cloud',
            'api', 'ui', 'ux', 'finance', 'marketing', 'sales', 'customer service', 'recruitment'
        ]

        found_skills = [skill for skill in possible_skills if skill in text]
        # Add any capitalized technical keywords automatically (dynamic detection)
        auto_detected = [token for token in tokens if token.isalpha() and len(token) > 2]
        final_skills = list(set(found_skills + auto_detected))

        return final_skills

    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from text"""
        text = text.lower()
        years = []

        # Pattern 1: "3 years of experience", "5+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?',
            r'(\d+)\s*to\s*\d+\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                try:
                    year = int(m)
                    if 0 <= year <= 50:
                        years.append(year)
                except ValueError:
                    continue

        # Pattern 2: Infer from date ranges
        date_patterns = [
            r'(\d{4})\s*[-to]+\s*(\d{4}|present)',
            r'(\d{4})\s*[-to]+\s*(\d{2})'
        ]

        current_year = 2024
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    start_year = int(match[0])
                    end_year = current_year if 'present' in match[1] else int(match[1])
                    diff = end_year - start_year
                    if 0 < diff <= 30:
                        years.append(diff)
                except Exception:
                    continue

        return max(years) if years else 0

    def parse_resume(self, pdf_file, filename: str) -> Dict:
        """Main parsing function"""
        raw_text = self.extract_text_from_pdf(pdf_file)
        if raw_text.startswith("Error"):
            return {
                'filename': filename,
                'raw_text': '',
                'clean_text': '',
                'skills': [],
                'experience_years': 0,
                'error': raw_text
            }

        clean_text = self.clean_text(raw_text)
        skills = self.extract_skills(raw_text)
        experience_years = self.extract_experience_years(raw_text)

        print(f"\n📄 Parsed {filename}")
        print(f"🧠 Skills Detected: {skills[:10]}... ({len(skills)} total)")
        print(f"⏳ Experience: {experience_years} years\n")

        return {
            'filename': filename,
            'raw_text': raw_text,
            'clean_text': clean_text,
            'skills': skills,
            'experience_years': experience_years,
            'error': None
        }
