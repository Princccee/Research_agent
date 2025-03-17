import requests
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from django.http import JsonResponse
from .research_main import *
from .research import *
from .usecase import *
from .resource import *

logger = logging.getLogger(__name__)

@api_view(['POST'])
def research(request):
    # Get the name of company or industry from the request:
    company_name = request.data.get("query", "").strip()

    raw_data = research_industry(company_name)
    # print(f"Raw data from internet: \n {raw_data}")

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

    filename = generate_markdown_file(company_name, summarized_company_info)

    return Response(
        {"message": "Report generated successfully.", "filename": filename},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def main(request):
    # fetch the company name
    company_name = request.data.get("query", "").strip()
    print(f"Conducting market research: {company_name}")
    
    # Step 1 : Market research
    research_results = get_summarized_info(company_name)
    # research_insights = research_industry_with_summary(company_name)
    print(f"Research insights: {research_results}")
    
    # # Step 1 : AI/Ml use cases generation
    # use_cases = generate_use_cases(company_name,research_results )
    # print(f"Use cases: {use_cases}")

    # # Step 3: Resources for each use-cases:
    # for use_case in use_cases:
    #     resource_asset_agent(use_case)

    return Response(
        {
            "message": f"Successfully completed the research for {company_name}",
            "Overview": f"{research_results}",
            # "Usecases": f"{use_cases}",
        },
        status=status.HTTP_200_OK
    )
