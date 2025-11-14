"""
Web Tools Module
Web scraping, content extraction, and URL processing
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import re


class WebScraper:
    """Web scraping and content extraction"""

    def __init__(self):
        self.session = None

    async def fetch_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Fetch content from URL

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            Dict with content and metadata
        """
        try:
            import aiohttp

            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(url, timeout=timeout) as response:
                content = await response.text()
                status = response.status

                return {
                    'success': True,
                    'url': url,
                    'status': status,
                    'content': content,
                    'content_type': response.headers.get('Content-Type', 'unknown'),
                    'content_length': len(content)
                }

        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }

    async def extract_text(self, url: str) -> Dict[str, Any]:
        """
        Extract readable text from webpage

        Args:
            url: URL to extract text from

        Returns:
            Dict with extracted text
        """
        result = await self.fetch_url(url)

        if not result.get('success'):
            return result

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(result['content'], 'html.parser')

            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Get text
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Extract metadata
            title = soup.find('title')
            title = title.string if title else 'No title'

            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''

            return {
                'success': True,
                'url': url,
                'title': title,
                'description': description,
                'text': text,
                'text_length': len(text)
            }

        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }

    async def extract_links(self, url: str) -> Dict[str, Any]:
        """
        Extract all links from webpage

        Args:
            url: URL to extract links from

        Returns:
            Dict with list of links
        """
        result = await self.fetch_url(url)

        if not result.get('success'):
            return result

        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin

            soup = BeautifulSoup(result['content'], 'html.parser')

            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                links.append({
                    'text': link.get_text(strip=True),
                    'href': href,
                    'absolute_url': absolute_url
                })

            return {
                'success': True,
                'url': url,
                'num_links': len(links),
                'links': links
            }

        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }

    async def download_file(self, url: str, output_dir: str = "./data/downloads") -> Dict[str, Any]:
        """
        Download file from URL

        Args:
            url: File URL
            output_dir: Directory to save file

        Returns:
            Dict with download info
        """
        try:
            import aiohttp
            import os

            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Get filename from URL
            filename = url.split('/')[-1]
            if not filename or '.' not in filename:
                filename = 'downloaded_file'

            output_path = Path(output_dir) / filename

            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(url) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(await response.read())

                    return {
                        'success': True,
                        'url': url,
                        'output_path': str(output_path),
                        'file_size': os.path.getsize(output_path)
                    }
                else:
                    return {
                        'success': False,
                        'url': url,
                        'error': f'HTTP {response.status}'
                    }

        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }

    async def search_in_page(self, url: str, keyword: str) -> Dict[str, Any]:
        """
        Search for keyword in webpage

        Args:
            url: URL to search in
            keyword: Keyword to find

        Returns:
            Dict with search results
        """
        result = await self.extract_text(url)

        if not result.get('success'):
            return result

        text = result['text']
        keyword_lower = keyword.lower()
        text_lower = text.lower()

        # Find all occurrences
        count = text_lower.count(keyword_lower)

        # Extract context around keyword
        contexts = []
        start = 0
        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break

            # Get context (100 chars before and after)
            context_start = max(0, pos - 100)
            context_end = min(len(text), pos + len(keyword) + 100)
            context = text[context_start:context_end]

            contexts.append({
                'position': pos,
                'context': context.strip()
            })

            start = pos + 1

        return {
            'success': True,
            'url': url,
            'keyword': keyword,
            'count': count,
            'contexts': contexts[:10]  # Limit to 10 contexts
        }

    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
