import os
import re
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API key
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_ai_usecases(company_name, company_summary):
    """Generates the top 5 relevant AI/ML use cases for the given company in bullet points."""
    prompt = (
        f"Based on the following company summary, suggest the **top 5 most impactful** AI and Machine Learning use cases "
        f"that {company_name} can implement. Provide practical applications aligned with the company's industry and services. "
        f"Format the response as a **clear, structured bullet-point list**, with each use case briefly explained:\n\n{company_summary}"
    )

    model = "gemini-2.0-flash"

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text

def parse_usecases(use_cases_text):
    """Parses the AI-generated use cases into a structured JSON format."""
    use_cases = []
    
    pattern = re.compile(r'\*\*\d+\.\s(.*?)\*\*:\n\s*\*\*(Explanation|Description):\*\*(.*?)\n\s*\*\*(Practical Application|Examples):\*\*(.*?)\n', re.S)
    matches = pattern.findall(use_cases_text)
    
    for match in matches:
        title = match[0].strip()
        explanation = match[2].strip()
        practical_applications = [app.strip() for app in match[4].strip().split('\n') if app.strip()]
        
        use_cases.append({
            "title": title,
            "explanation": explanation,
            "practical_application": practical_applications
        })
    
    return json.dumps({"use_cases": use_cases}, indent=4)

def generate_structured_usecases(company_name, reseach_result):
    use_cases = generate_ai_usecases(company_name, reseach_result)
    return parse_usecases(use_cases)

if __name__ == "__main__":
    company_summary = input("Enter the company summary: ")
    use_cases = generate_ai_usecases(company_summary)
    print("\nAI/ML Use Cases:\n", use_cases)
