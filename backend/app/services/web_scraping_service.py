"""
Web scraping service for extracting content from URLs.

This module provides functionality for fetching and extracting
text content from web pages.
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class WebScrapingService:
    """
    Service class for handling web content extraction.

    This class manages URL fetching, content parsing, and text extraction
    from web pages.
    """

    DEFAULT_TIMEOUT = 30
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB
    USER_AGENT = "Mozilla/5.0 (compatible; ProposalBot/1.0)"

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the web scraping service.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def extract_content_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract text content from a URL.

        Args:
            url: The URL to extract content from

        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                raise ValueError(f"Invalid URL: {url}")

            # Fetch content
            html_content = await self._fetch_url_content(url)

            # Parse and extract text
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_text_content(soup)

            result = {
                "url": url,
                "title": title,
                "content": content,
                "status": "success",
                "content_length": len(content),
            }

            logger.info(f"Successfully extracted content from URL: {url}")
            return result

        except Exception as e:
            logger.error(f"Error extracting content from URL {url}: {str(e)}")
            return {
                "url": url,
                "title": None,
                "content": "",
                "status": "error",
                "error": str(e),
            }

    async def _fetch_url_content(self, url: str) -> str:
        """
        Fetch HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string
        """
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")

                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > self.MAX_CONTENT_LENGTH:
                    raise Exception(f"Content too large: {content_length} bytes")

                content = await response.text()

                if len(content) > self.MAX_CONTENT_LENGTH:
                    raise Exception(f"Content too large: {len(content)} bytes")

                return content

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract title from HTML soup.

        Args:
            soup: BeautifulSoup object

        Returns:
            Extracted title or None
        """
        # Try different title sources
        title_sources = [
            soup.find("title"),
            soup.find("h1"),
            soup.find("meta", attrs={"property": "og:title"}),
            soup.find("meta", attrs={"name": "title"}),
        ]

        for source in title_sources:
            if source:
                if source.name == "meta":
                    title = source.get("content", "").strip()
                else:
                    title = source.get_text().strip()

                if title:
                    return title[:200]  # Limit title length

        return None

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main text content from HTML soup.

        Args:
            soup: BeautifulSoup object

        Returns:
            Extracted text content
        """
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        # Try to find main content areas
        main_content_selectors = [
            "main",
            "article",
            ".content",
            ".main-content",
            "#content",
            "#main",
            'div[role="main"]',
        ]

        main_content = None
        for selector in main_content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find("body") or soup

        # Extract text with paragraph separation
        paragraphs = []
        for element in main_content.find_all(
            ["p", "div", "section", "h1", "h2", "h3", "h4", "h5", "h6"]
        ):
            text = element.get_text().strip()
            if text and len(text) > 20:  # Skip very short text
                paragraphs.append(text)

        content = "\n\n".join(paragraphs)

        # Fallback to all text if no paragraphs found
        if not content:
            content = main_content.get_text().strip()

        # Clean up whitespace
        content = "\n".join(
            line.strip() for line in content.split("\n") if line.strip()
        )

        return content

    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if URL is properly formatted.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in [
                "http",
                "https",
            ]
        except Exception:
            return False
