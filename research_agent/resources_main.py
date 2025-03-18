import os
import requests
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import subprocess
import json
import feedparser
from kaggle.api.kaggle_api_extended import KaggleApi

GITHUB_TOKEN = os.getenv("GITHUB_API_KEY")

os.environ['KAGGLE_USERNAME'] = os.getenv("KAGGLE_USERNAME")
os.environ['KAGGLE_KEY'] = os.getenv("KAGGLE_KEY")

api = KaggleApi()
api.authenticate()

def fetch_huggingface_models(query, limit=5):
    """Fetch relevant Hugging Face models based on the input query.
    
    Args:
        query (str): The search query for models.
        limit (int): The number of models to return (default: 5).

    Returns:
        list: A list of dictionaries containing model names and their URLs.
    """
    url = f"https://huggingface.co/api/models?search={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        models = response.json()

        if not models:
            return [{"message": "No relevant models found"}]

        model_list = [
            {"name": model["id"], "url": f"https://huggingface.co/{model['id']}"}
            for model in models[:limit]
        ]
        
        return model_list
    
    except requests.RequestException as e:
        return [{"error": str(e)}]    

    
def fetch_huggingface_datasets(query, limit=5):
    """Fetch relevant Hugging Face datasets based on the input query.
    
    Args:
        query (str): The search query for datasets.
        limit (int): The number of datasets to return (default: 5).

    Returns:
        list: A list of dictionaries containing dataset names and their URLs.
    """
    url = f"https://huggingface.co/api/datasets?search={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        datasets = response.json()

        if not datasets:
            return [{"message": "No relevant datasets found"}]

        dataset_list = [
            {"name": dataset["id"], "url": f"https://huggingface.co/datasets/{dataset['id']}"}
            for dataset in datasets[:limit]
        ]
        
        return dataset_list
    
    except requests.RequestException as e:
        return [{"error": str(e)}]
    

def fetch_kaggle_datasets(query, limit=5):
    """Fetch relevant Kaggle datasets based on the input query.

    Args:
        query (str): The search query for datasets.
        limit (int): The number of datasets to return (default: 5).

    Returns:
        list: A list of dictionaries containing dataset names and their URLs.
    """
    try:
        datasets = api.dataset_list(search=query)
        
        if not datasets:
            return [{"message": "No relevant datasets found"}]

        dataset_list = [
            {"name": dataset.ref, "url": f"https://www.kaggle.com/datasets/{dataset.ref}"}
            for dataset in datasets[:limit]
        ]

        return dataset_list
    
    except Exception as e:
        return [{"error": str(e)}]
    

def search_arxiv_papers(query):
    """
    Search arXiv for research papers related to the input query.
    """
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": query, "start": 0, "max_results": 5}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)

        root = ET.fromstring(response.content)
        papers = []

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.findtext("{http://www.w3.org/2005/Atom}title", "").strip()
            link = entry.findtext("{http://www.w3.org/2005/Atom}id", "").strip()
            papers.append({"title": title, "url": link})

        return papers if papers else [{"message": "No papers found"}]

    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch papers: {e}"}]


def fetch_github_repos(query, limit=5, github_token=None):
    """Fetch relevant GitHub repositories based on the input query.

    Args:
        query (str): The search query for repositories.
        limit (int): The number of repositories to return (default: 5).
        github_token (str, optional): GitHub API token for higher rate limits.

    Returns:
        list: A list of dictionaries containing repository names and their URLs.
    """
    url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    params = {
        "q": query,
        "sort": "stars",  # Sort by most stars
        "order": "desc",
        "per_page": limit
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data:
            return [{"message": "No relevant repositories found"}]

        repo_list = [
            {"name": repo["full_name"], "url": repo["html_url"]}
            for repo in data["items"]
        ]

        return repo_list
    
    except requests.exceptions.RequestException as e:
        return [{"error": str(e)}]
         

# Main function to process use cases
def collect_resources_for_usecases(use_cases_json):
    # use_cases = use_cases_json["Usecases"]["use_cases"]
    use_cases = use_cases_json["use_cases"]
    resource_collection = []

    for use_case in use_cases:
        title = use_case["title"]
        print(f"Collecting resources for: {title}")

        # models = search_huggingface(title)
        models = fetch_huggingface_models(title)
        hf_datasets = fetch_huggingface_datasets(title)
        kaggle_datasets = fetch_kaggle_datasets(title)
        github_repos = fetch_github_repos(title, GITHUB_TOKEN)
        papers = search_arxiv_papers(title)

        resource_collection.append({
            "title": title,
            "resources": {
                "huggingface_models": models,
                "huggingface_datasets": hf_datasets,
                "kaggle_datasets": kaggle_datasets,
                "github_repositories": github_repos,
                "research_papers": papers
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

# # Example usage
# query = "image segmentation"
# models = fetch_huggingface_models(query)
# for model in models:
#     print(model)

# # Example usage
# query = "image segmentation"
# datasets = fetch_kaggle_datasets(query)
# for dataset in datasets:
#     print(dataset)

# # Example usage
# query = "machine learning"
# repos = fetch_github_repos(query)
# for repo in repos:
#     print(repo)