#!/usr/bin/env python3
"""
Exam Question Extraction CLI Tool
Main entry point for the CLI application.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.scraper import ExamScraper
from tools.extractor import QuestionExtractor
from tools.utils import setup_directories, print_success, print_error, print_info


def scrape_command(args):
    """Handle the scrape subcommand."""
    print_info(f"Starting scrape for subject: {args.subject}, topic: {args.topic}")
    
    # Setup directories
    setup_directories()
    
    scraper = ExamScraper()
    try:
        downloaded_files = scraper.scrape_papers(args.subject, args.topic)
        
        if downloaded_files:
            print_success(f"Successfully downloaded {len(downloaded_files)} papers:")
            for file_path in downloaded_files:
                print(f"  - {file_path}")
        else:
            print_info("No new papers were downloaded (may already exist)")
            
    except Exception as e:
        print_error(f"Scraping failed: {str(e)}")
        sys.exit(1)


def extract_command(args):
    """Handle the extract subcommand."""
    file_path = Path(args.file_path)
    
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        sys.exit(1)
    
    print_info(f"Extracting questions from: {file_path}")
    print_info(f"Topic filter: {args.topic}")
    
    # Setup directories
    setup_directories()
    
    extractor = QuestionExtractor()
    try:
        questions = extractor.extract_questions(
            file_path=str(file_path),
            topic=args.topic,
            use_llm=args.use_llm
        )
        
        if questions:
            print_success(f"Extracted {len(questions)} questions related to '{args.topic}'")
            
            # Print questions
            for i, question in enumerate(questions, 1):
                print(f"\n{i}. {question}")
            
            # Save to file if specified
            save_path = args.save_path or "outputs/questions.json"
            extractor.save_questions(questions, args.topic, args.subject, save_path)
            print_success(f"Questions saved to: {save_path}")
            
        else:
            print_info(f"No questions found related to '{args.topic}'")
            
    except Exception as e:
        print_error(f"Extraction failed: {str(e)}")
        sys.exit(1)


def pipeline_command(args):
    """Handle the pipeline subcommand (scrape + extract)."""
    print_info(f"Starting pipeline for subject: {args.subject}, topic: {args.topic}")
    
    # Setup directories
    setup_directories()
    
    # Step 1: Scrape papers
    print_info("Step 1: Scraping papers...")
    scraper = ExamScraper()
    try:
        downloaded_files = scraper.scrape_papers(args.subject, args.topic)
        
        if not downloaded_files:
            # Check if papers already exist
            data_dir = Path("data/raw_papers")
            existing_files = list(data_dir.glob("*.pdf"))
            if existing_files:
                print_info("Using existing papers from previous downloads")
                downloaded_files = [str(f) for f in existing_files]
            else:
                print_error("No papers found to process")
                sys.exit(1)
                
    except Exception as e:
        print_error(f"Scraping failed: {str(e)}")
        sys.exit(1)
    
    # Step 2: Extract questions from all downloaded papers
    print_info("Step 2: Extracting questions...")
    extractor = QuestionExtractor()
    all_questions = []
    
    try:
        for file_path in downloaded_files:
            if Path(file_path).suffix.lower() == '.pdf':
                print_info(f"Processing: {Path(file_path).name}")
                questions = extractor.extract_questions(
                    file_path=file_path,
                    topic=args.topic,
                    use_llm=args.use_llm
                )
                all_questions.extend(questions)
        
        if all_questions:
            print_success(f"Extracted {len(all_questions)} total questions related to '{args.topic}'")
            
            # Print questions
            for i, question in enumerate(all_questions, 1):
                print(f"\n{i}. {question}")
            
            # Save all questions
            save_path = "outputs/questions.json"
            extractor.save_questions(all_questions, args.topic, args.subject, save_path)
            print_success(f"All questions saved to: {save_path}")
            
        else:
            print_info(f"No questions found related to '{args.topic}' in any papers")
            
    except Exception as e:
        print_error(f"Question extraction failed: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract exam questions from academic papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape --subject "Mathematics" --topic "Linear Algebra"
  %(prog)s extract --file_path "data/raw_papers/2022_math_paper.pdf" --topic "Linear Algebra"
  %(prog)s pipeline --subject "Mathematics" --topic "Linear Algebra" --use_llm
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape subcommand
    scrape_parser = subparsers.add_parser('scrape', help='Scrape exam papers by subject and topic')
    scrape_parser.add_argument('--subject', required=True, help='Subject area (e.g., "Mathematics")')
    scrape_parser.add_argument('--topic', required=True, help='Specific topic (e.g., "Linear Algebra")')
    
    # Extract subcommand
    extract_parser = subparsers.add_parser('extract', help='Extract questions from a PDF file')
    extract_parser.add_argument('--file_path', required=True, help='Path to the PDF file')
    extract_parser.add_argument('--topic', required=True, help='Topic to filter questions')
    extract_parser.add_argument('--subject', default='Unknown', help='Subject area for metadata')
    extract_parser.add_argument('--use_llm', action='store_true', help='Use LLM for better extraction')
    extract_parser.add_argument('--save_path', help='Output file path (default: outputs/questions.json)')
    
    # Pipeline subcommand
    pipeline_parser = subparsers.add_parser('pipeline', help='Run complete pipeline (scrape + extract)')
    pipeline_parser.add_argument('--subject', required=True, help='Subject area (e.g., "Mathematics")')
    pipeline_parser.add_argument('--topic', required=True, help='Specific topic (e.g., "Linear Algebra")')
    pipeline_parser.add_argument('--use_llm', action='store_true', help='Use LLM for better extraction')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
    if args.command == 'scrape':
        scrape_command(args)
    elif args.command == 'extract':
        extract_command(args)
    elif args.command == 'pipeline':
        pipeline_command(args)


if __name__ == "__main__":
    main()