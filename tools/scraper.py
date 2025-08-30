"""
Web scraper for exam papers based on subject and topic.
"""

import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
from .utils import print_info, print_success, print_error, print_progress


class ExamScraper:
    """Handles scraping of exam papers from academic sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.download_dir = Path("data/raw_papers")
        
    def scrape_papers(self, subject, topic):
        """
        Scrape exam papers based on subject and topic.
        
        Args:
            subject (str): The subject area to search for
            topic (str): The specific topic within the subject
            
        Returns:
            list: List of downloaded file paths
        """
        downloaded_files = []
        
        # Create download directory if it doesn't exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Search for papers using multiple strategies
        search_urls = self._generate_search_urls(subject, topic)
        
        for url in search_urls:
            try:
                print_info(f"Searching: {url}")
                papers = self._search_papers(url, subject, topic)
                
                for paper_info in papers:
                    file_path = self._download_paper(paper_info)
                    if file_path:
                        downloaded_files.append(file_path)
                        
            except Exception as e:
                print_error(f"Error searching {url}: {str(e)}")
                continue
        
        return downloaded_files
    
    def _generate_search_urls(self, subject, topic):
        """Generate search URLs for different academic sources."""
        # This is a simplified example - in practice, you'd use actual academic databases
        base_urls = [
            f"https://example-academic-site.com/search?q={subject}+{topic}+exam",
            f"https://papers.example.com/search?subject={subject}&topic={topic}",
        ]
        return base_urls
    
    def _search_papers(self, search_url, subject, topic):
        """
        Search for papers on a given URL.
        
        Returns:
            list: List of paper info dictionaries
        """
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            papers = []
            
            # Look for PDF links (this is a simplified example)
            pdf_links = soup.find_all('a', href=True)
            
            for link in pdf_links:
                href = link.get('href')
                if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                    # Filter by subject and topic in the link text or URL
                    link_text = link.get_text().lower()
                    href_lower = href.lower()
                    
                    if (subject.lower() in link_text or subject.lower() in href_lower) and \
                       (topic.lower() in link_text or topic.lower() in href_lower):
                        
                        full_url = urljoin(search_url, href)
                        papers.append({
                            'url': full_url,
                            'title': link.get_text().strip() or f"{subject}_{topic}_paper",
                            'subject': subject,
                            'topic': topic
                        })
            
            return papers[:5]  # Limit to 5 papers per search
            
        except requests.RequestException as e:
            print_error(f"Failed to search {search_url}: {str(e)}")
            return []
    
    def _download_paper(self, paper_info):
        """
        Download a paper if it doesn't already exist.
        
        Args:
            paper_info (dict): Paper information including URL and title
            
        Returns:
            str: Path to downloaded file or None if failed
        """
        # Generate filename
        safe_title = "".join(c for c in paper_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"{safe_title}.pdf"
        file_path = self.download_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            print_info(f"File already exists: {filename}")
            return str(file_path)
        
        try:
            print_progress(f"Downloading: {filename}")
            
            response = self.session.get(paper_info['url'], timeout=30)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and len(response.content) < 1000:
                print_error(f"Invalid PDF content for {filename}")
                return None
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print_success(f"Downloaded: {filename} ({len(response.content)} bytes)")
            time.sleep(1)  # Be respectful to servers
            
            return str(file_path)
            
        except Exception as e:
            print_error(f"Failed to download {paper_info['url']}: {str(e)}")
            return None