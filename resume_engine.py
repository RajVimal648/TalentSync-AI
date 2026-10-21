import re
import math
from collections import Counter
import pypdf

# Default Target Role Presets
ROLE_PRESETS = {
    "Software Developer": "Python Java SQL Git REST APIs Object-Oriented Data Structures Problem Solving Algorithms Unit Testing Docker CI/CD Agile Software Architecture Clean Code HTML CSS",
    "Full Stack Web Developer": "JavaScript React Node.js Express HTML5 CSS3 Tailwind CSS MongoDB REST APIs TypeScript Git Redux Webpack Web Performance Next.js Clean Code",
    "Python Backend Engineer": "Python Flask Django FastAPI PostgreSQL MySQL REST APIs Microservices PyTest Git OOP Docker Redis Data Structures Unit Testing ORM Celery Agile",
    "Java Enterprise Developer": "Java Spring Boot Hibernate MySQL PostgreSQL Microservices Maven JUnit REST APIs Object Oriented Design Git Docker Kafka Data Structures",
    "Data Analyst & BI Developer": "Python SQL Pandas NumPy Tableau Power BI Data Visualization Statistics Machine Learning Excel Analysis ETL Data Cleaning Database Queries Dashboards",
    "AI / ML & Data Science Engineer": "Python TensorFlow PyTorch Scikit-Learn Pandas NumPy Data Science NLP Computer Vision Machine Learning Deep Learning SQL Model Deployment Git",
    "DevOps & Cloud Engineer": "AWS Docker Kubernetes Terraform CI/CD Linux Shell Scripting Git Ansible Prometheus Cloud Security Microservices Monitoring Networking"
}

# Technical Skill Taxonomy
TECH_SKILLS_TAXONOMY = [
    "python", "java", "javascript", "html", "css", "sql", "mysql", "postgresql", "mongodb", "flask", "django", "fastapi",
    "react", "node", "tailwind", "express", "redux", "next.js", "git", "docker", "kubernetes", "aws", "terraform", "ansible",
    "tableau", "power bi", "pandas", "numpy", "statistics", "rest apis", "microservices", "spring boot", "hibernate", 
    "maven", "pytest", "unit testing", "agile", "data structures", "algorithms", "excel", "typescript", "c++", "linux", 
    "ci/cd", "clean code", "oop", "tensorflow", "pytorch", "scikit-learn", "nlp", "machine learning", "deep learning",
    "redis", "kafka", "etl"
]

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
    "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself",
    "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
    "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves"
}

def extract_text_from_pdf(pdf_file_or_stream):
    """
    Extracts text from a PDF file path or file stream using pypdf.
    """
    reader = pypdf.PdfReader(pdf_file_or_stream)
    full_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text.append(page_text)
    return "\n".join(full_text)

def tokenize(text):
    """
    Extracts lowercase word tokens, ignoring stopwords and non-alphanumeric characters.
    """
    words = re.findall(r'[a-zA-Z0-9\+\#\.\-]+', text.lower())
    tokens = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return tokens

def compute_tfidf_cosine_similarity(doc1, doc2):
    """
    Computes mathematical TF-IDF Cosine Similarity between doc1 and doc2.
    Formula: Cosine Similarity = (Vector A · Vector B) / (||Vector A|| × ||Vector B||)
    """
    tokens1 = tokenize(doc1)
    tokens2 = tokenize(doc2)
    
    if not tokens1 or not tokens2:
        return 0.0

    corpus = [tokens1, tokens2]
    num_docs = 2

    # Compute Document Frequency (DF)
    doc_freq = {}
    for doc in corpus:
        unique_tokens = set(doc)
        for token in unique_tokens:
            doc_freq[token] = doc_freq.get(token, 0) + 1

    # Vocabulary
    vocab = sorted(list(doc_freq.keys()))
    
    # Compute IDF with smoothing: log((1 + N) / (1 + df)) + 1
    idf = {}
    for token in vocab:
        idf[token] = math.log((1 + num_docs) / (1 + doc_freq[token])) + 1.0

    # Compute TF-IDF vectors
    def get_tfidf_vector(tokens):
        counts = Counter(tokens)
        total_tokens = len(tokens)
        vec = []
        for token in vocab:
            tf = counts.get(token, 0) / total_tokens
            tfidf = tf * idf[token]
            vec.append(tfidf)
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    vec1 = get_tfidf_vector(tokens1)
    vec2 = get_tfidf_vector(tokens2)

    # Dot product = Cosine similarity for L2-normalized vectors
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    similarity = max(0.0, min(1.0, dot_product))
    return similarity

def calculate_section_completeness(resume_text):
    """
    Checks for presence of standard resume sections:
    - Summary / Objective (25%)
    - Technical Skills (25%)
    - Projects / Experience (25%)
    - Education (25%)
    """
    text = resume_text.lower()
    has_summary = bool(re.search(r'\b(summary|objective|profile|about me|career summary)\b', text))
    has_skills = bool(re.search(r'\b(skill|skills|technologies|technical stack|competencies)\b', text))
    has_projects = bool(re.search(r'\b(project|projects|system|experience|work experience|employment)\b', text))
    has_edu = bool(re.search(r'\b(education|academic|bca|b\.tech|bachelor|degree|college|university)\b', text))

    score = 0
    if has_summary: score += 25
    if has_skills: score += 25
    if has_projects: score += 25
    if has_edu: score += 25

    return {
        'score': score,
        'has_summary': has_summary,
        'has_skills': has_skills,
        'has_projects': has_projects,
        'has_edu': has_edu
    }

