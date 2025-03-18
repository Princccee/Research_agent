import requests
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http import JsonResponse
from .research_main import *
from .usecase_main import *
from .resources_main import *

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

    return Response(
        {
            "message": f"Successfully completed the research for {company_name}",
            "Overview": research_results,
            "Usecases": use_cases,
            "Resources": resources
        },
        status=status.HTTP_200_OK
    )
