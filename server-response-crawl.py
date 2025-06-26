import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import pandas as pd

def find_internal_links(url, domain_name):
    """Finds all internal links on a given page within the specified domain."""
    internal_urls = set()
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                full_url = urljoin(url, href)
                parsed_href = urlparse(full_url)
                # Only include internal links and exclude fragment identifiers and non-html files
                if parsed_href.netloc == domain_name and parsed_href.fragment == '' and not any(parsed_href.path.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js']):
                    internal_urls.add(full_url)
    except requests.exceptions.RequestException:
        pass  # Silently skip pages that fail to load
    return internal_urls

def check_url_status(url):
    """Checks the status code of a given URL."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code
    except requests.exceptions.RequestException:
        return None # Return None for connection errors

def crawl_and_collect_status_codes(start_url, output_filename="url_status_codes.csv"):
    """
    Crawls a website, collects internal HTML URLs and their status codes,
    and saves the results to a CSV file.
    """
    visited_urls = set()
    to_visit_urls = {start_url}
    url_status_data = []
    domain_name = urlparse(start_url).netloc

    print(f"Starting crawl from: {start_url}")

    while to_visit_urls:
        current_url = to_visit_urls.pop()

        if current_url in visited_urls:
            continue

        print(f"Checking: {current_url}")
        visited_urls.add(current_url)

        status_code = check_url_status(current_url)

        url_status_data.append({'URL': current_url, 'Status Code': status_code})

        # Find internal links on the current page and add to the to_visit set
        if status_code is not None and status_code != 404: # Avoid crawling broken pages
             internal_links = find_internal_links(current_url, domain_name)
             for link in internal_links:
                 if link not in visited_urls:
                     to_visit_urls.add(link)

        time.sleep(1) # Add a small delay to be polite to the server

    print("\nCrawl finished.")

    if url_status_data:
        # Save results to a CSV file
        df = pd.DataFrame(url_status_data)
        df.to_csv(output_filename, index=False)
        print(f"\nURL status codes saved to {output_filename}")
    else:
        print("\nNo URLs found or checked.")

# Example usage:
# Replace with the starting URL of the website you want to crawl
start_url = "YOUR_WEBSITE_FULL_URL"

# Crawl the website and collect status codes
crawl_and_collect_status_codes(start_url)
