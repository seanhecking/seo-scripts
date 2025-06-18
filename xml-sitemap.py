import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

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
                # Only include internal links and exclude fragment identifiers
                if parsed_href.netloc == domain_name and parsed_href.fragment == '':
                    internal_urls.add(full_url)
    except requests.exceptions.RequestException:
        pass  # Silently skip pages that fail to load
    return internal_urls

def crawl_website(start_url):
    """Crawls a website to find all internal pages."""
    visited_urls = set()
    to_visit_urls = {start_url}
    all_internal_pages = set()

    print(f"Starting crawl from: {start_url}")

    while to_visit_urls:
        current_url = to_visit_urls.pop()

        if current_url in visited_urls:
            continue

        print(f"Visiting: {current_url}")
        visited_urls.add(current_url)
        all_internal_pages.add(current_url)

        # Find internal links on the current page
        internal_links = find_internal_links(current_url)
        for link in internal_links:
            if link not in visited_urls:
                to_visit_urls.add(link)

        time.sleep(1) # Add a small delay to be polite to the server

    print("\nCrawl finished.")
    return all_internal_pages

def create_sitemap(urls, output_filename="sitemap.xml"):
    """Creates an XML sitemap from a list of URLs."""
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in urls:
        url_element = SubElement(urlset, 'url')
        loc = SubElement(url_element, 'loc')
        loc.text = url
        # You can add other optional elements like <lastmod>, <changefreq>, <priority>
        # Example:
        # lastmod = SubElement(url_element, 'lastmod')
        # lastmod.text = '2023-10-27' # Replace with actual last modification date

    # Generate pretty XML
    rough_string = tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml_as_string)

    print(f"\nSitemap created: {output_filename}")

# Example usage:
# Replace with the starting URL of the website you want to crawl
start_url = "YOUR_WEBSITE_URL_HERE"

# Crawl the website to get all internal pages
all_pages = crawl_website(start_url)

# Create and save the sitemap
if all_pages:
    create_sitemap(all_pages)
else:
    print("No pages found to create a sitemap.")
