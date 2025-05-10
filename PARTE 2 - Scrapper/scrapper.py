import os
import json
import time
import random
import logging
import requests
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin as urllib_urljoin

def urljoin(base, url):
    """Safe wrapper for urljoin that ensures string inputs."""
    return urllib_urljoin(str(base), str(url))

# Configure logging
logger = logging.getLogger(__name__)

# Constants
JOURNALS_FILE = "data/journals.json"
SCIMAGOJR_BASE_URL = "https://www.scimagojr.com"
RESURCHIFY_BASE_URL = "https://www.resurchify.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Make sure the data directory exists
os.makedirs("data", exist_ok=True)

def load_journals():
    """Load journals from JSON file or create empty structure if the file doesn't exist."""
    try:
        if os.path.exists(JOURNALS_FILE):
            with open(JOURNALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"journals": {}}
    except Exception as e:
        logger.error(f"Error loading journals: {e}")
        return {"journals": {}}

def save_journals(journals_data):
    """Save journals data to JSON file."""
    try:
        with open(JOURNALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(journals_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving journals: {e}")

def get_journal_data(issn, force_update=False):
    """Get journal data for a specific ISSN, scraping if necessary."""
    journals_data = load_journals()
    
    # Check if we already have this journal
    if issn in journals_data["journals"] and not force_update:
        # Check if data is older than 1 month
        last_visit = datetime.datetime.fromisoformat(journals_data["journals"][issn]["ultima_visita"])
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        
        if last_visit > one_month_ago:
            return journals_data["journals"][issn]
    
    # Need to scrape the data
    try:
        # First try scimagojr.com
        journal_data = scrape_scimagojr_journal(issn)
        
        # Then try resurchify.com for additional data
        resurchify_data = scrape_resurchify_journal(issn)
        if resurchify_data:
            # Merge the data
            journal_data.update(resurchify_data)
        
        # Add timestamp
        journal_data["ultima_visita"] = datetime.datetime.now().isoformat()
        
        # Save the data
        journals_data["journals"][issn] = journal_data
        save_journals(journals_data)
        
        return journal_data
    except Exception as e:
        logger.error(f"Error scraping journal {issn}: {e}")
        # If we already have old data, return it instead of nothing
        if issn in journals_data["journals"]:
            return journals_data["journals"][issn]
        return None

def scrape_scimagojr_journal(issn):
    """Scrape journal information from scimagojr.com."""
    url = f"{SCIMAGOJR_BASE_URL}/journalsearch.php?q={issn}&tip=iss"
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the journal link in search results
        journal_link = soup.select_one('.search_results a.journalLink')
        if not journal_link or 'href' not in journal_link.attrs:
            logger.warning(f"Journal with ISSN {issn} not found on scimagojr.com")
            return {}
        
        journal_url = urljoin(SCIMAGOJR_BASE_URL, str(journal_link['href']))
        
        # Add delay before next request
        time.sleep(random.uniform(1, 3))
        
        # Get the journal page
        journal_response = requests.get(journal_url, headers=HEADERS, timeout=10)
        journal_response.raise_for_status()
        
        journal_soup = BeautifulSoup(journal_response.text, 'html.parser')
        
        # Extract journal data
        journal_name_element = journal_soup.select_one('.journalName')
        journal_data = {
            "issn": issn,
            "title": journal_name_element.text.strip() if journal_name_element else "Unknown",
            "website": None,
            "h_index": None,
            "subject_area": [],
            "publisher": None,
            "publication_type": None,
            "widget": journal_url,
        }
        
        # Extract website
        website_link = journal_soup.select_one('a[title="Go to the web page of this journal"]')
        if website_link:
            journal_data["website"] = website_link['href']
        
        # Extract H-Index
        h_index_cell = journal_soup.select_one('td.cellindname:-soup-contains("H index")')
        if h_index_cell and h_index_cell.find_next_sibling():
            sibling = h_index_cell.find_next_sibling()
            if sibling and hasattr(sibling, 'text'):
                journal_data["h_index"] = sibling.text.strip()
        
        # Extract subject areas
        subject_areas = journal_soup.select('.journalSubjects dd')
        for subject in subject_areas:
            area_text = subject.text.strip()
            if area_text:
                journal_data["subject_area"].append(area_text)
        
        # Extract publisher
        publisher_cell = journal_soup.select_one('td.journalnamecell:-soup-contains("Publisher")')
        if publisher_cell and publisher_cell.find_next_sibling():
            sibling = publisher_cell.find_next_sibling()
            if sibling and hasattr(sibling, 'text'):
                journal_data["publisher"] = sibling.text.strip()
        
        # Extract publication type
        pub_type_cell = journal_soup.select_one('td.journalnamecell:-soup-contains("Type")')
        if pub_type_cell and pub_type_cell.find_next_sibling():
            sibling = pub_type_cell.find_next_sibling()
            if sibling and hasattr(sibling, 'text'):
                journal_data["publication_type"] = sibling.text.strip()
        
        return journal_data
    
    except Exception as e:
        logger.error(f"Error scraping scimagojr.com for ISSN {issn}: {e}")
        return {}

def scrape_resurchify_journal(issn):
    """Scrape additional journal information from resurchify.com."""
    url = f"{RESURCHIFY_BASE_URL}/find-journals/search?query={issn}"
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the journal card
        journal_card = soup.select_one('.journal-card')
        if not journal_card:
            logger.warning(f"Journal with ISSN {issn} not found on resurchify.com")
            return {}
        
        # Extract additional data
        additional_data = {}
        
        # Impact factor
        impact_factor_elem = journal_card.select_one('.journal-card-impact-factor')
        if impact_factor_elem:
            impact_factor_text = impact_factor_elem.text.strip()
            if "Impact Factor:" in impact_factor_text:
                additional_data["impact_factor"] = impact_factor_text.split("Impact Factor:")[-1].strip()
        
        # Acceptance rate if available
        acceptance_rate_elem = journal_card.select_one('.journal-card-acceptance-rate')
        if acceptance_rate_elem:
            acceptance_rate_text = acceptance_rate_elem.text.strip()
            if "Acceptance Rate:" in acceptance_rate_text:
                additional_data["acceptance_rate"] = acceptance_rate_text.split("Acceptance Rate:")[-1].strip()
        
        # Time to first decision if available
        time_to_decision_elem = journal_card.select_one('.journal-card-time-to-first-decision')
        if time_to_decision_elem:
            time_text = time_to_decision_elem.text.strip()
            if "Time to First Decision:" in time_text:
                additional_data["time_to_first_decision"] = time_text.split("Time to First Decision:")[-1].strip()
        
        return additional_data
    
    except Exception as e:
        logger.error(f"Error scraping resurchify.com for ISSN {issn}: {e}")
        return {}

def search_journals(query, field="title"):
    """Search for journals in the local database."""
    journals_data = load_journals()
    results = []
    
    query = query.lower()
    
    for issn, journal in journals_data["journals"].items():
        if field == "title" and query in journal.get("title", "").lower():
            results.append(journal)
        elif field == "issn" and query in issn.lower():
            results.append(journal)
        elif field == "publisher" and query in journal.get("publisher", "").lower():
            results.append(journal)
        elif field == "subject" and any(query in subject.lower() for subject in journal.get("subject_area", [])):
            results.append(journal)
    
    return results

def get_all_journals():
    """Get all journals from the local database."""
    journals_data = load_journals()
    return list(journals_data["journals"].values())