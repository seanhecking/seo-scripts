import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

def find_internal_links(url):
    """Finds all internal links on a given page."""
    internal_urls = set()
    domain_name = urlparse(url).netloc
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                full_url = urljoin(url, href)
                parsed_href = urlparse(full_url)
                if parsed_href.netloc == domain_name and parsed_href.fragment == '':
                    internal_urls.add(full_url)
    except requests.exceptions.RequestException:
        pass  # Silently skip pages that fail to load
    return internal_urls

def check_url(url):
    """Checks the status code of a given URL."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code
    except requests.exceptions.RequestException:
        return None # Return None for connection errors

def crawl_and_find_404s(start_url):
    """Crawls a website to find and list 404 errors."""
    visited_urls = set()
    to_visit_urls = {start_url}
    broken_links = []

    print(f"Starting crawl from: {start_url}")

    while to_visit_urls:
        current_url = to_visit_urls.pop()

        if current_url in visited_urls:
            continue

        print(f"Checking: {current_url}")
        visited_urls.add(current_url)

        status_code = check_url(current_url)

        if status_code is not None and status_code == 404:
            print(f"404 found: {current_url}")
            broken_links.append(current_url)

        # Find internal links on the current page and add to the to_visit set
        # Only do this if the status code is not None and not 404,
        # to avoid unnecessary crawling of broken pages.
        if status_code is not None and status_code != 404:
            internal_links = find_internal_links(current_url)
            for link in internal_links:
                if link not in visited_urls:
                    to_visit_urls.add(link)

        time.sleep(1) # Add a small delay to be polite to the server

    print("\nCrawl finished.")
    if broken_links:
        print("\nFound 404 errors at the following URLs:")
        for link in broken_links:
            print(link)
    else:
        print("\nNo 404 errors found.")

# Example usage:
# Replace with the starting URL of the website you want to crawl
start_url = "YOUR_WEBSITE_URL_HERE"
crawl_and_find_404s(start_url)