import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Helper Function: Search Kaggle for datasets
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

# Helper Function: Search HuggingFace for datasets and models
def search_huggingface(query, search_type="dataset"):
    """
    Search HuggingFace for datasets or models.
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

# Helper Function: Search research papers using arXiv API
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
        
def propose_genai_solutions(use_case):
        solutions = {
            "document search": "Use a GenAI-powered document search system with semantic search capabilities (e.g., using OpenAI embeddings).",
            "automated report generation": "Build a system that generates summary reports or insights using fine-tuned language models like GPT-4.",
            "AI-powered chat systems": "Develop a chatbot for answering questions or assisting customers using a large language model like LLaMA or GPT."
        }
        print("\nProposed GenAI Solutions:")
        for solution, description in solutions.items():
            print(f"- {solution}: {description}")    
        

def save_resources_to_file(use_case, kaggle_results, huggingface_datasets, huggingface_models, arxiv_papers, filename="resources.md"):
        with open(filename, "w") as file:
            file.write(f"# Resources for Use Case: {use_case}\n\n")
            
            file.write("## Kaggle Datasets\n")
            for dataset in kaggle_results:
                file.write(f"- [{dataset['title']}]({dataset['url']})\n")
            
            file.write("\n## HuggingFace Datasets\n")
            for dataset in huggingface_datasets:
                file.write(f"- [{dataset['name']}]({dataset['url']})\n")
            
            file.write("\n## HuggingFace Models\n")
            for model in huggingface_models:
                file.write(f"- [{model['name']}]({model['url']})\n")
            
            file.write("\n## Research Papers\n")
            for paper in arxiv_papers:
                file.write(f"- [{paper['title']}]({paper['url']})\n")
        print(f"\nResources saved to {filename}")    


# Resource Asset Agent
def resource_asset_agent(use_case):
    """
    Search for datasets, models, and research resources for a specific use case.
    Save the results to a file and propose GenAI solutions if applicable.
    """
    print(f"Searching resources for use case: {use_case}\n")
    
    # Search for Kaggle datasets
    kaggle_results = search_kaggle_datasets(use_case)
    print("\nKaggle Datasets:")
    for dataset in kaggle_results:
        print(f"- {dataset['title']}: {dataset['url']}")

    # Search for HuggingFace datasets and models
    huggingface_datasets = search_huggingface(use_case, search_type="dataset")
    huggingface_models = search_huggingface(use_case, search_type="model")
    print("\nHuggingFace Datasets:")
    for dataset in huggingface_datasets:
        print(f"- {dataset['name']}: {dataset['url']}")
        
    print("\nHuggingFace Models:")
    for model in huggingface_models:
        print(f"- {model['name']}: {model['url']}")

    # Search for research papers
    arxiv_papers = search_arxiv_papers(use_case)
    print("\nResearch Papers:")
    for paper in arxiv_papers:
        print(f"- {paper['title']}: {paper['url']}")

    # Search for GitHub repositories
    github_results = search_github_repositories(use_case)
    print("\nGitHub Repositories:")
    for repo in github_results:
        print(f"- {repo['name']} (⭐ {repo['stars']}): {repo['url']}")

    # Save resources to a file
    save_resources_to_file(
        use_case=use_case,
        kaggle_results=kaggle_results,
        huggingface_datasets=huggingface_datasets,
        huggingface_models=huggingface_models,
        arxiv_papers=arxiv_papers,
        filename="resources.md"
    )

    # Propose GenAI solutions
    propose_genai_solutions(use_case)

if __name__ == "__main__":
    use_case = input("Enter the use case or topic: ")
    resource_asset_agent(use_case)

