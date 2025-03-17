import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from google import genai

GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
CX = "b5e652f249c6144c2"

# Configure Gemini API key
client = genai.Client(api_key=GEMINI_API_KEY)

def search_google(query):
    """Fetch top search results from Google API and prioritize Wikipedia."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_SEARCH_API_KEY}&cx={CX}"
    response = requests.get(url)
    data = response.json()
    
    links = [item["link"] for item in data.get("items", [])[:5]]  # Get top 5 results
    
    # Prioritize Wikipedia link if available
    wiki_link = next((link for link in links if "wikipedia.org" in link), None)
    if wiki_link:
        links.insert(0, wiki_link)  # Move Wikipedia to the top
    
    return links

def extract_text_from_url(url):
    """Scrape text from a URL with improved filtering."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract text from paragraph tags
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        
        # Remove common unwanted phrases
        unwanted_phrases = [
            "Read more", "Learn more", "Click here", "Subscribe", "Sign up",
            "Follow us", "Contact us", "Get started", "All rights reserved"
        ]
        for phrase in unwanted_phrases:
            text = text.replace(phrase, "")
        
        # Limit text to 1500 characters
        return text[:1500] if text else "No relevant content found."
    
    except Exception as e:
        return f"Error extracting content: {e}"
    
def generate_company_overview(scraped_info):
    """Generates a company overview using Google Gemini."""
    prompt = (
        "Provide a concise and well-structured summary of the following company details. "
        "Ensure key information is retained while removing redundancy and unnecessary details. "
        "Focus on the company's core business, major milestones, and recent developments:\n\n"
        f"{scraped_info}"
    )

    model = "gemini-2.0-flash"

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text   
    
def remove_duplicates(text):
    """Remove duplicate paragraphs by normalizing spaces and removing repeats."""
    paragraphs = list(dict.fromkeys(re.sub(r'\s+', ' ', text).split(". ")))  # Normalize spaces & split sentences
    return ". ".join(paragraphs)


def truncate_text(text, limit=3000):
    """Truncate text at the nearest sentence boundary before the limit."""
    if len(text) <= limit:
        return text
    # Find the last period (.) before limit and cut there
    last_sentence_end = text[:limit].rfind(". ")
    return text[:last_sentence_end+1] if last_sentence_end != -1 else text[:limit]

def clean_text(text):
    """Remove citation numbers like [4], [5]"""
    return re.sub(r"\[\d+\]", "", text)

def clean_irrelevant_content(text):
    """Remove irrelevant sections like newsletter & policy text."""
    stop_phrases = ["Newsletter", "Privacy Policy", "Terms of Service", "Sign In", "Founder first", "Start your day"]
    for phrase in stop_phrases:
        text = text.split(phrase)[0]  
    return text.strip()

# Driver function
def get_company_info(company_name):
    """Search, scrape, and summarize company info"""
    search_results = search_google(company_name + " company profile")
    extracted_texts = [extract_text_from_url(url) for url in search_results]
    
    # Combine extracted texts
    combined_text = remove_duplicates(truncate_text(clean_irrelevant_content(" ".join(extracted_texts))))
    
    return combined_text 

# Example usage
query = input("Enter a company/industry name: ")
info = get_company_info(query)
overview = generate_company_overview(info)
# print(f"Info: {info}")
print(f"Summarised info: {info}")
# print(f"\nExtracted Info:\n{info[:1000]}...")  # Display first 1000 chars