def analyze_resume(resume_text, job_description, target_role="Software Developer"):
    """
    Performs complete Explainable NLP resume intelligence analysis.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")
    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # 1. Skill Extraction & Gap Detection
    detected_skills = []
    missing_skills = []
    skill_weights = []

    for skill in TECH_SKILLS_TAXONOMY:
        # Check presence using word boundary or phrase match
        escaped_skill = re.escape(skill)
        pattern = r'(?:\b|_)' + escaped_skill + r'(?:\b|_)'
        
        is_in_jd = bool(re.search(pattern, jd_lower))
        is_in_resume = bool(re.search(pattern, resume_lower))

        if is_in_jd:
            skill_name_upper = skill.upper()
            if is_in_resume:
                if skill_name_upper not in detected_skills:
                    detected_skills.append(skill_name_upper)
                    occurrences = len(re.findall(pattern, resume_lower))
                    weight = min(0.98, round(0.50 + (occurrences * 0.12), 2))
                    skill_weights.append({'skill': skill_name_upper, 'weight': weight, 'occurrences': occurrences})
            else:
                if skill_name_upper not in missing_skills:
                    missing_skills.append(skill_name_upper)

    # Detect custom keywords and role-specific terms from the Job Description
    jd_tokens = [w for w in tokenize(job_description) if len(w) > 2]
    for token in set(jd_tokens):
        token_upper = token.upper()
        if token_upper not in detected_skills and token_upper not in missing_skills:
            pattern = r'\b' + re.escape(token) + r'\b'
            occurrences = len(re.findall(pattern, resume_lower))
            if occurrences > 0 and len(detected_skills) < 18:
                detected_skills.append(token_upper)
                weight = min(0.95, round(0.42 + (occurrences * 0.11), 2))
                skill_weights.append({'skill': token_upper, 'weight': weight, 'occurrences': occurrences})
            elif len(missing_skills) < 10 and len(token) > 3:
                pattern = r'\b' + re.escape(token) + r'\b'
                if not re.search(pattern, resume_lower):
                    missing_skills.append(token_upper)

    # Fallback if no skills were explicitly extracted: search common terms in JD
    if not detected_skills and not missing_skills:
        jd_fallback = [w.upper() for w in tokenize(job_description) if len(w) > 3][:12]
        for term in jd_fallback:
            if term.lower() in resume_lower:
                detected_skills.append(term)
                skill_weights.append({'skill': term, 'weight': 0.60, 'occurrences': 1})
            else:
                missing_skills.append(term)

    # Sort skill weights by highest relevance
    skill_weights.sort(key=lambda x: x['weight'], reverse=True)

    # 2. Section Completeness
    section_info = calculate_section_completeness(resume_text)
    section_score = section_info['score']

    # 3. TF-IDF Cosine Similarity
    raw_similarity = compute_tfidf_cosine_similarity(resume_text, job_description)
    
    # Keyword overlap ratio
    total_req_keywords = len(detected_skills) + len(missing_skills)
    keyword_ratio = (len(detected_skills) / total_req_keywords) if total_req_keywords > 0 else 0.5

    # Blended TF-IDF score (Cosine similarity + Keyword match density)
    blended_tfidf = (raw_similarity * 0.5) + (keyword_ratio * 0.5)
    tfidf_score = min(100, max(10, round(blended_tfidf * 100)))

    # 4. Final ATS Score: Formula = (TF-IDF × 70%) + (Section Completeness × 30%)
    tfidf_contrib = round(tfidf_score * 0.7, 1)
    section_contrib = round(section_score * 0.3, 1)
    final_score = min(100, max(5, round(tfidf_contrib + section_contrib)))

    # 5. Quality & Formatting Diagnostics
    has_metrics = bool(re.search(r'\b\d+%\b|\b\d+\+\b|\b\d+\s*ms\b|\$\d+|\b\d+\s*(users|clients|requests|records)\b', resume_lower))
    has_categories = bool(re.search(r'\b(languages|frameworks|databases|tools|developer tools|platforms)\b', resume_lower))

    # Gap to 80% Benchmark
    gap_to_80 = max(0, 80 - final_score)

    # Dynamic Rewriting Sample Bullet Point for Selected Role
    top_missing = " & ".join(missing_skills[:2]) if missing_skills else "Docker & CI/CD"
    top_detected = detected_skills[0] if detected_skills else "Python"
    sample_bullet = f'• Replace generic lines with: "Architected high-throughput services using {top_detected} and {top_missing}, decreasing latency by 35% and improving automated test coverage to 92%."'

    return {
        'target_role': target_role,
        'final_score': final_score,
        'tfidf_score': tfidf_score,
        'section_score': section_score,
        'tfidf_contrib': tfidf_contrib,
        'section_contrib': section_contrib,
        'detected_skills': detected_skills,
        'missing_skills': missing_skills,
        'skill_weights': skill_weights,
        'sections': section_info,
        'has_metrics': has_metrics,
        'has_categories': has_categories,
        'gap_to_80': gap_to_80,
        'sample_bullet': sample_bullet
    }

