import requests
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
import logging
from django.http import JsonResponse
from .research_main import *
from .usecase_main import *
from .resources_main import *
from .pdf_generator import generate_pdf

logger = logging.getLogger(__name__)

@api_view(['POST'])
def main(request):
    # fetch the company name
    company_name = request.data.get("query", "").strip()
    print(f"Conducting market research: {company_name}")
    
    # Step 1 : Market research
    research_results = get_summarized_info(company_name)
    # print(research_results)
    
    # Step 2 : AI/Ml use cases generation
    use_cases = generate_structured_usecases(company_name, research_results)
    # print(use_cases)

    # Step 3: Generate relevant resources for each usecases
    resources = collect_resources_for_usecases(use_cases)
    # print(resources)

    # Prepare response data
    response_data = {
        "message": f"Successfully completed the research for {company_name}",
        "Overview": research_results,
        "Usecases": use_cases,
        "Resources": resources
    }

     # Save response as result.json in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))  
    result_file_path = os.path.join(project_root, "result.json")

    with open(result_file_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=4, ensure_ascii=False)
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def download_pdf(request):
    json_file = "result.json"
    file_path = "final_proposal.pdf"  

    # Generate the PDF before sending it
    generate_pdf(json_file, file_path)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename="Research_Report.pdf")
    return JsonResponse({"error": "File not found"}, status=404)