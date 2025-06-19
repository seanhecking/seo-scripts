import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import pandas as pd
import re

# Function to calculate Flesch-Kincaid Grade Level
def flesch_kincaid_grade_level(text):
    """Calculates the Flesch-Kincaid Grade Level for a given text."""
    # Remove HTML tags and scripts
    clean_text = re.sub(r'<.*?>', '', text)
    clean_text = re.sub(r'<script.*?>.*?</script>', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'<style.*?>.*?</style>', '', clean_text, flags=re.DOTALL)

    sentences = re.split(r'[.!?]+', clean_text)
    sentences = [s for s in sentences if s.strip()] # Remove empty sentences

    words = re.findall(r'\b\w+\b', clean_text.lower())

    syllable_count = 0
    # A simple approach to counting syllables (can be improved for accuracy)
    # Count vowels as syllables, handle consecutive vowels as one,
    # and handle 'e' at the end of a word.
    vowels = "aeiouy"
    for word in words:
        count = 0
        if word.endswith('e'):
            word = word[:-1]
        word = re.sub(r'[aeiouy]{2,}', 'a', word) # Treat consecutive vowels as one
        count = len(re.findall(r'[aeiouy]', word))
        if count == 0:
            count = 1 # Assume at least one syllable
        syllable_count += count

    num_sentences = len(sentences)
    num_words = len(words)
    num_syllables = syllable_count

    if num_words == 0 or num_sentences == 0:
        return 0.0 # Avoid division by zero

    # Flesch-Kincaid Grade Level formula
    score = 0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59
    return round(score, 2) # Round to 2 decimal places

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

def get_page_text(url):
    """Fetches the text content of a given URL."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from common content areas (you might need to adjust this)
            # Example: paragraphs, headings, list items
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            page_text = ' '.join([element.get_text() for element in text_elements])
            return page_text.strip()
        else:
            return None
    except requests.exceptions.RequestException:
        return None # Return None for connection errors

def crawl_and_analyze_readability(start_url):
    """Crawls a website, analyzes readability, and saves results to CSV."""
    visited_urls = set()
    to_visit_urls = {start_url}
    readability_results = []

    print(f"Starting crawl from: {start_url}")

    while to_visit_urls:
        current_url = to_visit_urls.pop()

        if current_url in visited_urls:
            continue

        print(f"Analyzing: {current_url}")
        visited_urls.add(current_url)

        page_text = get_page_text(current_url)

        if page_text:
            score = flesch_kincaid_grade_level(page_text)
            readability_results.append({'URL': current_url, 'Readability Score (F-K)': score})
            print(f"  Score: {score}")

            # Find internal links on the current page
            internal_links = find_internal_links(current_url)
            for link in internal_links:
                if link not in visited_urls:
                    to_visit_urls.add(link)
        else:
             print(f"  Could not retrieve or analyze text for: {current_url}")


        time.sleep(1) # Add a small delay to be polite to the server

    print("\nCrawl and analysis finished.")

    if readability_results:
        # Save results to a CSV file
        df = pd.DataFrame(readability_results)
        df.to_csv("readability_scores.csv", index=False)
        print("\nReadability scores saved to readability_scores.csv")
    else:
        print("\nNo pages found or analyzed.")

# Example usage:
# Replace with the starting URL of the website you want to crawl
start_url = "YOUR_URL_HERE"

# NOTES ON READING SCORES
# 100–90  5th grade Very easy to read
# 90–80   6th grade Easy to read (the target for most consumer copy)
# 80–70   7th grade Fairly easy to read (target for professionals, B2B)
# 70–60   8th & 9th Grade Plain English (target for professionals, B2B)
# 60-50   10th to 12th grade (target for engineers, tech copy)
# 50–30   College
# 30–10   College Graduate
# 10–0    Professional

# Crawl the website and analyze readability
crawl_and_analyze_readability(start_url)
