import os
import requests
from dotenv import load_dotenv
import logging
load_dotenv()

logger = logging.getLogger(__name__)

# Define the query_forefront function
def query_forefront(prompt, model="forefront/Mistral-7B-claude-chat", max_tokens=300, temperature=0.5):
    """
    Queries the Forefront API with a specified prompt and returns the model's response.
    
    Args:
        prompt (str): The input prompt to send to the model.
        model (str): The model name to use (default: "forefront/Mistral-7B-claude-chat").
        max_tokens (int): The maximum number of tokens to generate (default: 300).
        temperature (float): Sampling temperature for randomness in responses (default: 0.5).
    
    Returns:
        str: The response text from the model, or None if an error occurs.
    """
    url = "https://api.forefront.ai/v1/chat/completions"
    api_key = os.getenv("FOREFRONT_API_KEY")
    if not api_key:
        raise ValueError("FOREFRONT_API_KEY environment variable is not set.")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", None)
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Define the research_industry function
def research_industry(company_name):
    search_query = f"{company_name} industry overview and AI trends"
    print(f"Researching: {search_query}")
    logger.info("Inside reasearch indusrty function")
    
    # Get the serpAPI key from env
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    if not serpapi_api_key:
        raise ValueError("SERPAPI_API_KEY environment variable is not set.")

    serpapi_url = "https://serpapi.com/search"
    # Payload 
    params = {
        "q": search_query,
        "api_key": serpapi_api_key,
        "engine": "google"
    }

    try:
        # Request the serpapi for the response
        response = requests.get(serpapi_url, params=params)
        response.raise_for_status()
        logger.info(f"Response: {response}")
        search_results = response.json().get("organic_results", [])
    except Exception as e:
        print(f"SerpAPI request failed: {e}")
        return {"company_info": "No data found", "industry_trends": "No trends found"}

    if not search_results:
        return {"company_info": "No data found", "industry_trends": "No trends found"}

    company_info = search_results[0].get("snippet", "No company info available")
    industry_trends = [result.get("snippet", "No snippet") for result in search_results[:3]]

    return {
        "company_info": company_info,
        "industry_trends": industry_trends
    }

# Define the summarize_with_forefront function
def summarize_with_forefront(text):
    """
    Summarize text using Forefront API.
    """
    prompt = (
        "You are an expert in market research. "
        "Summarize the following information clearly and concisely without repetition or redundancy:\n\n"
        f"{text}"
    )
    response = query_forefront(prompt, max_tokens=500)
    return response if response else "No summary available."

# Define the chunk_text function
def chunk_text(text, max_length=1500):
    """
    Splits text into smaller chunks for processing.
    """
    words = text.split()
    chunks = []
    while words:
        chunk = []
        while words and len(" ".join(chunk)) + len(words[0]) + 1 <= max_length:
            chunk.append(words.pop(0))
        chunks.append(" ".join(chunk))
    return chunks

def clean_and_display_response(raw_response):
    # Split the raw response into segments
    segments = raw_response.split("<|im_start|>")
    
    # Filter only the assistant's responses
    assistant_responses = [
        segment.replace("assistant", "").strip()
        for segment in segments
        if segment.strip().startswith("assistant")
    ]
    
    # Display the assistant responses in bullets
    print("AI Agent Responses:")
    for response in assistant_responses:
        print(f"- {response}")

def generate_markdown_file(query, summary):
    """Generate Markdown report and save it"""
    md_content = f"""# {query} Report

## Overview
{summary}

## Industry Trends
- Key trends in the industry.
- Emerging technologies.
- Market growth insights.

## Key Insights
- How the industry is evolving.
- What companies are leading.
- Investment opportunities.

---
*Generated using AI and SerpAPI.*
"""
    filename = query.lower().replace(" ", "_") + "_report.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(md_content)
    
    return filename        

# Define the research_industry_with_summary function
def research_industry_with_summary(company_name):
    raw_data = research_industry(company_name)
    print(f"Raw data from internet: \n {raw_data}")

    combined_trends = " ".join(raw_data["industry_trends"])
    all_summaries = []

    # Process company info
    company_info_chunks = chunk_text(raw_data["company_info"])
    for chunk in company_info_chunks:
        all_summaries.append(summarize_with_forefront(chunk))

    summarized_company_info = " ".join(all_summaries).strip()

    # Process industry trends
    trend_chunks = chunk_text(combined_trends)
    trend_summaries = []
    for chunk in trend_chunks:
        trend_summaries.append(summarize_with_forefront(chunk))
    
    summarized_trends = " ".join(trend_summaries).strip()

    # Add warnings for insufficient data
    if len(summarized_company_info) < 50:
        summarized_company_info += " (Info may be limited; please verify sources.)"
    if len(summarized_trends) < 50:
        summarized_trends += " (Trends may be incomplete; please verify sources.)"

    return {
        "company_info": summarized_company_info,
        "industry_trends": summarized_trends
    }

if __name__ == "__main__":
    company_name = input("Enter the company name: ")
    results = research_industry_with_summary(company_name)
    
    print("\n--- Research Results ---")
    print(f"Company Info:\n{results['company_info']}")
    print(f"\nIndustry Trends:\n{results['industry_trends']}")
