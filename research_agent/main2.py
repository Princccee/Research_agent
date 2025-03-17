import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_groq import ChatGroq


load_dotenv()


SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = "qwen-2.5-32b"


search_tool = SerperDevTool()


company = input("Enter company name: ")

print(" Fetching company information...")
company_info_result = search_tool._run(f"{company} company overview")


print("\n Company Info Result from Search:\n", company_info_result, "\n")


if not company_info_result or len(company_info_result.strip()) < 5:
    print("Error: No valid company info found. Exiting.")
    exit()

print(" Company information fetched.")


company_info = Agent(
    llm=ChatGroq(model_name=GROQ_MODEL, api_key=GROQ_API_KEY),  
    role="Senior Company Information Retriever",
    goal=f"Retrieve and provide detailed information about {company}.",
    verbose=True,
    memory=True,
    backstory="Driven by curiosity, you're at the forefront of innovation.",
    tools=[search_tool],
    allow_delegation=False
)

ai_info_research = Agent(
    llm=ChatGroq(model_name=GROQ_MODEL, api_key=GROQ_API_KEY),  
    role="AI Information Researcher",
    goal=f"Analyze the operations of {company} and generate AI use cases based on the provided data.",
    verbose=True,
    memory=True,
    backstory="Driven by curiosity, you're at the forefront of innovation.",
    tools=[],
    allow_delegation=False
)


info_task = Task(
    description=f"Summarize the following information about {company}: {company_info_result}",
    expected_output="A structured summary of the company's business activities.",
    agent=company_info,
)

use_case_task = Task(
    description=f"Using the given company information, generate AI use cases for {company}.",
    expected_output="A detailed AI use case for the company.",
    agent=ai_info_research,
    
)


crew = Crew(
    agents=[company_info, ai_info_research],
    tasks=[info_task, use_case_task],
    process=Process.sequential  
)

results = crew.kickoff()


print("\n CrewAI Execution Results:\n", results)


if isinstance(results, str):
    company_summary = results
    ai_use_case = "AI use cases not generated."
elif isinstance(results, list) and len(results) >= 2:
    company_summary = results[0] if results[0] else "No valid company summary generated."
    ai_use_case = results[1] if results[1] else "No valid AI use case generated."
else:
    company_summary = "No valid company summary generated."
    ai_use_case = "No valid AI use case generated."

# Write to Markdown file
with open("new-usecase-post.md", "w", encoding="utf-8") as file:
    # file.write(f"# {company} - Company Overview\n\n")
    file.write(f"##  Company Information\n\n{company_summary}\n\n")
    # file.write(f"##  AI Use Cases\n\n{ai_use_case}\n")

print("\n Results saved successfully to new-usecase-post.md")