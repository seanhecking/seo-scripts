# Sean Hecking SEO Python Scripts

A collection of Python scripts designed to assist with common Search Engine Optimization (SEO) tasks such as XML site map, metadata auditing, sitemap validation, error pages, link checks, and more.

## Features

- **404 Error Page Checker** – Crawls a website to find 404 error pages and links, then creates a CSV file.
- **Server Response Checker** – Crawls a website to find all pages and their server response, then creates a CSV file.
- **XML Sitemap Generator** – Crawls a website and creates an XML sitemap manually.
- **CSV Crawl Match** – Matches a list of new and old URLs using two colunns.
- **Reading Scores** – Crawls a website and finds the reading scores for each page, then saves to a CSV file.
- **Flexible & Modular** – Easy to modify, extend, or integrate into your pipeline.

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.8+
- `pip` (Python package installer)
- Optional: API keys for third-party SEO tools (e.g., Ahrefs, SEMrush, Google Search Console)

### Installation

```bash
gh repo clone seanhecking/seo-scripts
cd seo-scripts
pip install -r requirements.txt
