"""
PDF question extractor with optional LLM enhancement.
"""

import PyPDF2
import re
import json
from pathlib import Path
from typing import List, Optional
import openai
import os
from .utils import print_info, print_success, print_error, print_progress


class QuestionExtractor:
    """Extracts questions from PDF files with topic filtering."""
    
    def __init__(self):
        self.llm_client = None
        self._setup_llm()
    
    def _setup_llm(self):
        """Setup LLM client if API key is available."""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.llm_client = openai
        else:
            print_info("OpenAI API key not found. LLM features will be disabled.")
    
    def extract_questions(self, file_path: str, topic: str, use_llm: bool = False) -> List[str]:
        """
        Extract questions from a PDF file filtered by topic.
        
        Args:
            file_path (str): Path to the PDF file
            topic (str): Topic to filter questions
            use_llm (bool): Whether to use LLM for better extraction
            
        Returns:
            List[str]: List of extracted questions
        """
        print_progress("Reading PDF content...")
        
        # Extract text from PDF
        text_content = self._extract_pdf_text(file_path)
        
        if not text_content:
            print_error("Failed to extract text from PDF")
            return []
        
        print_progress("Identifying questions...")
        
        # Extract questions using pattern matching
        questions = self._extract_questions_basic(text_content)
        
        # Filter by topic
        filtered_questions = self._filter_by_topic(questions, topic)
        
        # Enhance with LLM if requested and available
        if use_llm and self.llm_client and filtered_questions:
            print_progress("Enhancing questions with LLM...")
            filtered_questions = self._enhance_with_llm(filtered_questions, topic)
        
        return filtered_questions
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text_content += page.extract_text() + "\n"
                    except Exception as e:
                        print_error(f"Error reading page {page_num + 1}: {str(e)}")
                        continue
                
                return text_content
                
        except Exception as e:
            print_error(f"Error reading PDF {file_path}: {str(e)}")
            return ""
    
    def _extract_questions_basic(self, text: str) -> List[str]:
        """Extract questions using basic pattern matching."""
        questions = []
        
        # Common question patterns
        patterns = [
            r'^\s*\d+[\.\)]\s*.+\?',  # 1. Question?
            r'^\s*[A-Z]\)\s*.+\?',    # A) Question?
            r'^\s*Question\s+\d+[:\.]?\s*.+',  # Question 1: ...
            r'^\s*Q\d+[:\.]?\s*.+',   # Q1: ...
            r'^.+\?\s*$',             # Any line ending with ?
        ]
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Skip very short lines
                continue
                
            for pattern in patterns:
                if re.match(pattern, line, re.MULTILINE | re.IGNORECASE):
                    # Clean up the question
                    cleaned = self._clean_question(line)
                    if cleaned and len(cleaned) > 15:  # Ensure substantial content
                        questions.append(cleaned)
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for q in questions:
            if q not in seen:
                seen.add(q)
                unique_questions.append(q)
        
        return unique_questions
    
    def _clean_question(self, question: str) -> str:
        """Clean and format a question."""
        # Remove extra whitespace
        question = ' '.join(question.split())
        
        # Remove common prefixes
        prefixes = [r'^\d+[\.\)]\s*', r'^[A-Z]\)\s*', r'^Question\s+\d+[:\.]?\s*', r'^Q\d+[:\.]?\s*']
        for prefix in prefixes:
            question = re.sub(prefix, '', question, flags=re.IGNORECASE)
        
        return question.strip()
    
    def _filter_by_topic(self, questions: List[str], topic: str) -> List[str]:
        """Filter questions by relevance to the specified topic."""
        if not topic:
            return questions
        
        topic_words = topic.lower().split()
        filtered = []
        
        for question in questions:
            question_lower = question.lower()
            
            # Check if any topic words appear in the question
            if any(word in question_lower for word in topic_words):
                filtered.append(question)
            
            # Also check for related mathematical terms if it's a math topic
            if 'algebra' in topic.lower() and any(term in question_lower for term in ['matrix', 'vector', 'equation', 'system']):
                if question not in filtered:
                    filtered.append(question)
        
        return filtered
    
    def _enhance_with_llm(self, questions: List[str], topic: str) -> List[str]:
        """Use LLM to enhance and refine questions."""
        if not self.llm_client:
            print_info("LLM not available, skipping enhancement")
            return questions
        
        try:
            enhanced_questions = []
            
            for question in questions:
                prompt = f"""
                Analyze this exam question and determine if it's truly related to "{topic}". 
                If it is related, clean it up and make it more clear. 
                If it's not related, respond with "UNRELATED".
                
                Question: {question}
                
                Respond with either the cleaned question or "UNRELATED":
                """
                
                response = self.llm_client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.1
                )
                
                result = response.choices[0].message.content.strip()
                
                if result != "UNRELATED" and len(result) > 10:
                    enhanced_questions.append(result)
                
                time.sleep(0.5)  # Rate limiting
            
            print_success(f"LLM enhanced {len(enhanced_questions)} out of {len(questions)} questions")
            return enhanced_questions
            
        except Exception as e:
            print_error(f"LLM enhancement failed: {str(e)}")
            return questions
    
    def save_questions(self, questions: List[str], topic: str, subject: str, save_path: str):
        """Save questions to a JSON file."""
        output_dir = Path(save_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        data = {
            "subject": subject,
            "topic": topic,
            "question_count": len(questions),
            "extracted_at": str(Path().cwd()),
            "questions": questions
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print_error(f"Failed to save questions: {str(e)}")
            raise