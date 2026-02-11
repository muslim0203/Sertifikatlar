import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
import logging

logger = logging.getLogger(__name__)

# Constants
REQUIRED_DOMAIN = "mijournals.com"
REQUIRED_PATH_SUBSTRING = "/Human_Studies/article/view/"

# Konferensiya bo'limi nomi — shu bo'lsa template_human_studies2 (ICSSHR) ishlatiladi
CONFERENCE_SECTION_NAME = "International Conference on Social Sciences and Humanities Research"

def validate_url(url: str) -> bool:
    """Checks if the URL is from mijournals.com and contains the specific path."""
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    
    # Check domain (e.g. mijournals.com or www.mijournals.com)
    if REQUIRED_DOMAIN not in parsed.netloc:
        return False
        
    if REQUIRED_PATH_SUBSTRING not in parsed.path:
        return False
        
    return True

def extract_metadata(url: str):
    """
    Fetches the OJS page and extracts metadata.
    Returns a dict with:
        'title': str
        'authors': list of str
        'date': str (formatted publication date)
    Raises exceptions on failure.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract Meta Tags
    # citation_title
    title_meta = soup.find('meta', attrs={'name': 'citation_title'})
    if not title_meta:
        logger.warning(f"No citation_title found for {url}")
        return None
    title = title_meta['content'].strip()

    # citation_author (can be multiple)
    authors_meta = soup.find_all('meta', attrs={'name': 'citation_author'})
    if not authors_meta:
        logger.warning(f"No citation_author found for {url}")
        return None
    authors = [meta['content'].strip() for meta in authors_meta]

    # citation_publication_date
    date_meta = soup.find('meta', attrs={'name': 'citation_publication_date'})
    publication_date_str = ""
    
    if date_meta:
        try:
            # Format usually YYYY/MM/DD or YYYY-MM-DD
            raw_date = date_meta['content'].strip()
            # Try parsing common formats
            # Often OJS uses YYYY/MM/DD
            date_obj = None
            for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y/%m", "%Y-%m", "%Y"):
                try:
                    date_obj = datetime.datetime.strptime(raw_date, fmt)
                    break
                except ValueError:
                    continue
            
            if date_obj:
                # User wants specific format? 
                # "citation_publication_date (publication date)"
                # "If citation_publication_date is missing or empty, use fallback date format: current month and year in English, e.g. 'February 2026'"
                # Implies if present, keep it? Or if present, format it nicely?
                # Probably format nicely like "February 2026" or "11 February 2026"
                # Let's standardize to "Month Year" or "Day Month Year" based on the fallback description.
                # "If citation_publication_date is missing or empty, use fallback date format: current month and year in English"
                # This suggests the preferred format is "Month Year". It's safe to use that for extracted dates too.
                publication_date_str = date_obj.strftime("%B %Y")
            else:
                publication_date_str = raw_date # Fallback to raw if logic fails but tag exists
        except Exception as e:
            logger.warning(f"Error parsing date {raw_date}: {e}")
            publication_date_str = ""
    
    if not publication_date_str:
        # Fallback date: current month and year in English
        now = datetime.datetime.now()
        publication_date_str = now.strftime("%B %Y")

    # citation_doi (DOI raqami)
    doi_meta = soup.find('meta', attrs={'name': 'citation_doi'})
    doi = doi_meta['content'].strip() if doi_meta and doi_meta.get('content') else None

    # Section: jurnal yoki konferensiya — sertifikat shabloni va ID prefiksi uchun
    section_name = None
    # OJS da odatda <dt>Section</dt><dd>...</dd> yoki label + span
    dt_section = soup.find('dt', string=lambda t: t and 'Section' in t.strip())
    if dt_section and dt_section.find_next_sibling('dd'):
        section_name = dt_section.find_next_sibling('dd').get_text(strip=True)
    if not section_name:
        # Yoki "Section" so'zidan keyingi matn (masalan div/label atrofida)
        for tag in soup.find_all(['div', 'p', 'span', 'li']):
            text = tag.get_text(strip=True)
            if text == 'Section' and tag.find_next_sibling():
                next_ = tag.find_next_sibling()
                if next_:
                    section_name = next_.get_text(strip=True)
                    break
            if text.startswith('Section') and len(text) > 10:
                section_name = text.replace('Section', '').strip().strip(':-').strip()
                break
    if not section_name and CONFERENCE_SECTION_NAME in soup.get_text():
        section_name = CONFERENCE_SECTION_NAME
    is_conference = bool(section_name and CONFERENCE_SECTION_NAME in section_name)

    return {
        'title': title,
        'authors': authors,
        'date': publication_date_str,
        'doi': doi,
        'section': section_name or '',
        'is_conference': is_conference,
    }
