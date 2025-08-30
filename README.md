# Exam Question Extraction CLI

A powerful command-line tool for scraping exam papers and extracting questions based on subject and topic filters.

## Features

- **Smart Scraping**: Download exam papers filtered by subject and topic
- **Question Extraction**: Extract questions from PDFs with topic-specific filtering
- **LLM Enhancement**: Optional AI-powered question refinement
- **Pipeline Mode**: Complete workflow from scraping to extraction
- **Structured Output**: Save results as organized JSON files
- **Progress Tracking**: Real-time feedback on operations
- **Caching**: Avoid duplicate downloads

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up OpenAI API key for LLM features:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Commands

#### 1. Scrape Papers
Download exam papers by subject and topic:
```bash
python ag.py scrape --subject "Mathematics" --topic "Linear Algebra"
```

#### 2. Extract Questions
Extract questions from a specific PDF:
```bash
python ag.py extract --file_path "data/raw_papers/math_exam.pdf" --topic "Linear Algebra"
```

With LLM enhancement:
```bash
python ag.py extract --file_path "data/raw_papers/math_exam.pdf" --topic "Linear Algebra" --use_llm
```

Custom output path:
```bash
python ag.py extract --file_path "data/raw_papers/math_exam.pdf" --topic "Linear Algebra" --save_path "custom/output.json"
```

#### 3. Full Pipeline
Run complete workflow (scrape + extract):
```bash
python ag.py pipeline --subject "Mathematics" --topic "Linear Algebra"
```

With LLM enhancement:
```bash
python ag.py pipeline --subject "Mathematics" --topic "Linear Algebra" --use_llm
```

## Project Structure

```
backend/ai/agent/
├── ag.py              # Main CLI script
├── tools/
│   ├── __init__.py
│   ├── scraper.py     # Web scraping functionality
│   ├── extractor.py   # PDF question extraction
│   └── utils.py       # Helper functions
├── data/
│   └── raw_papers/    # Downloaded exam PDFs
├── outputs/
│   └── questions.json # Extracted questions
└── requirements.txt
```

## Output Format

Questions are saved in JSON format:

```json
{
  "subject": "Mathematics",
  "topic": "Linear Algebra",
  "question_count": 15,
  "extracted_at": "/path/to/project",
  "questions": [
    "What is the determinant of a 2x2 matrix?",
    "Solve the system of linear equations using Gaussian elimination.",
    "..."
  ]
}
```

## Features

- **Topic Filtering**: Only extracts questions relevant to the specified topic
- **Duplicate Prevention**: Automatically skips already downloaded papers
- **Error Handling**: Comprehensive error reporting and recovery
- **Progress Tracking**: Real-time feedback on long-running operations
- **Modular Design**: Clean separation of concerns for maintainability

## Requirements

- Python 3.7+
- Internet connection for scraping
- OpenAI API key (optional, for LLM features)