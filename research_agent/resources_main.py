import os
import requests
from dotenv import load_dotenv
import subprocess
import json
import feedparser

# Helper Function: Search HuggingFace for datasets and models
def search_huggingface(query, search_type="model"):
    """
    Search HuggingFace for models
    """
    url = f"https://huggingface.co/api/{search_type}s"
    params = {"search": query}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        items = response.json()
        return [
            {"name": item["id"], "url": f"https://huggingface.co/{item['id']}"} for item in items
        ]
    else:
        return []


def search_kaggle_datasets(query):
    """
    Search Kaggle for datasets related to the query.
    """
    kaggle_api_token = os.getenv("KAGGLE_API_KEY")
    if not kaggle_api_token:
        raise ValueError("KAGGLE_API_KEY environment variable is not set.")
    
    url = f"https://www.kaggle.com/api/v1/datasets/list"
    headers = {
        "Authorization": f"Bearer {kaggle_api_token}",
        "Content-Type": "application/json",
    }
    params = {"search": query}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        datasets = response.json()
        return [
            {"title": d["title"], "url": f"https://kaggle.com/{d['ref']}"} for d in datasets
        ]
    else:
        return []

def search_arxiv_papers(query):
    """
    Search arXiv for research papers.
    """
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": query, "start": 0, "max_results": 5}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(response.content)
        papers = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            link = entry.find("{http://www.w3.org/2005/Atom}id").text
            papers.append({"title": title.strip(), "url": link.strip()})
        return papers
    else:
        return []
    
def search_github_repositories(query):
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        items = response.json()["items"]
        return [
            {"name": item["full_name"], "url": item["html_url"], "stars": item["stargazers_count"]}
                for item in items[:5]
            ]
    else:
        return []    

# Main function to process use cases
def collect_resources_for_usecases(use_cases_json):
    # use_cases = use_cases_json["Usecases"]["use_cases"]
    use_cases = use_cases_json["use_cases"]
    resource_collection = []

    for use_case in use_cases:
        title = use_case["title"]
        print(f"Collecting resources for: {title}")

        models = search_huggingface(title)
        datasets = search_kaggle_datasets(title)
        github_repos = search_github_repositories(title)
        # papers = search_arxiv_papers(title)

        resource_collection.append({
            "title": title,
            "resources": {
                "huggingface_models": models,
                "kaggle_datasets": datasets,
                "github_repositories": github_repos,
                # "research_papers": papers
            }
        })
    
    return {"use_cases_resources": resource_collection}


# Example JSON input (You should replace this with actual input)
use_cases_json = {
    "Usecases": {
        "use_cases": [
            {
                "title": "Demand Forecasting & Dynamic Pricing",
                "explanation": "Predict ride demand in real-time based on historical data, weather patterns, event schedules, and location. This enables dynamic pricing that optimizes revenue and ensures adequate driver supply, especially during peak hours or in specific areas.",
                "practical_application": [
                    "Using a machine learning model to analyze historical ride data coupled with real-time event data (e.g., concerts, festivals) to predict demand surges and automatically adjust fares accordingly."
                ]
            },
            {
                "title": "Route Optimization & Driver Allocation",
                "explanation": "Leverage AI algorithms to determine the most efficient routes for drivers, considering real-time traffic conditions, road closures, and customer pick-up/drop-off locations.",
                "practical_application": [
                    "Implementing a GPS-enabled system that uses AI to dynamically update routes based on live traffic data."
                ]
            }
        ]
    }
}

# # Collect resources and save as JSON
# resources_json = collect_resources_for_usecases(use_cases_json)
# with open("use_case_resources.json", "w") as f:
#     json.dump(resources_json, f, indent=4)

# print("Resources collected successfully!")