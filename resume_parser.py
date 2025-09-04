import PyPDF2
import re
from typing import List, Dict
import io

class ResumeParser:
    def __init__(self):
        """Initialize the resume parser without spaCy"""
        pass
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}\""
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\+\#\.\(\)]', ' ', text)
        text = text.lower().strip()
        return text
    
    def extract_skills(self, text: str) -> List[str]:
        """ENHANCED skill extraction specifically for Python Developer resumes"""
        found_skills = []
        text_lower = text.lower()
        
        # Core programming languages
        if re.search(r'\bpython\b', text_lower):
            found_skills.append('python')
        if re.search(r'\bjava(?!script)\b', text_lower):
            found_skills.append('java')
        if re.search(r'\bjavascript\b', text_lower):
            found_skills.append('javascript')
        if re.search(r'\bc\+\+\b', text_lower):
            found_skills.append('c++')
        if re.search(r'\bc#\b', text_lower):
            found_skills.append('c#')
        
        # Python frameworks (CRITICAL for the job)
        if re.search(r'\bdjango\b', text_lower):
            found_skills.append('django')
        if re.search(r'\bflask\b', text_lower):
            found_skills.append('flask')
        if re.search(r'\bfastapi\b', text_lower):
            found_skills.append('fastapi')
        
        # API Development (VERY IMPORTANT)
        if re.search(r'\brest\s*api\b|\brestful\b|\bapi\s*development\b', text_lower):
            found_skills.append('rest api')
        if re.search(r'\bapi\b', text_lower):
            found_skills.append('api')
        if re.search(r'\bmicroservices\b', text_lower):
            found_skills.append('microservices')
        
        # Database skills (REQUIRED)
        if re.search(r'\bsql\b', text_lower):
            found_skills.append('sql')
        if re.search(r'\bmysql\b', text_lower):
            found_skills.append('mysql')
        if re.search(r'\bpostgresql\b|\bpostgres\b', text_lower):
            found_skills.append('postgresql')
        if re.search(r'\bmongodb\b|\bmongo\b', text_lower):
            found_skills.append('mongodb')
        if re.search(r'\bsqlite\b', text_lower):
            found_skills.append('sqlite')
        if re.search(r'\bdatabase\b', text_lower):
            found_skills.append('database')
        
        # Version Control (REQUIRED)
        if re.search(r'\bgit\b', text_lower):
            found_skills.append('git')
        if re.search(r'\bgithub\b', text_lower):
            found_skills.append('github')
        if re.search(r'\bversion\s*control\b', text_lower):
            found_skills.append('version control')
        
        # Web technologies
        if re.search(r'\bhtml\b', text_lower):
            found_skills.append('html')
        if re.search(r'\bcss\b', text_lower):
            found_skills.append('css')
        if re.search(r'\breact\b', text_lower):
            found_skills.append('react')
        if re.search(r'\bangular\b', text_lower):
            found_skills.append('angular')
        if re.search(r'\bnode\.?js\b', text_lower):
            found_skills.append('nodejs')
        
        # DevOps and Cloud
        if re.search(r'\bdocker\b', text_lower):
            found_skills.append('docker')
        if re.search(r'\baws\b', text_lower):
            found_skills.append('aws')
        if re.search(r'\bazure\b', text_lower):
            found_skills.append('azure')
        if re.search(r'\blinux\b', text_lower):
            found_skills.append('linux')
        
        # Testing and Development Practices
        if re.search(r'\bunit\s*testing\b|\btesting\b', text_lower):
            found_skills.append('testing')
        if re.search(r'\bagile\b', text_lower):
            found_skills.append('agile')
        if re.search(r'\bscrum\b', text_lower):
            found_skills.append('scrum')
        
        # Soft skills (REQUIRED by job posting)
        if re.search(r'\bproblem.solving\b|\bproblem\s*solving\b|\bdebugging\b', text_lower):
            found_skills.append('problem solving')
        if re.search(r'\bteam\s*collaboration\b|\bcollaboration\b|\bteam\s*work\b|\bteam\s*player\b', text_lower):
            found_skills.append('collaboration')
        if re.search(r'\bcommunication\b', text_lower):
            found_skills.append('communication')
        if re.search(r'\bleadership\b|\bmentoring\b|\bmentor\b', text_lower):
            found_skills.append('leadership')
        
        # Data Science (bonus)
        if re.search(r'\bmachine\s*learning\b|\bml\b', text_lower):
            found_skills.append('machine learning')
        if re.search(r'\bpandas\b', text_lower):
            found_skills.append('pandas')
        if re.search(r'\bnumpy\b', text_lower):
            found_skills.append('numpy')
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience_years(self, text: str) -> int:
        """IMPROVED experience extraction with multiple patterns"""
        text_lower = text.lower()
        years = []
        
        # Pattern 1: Direct experience statements
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)(?:\s+in\s+python|\s+with\s+python)?',
            r'(\d+)\+?\s*years?\s*python',
            r'(\d+)\+?\s*years?\s*(?:in|with|using)\s*(?:python|development|programming)',
            r'(\d+)\+?\s*yr?s?\s*(?:experience|exp)',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?',
            r'(\d+)\s*to\s*\d+\s*years?\s*(?:experience|exp)',
            r'(\d+)\+\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    year_value = int(match)
                    if 0 <= year_value <= 50:  # Reasonable range
                        years.append(year_value)
                except ValueError:
                    continue
        
        # Pattern 2: Extract from work experience dates
        date_patterns = [
            r'(\d{4})\s*-\s*present',
            r'(\d{4})\s*-\s*(\d{4})',
            r'(\d{4})\s*to\s*present',
            r'(\d{4})\s*to\s*(\d{4})'
        ]
        
        current_year = 2024  # Adjust as needed
        work_years = []
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        if len(match) == 2 and match[1]:  # Start and end year
                            start_year, end_year = int(match[0]), int(match[1])
                            work_years.append(end_year - start_year)
                        elif len(match) == 2 and not match[1]:  # Start year to present
                            start_year = int(match[0])
                            work_years.append(current_year - start_year)
                        else:  # Single year to present
                            start_year = int(match[0])
                            work_years.append(current_year - start_year)
                    else:  # Single match to present
                        start_year = int(match)
                        work_years.append(current_year - start_year)
                except (ValueError, IndexError):
                    continue
        
        # Combine both methods and take the maximum reasonable value
        all_years = years + work_years
        valid_years = [y for y in all_years if 0 <= y <= 25]  # Max 25 years seems reasonable
        
        return max(valid_years) if valid_years else 0
    
    def parse_resume(self, pdf_file, filename: str) -> Dict:
        """Main function to parse resume and return structured data"""
        try:
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
            
            print(f"\n=== PARSING {filename} ===")
            print(f"Skills found: {skills}")
            print(f"Experience years: {experience_years}")
            print("=" * 40)
            
            return {
                'filename': filename,
                'raw_text': raw_text,
                'clean_text': clean_text,
                'skills': skills,
                'experience_years': experience_years,
                'error': None
            }
            
        except Exception as e:
            return {
                'filename': filename,
                'raw_text': '',
                'clean_text': '',
                'skills': [],
                'experience_years': 0,
                'error': f"Error parsing resume: {str(e)}"
            }
