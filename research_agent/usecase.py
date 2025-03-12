import os
import requests
from dotenv import load_dotenv
import json
from .research import query_forefront

# Load environment variables
load_dotenv()

# Use Case Generation Function
def generate_use_cases(company_name, research_results):
    """
    Generates AI/GenAI use cases based on insights from the Research Agent.
    
    Args:
        company_name (str): Name of the company/industry.
        research_results (dict): Insights from the Research Agent.

    Returns:
        list: A list of proposed use cases.
    """
    # Construct the prompt
    prompt = (
        f"Based on the following insights about {company_name}, suggest AI/GenAI use cases:\n\n"
        f"Company Info:\n{research_results['company_info']}\n\n"
        f"Industry Trends:\n{research_results['industry_trends']}\n\n"
        "1. Suggest AI/GenAI use cases for the company.\n"
        "2. List operations that can benefit from AI.\n"
        "3. Include potential datasets and implementation steps for each use case.\n\n"
        "Provide concise but detailed recommendations."
    )
    
    # Query the Forefront API
    response = query_forefront(prompt)
    
    if response:
        # Process response into a structured list
        use_case_list = [line.strip() for line in response.split("\n") if line.strip()]
        return use_case_list
    else:
        return ["No use cases could be generated."]
    
# Helper Function: Format Use Cases    
def format_use_cases(raw_response):
    """Format use cases with proper spacing and structure."""
    formatted_text = []
    use_cases = raw_response.split("1. ")
    for i, use_case in enumerate(use_cases[1:], start=1):  # Skip the initial split part
        formatted_text.append(f"#### {i}. {use_case.strip()}")
    return "\n\n---\n\n".join(formatted_text)


if __name__ == "__main__":
    # Example execution
    # Mocked research results for testing
    research_results = {
        "company_info": "Tesla specializes in advanced AI for autonomous vehicles and robotics.",
        "industry_trends": (
            "AI is being heavily integrated into vehicle automation, robotics, and manufacturing. "
            "AI-driven predictive maintenance and supply chain optimization are gaining traction."
        ),
    }

    # Specify company name
    company_name = "Tesla"
    
    # Generate use cases
    use_cases = generate_use_cases(company_name, research_results)
    formatted_use_cases = format_use_cases("\n".join(use_cases))

    print("--- Proposed Use Cases ---\n")
    print(formatted_use_cases)
