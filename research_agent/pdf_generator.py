import json
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListItem, ListFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def validate_json_data(data):
    required_fields = ["Overview", "Usecases", "Resources"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True

def create_pdf_from_json(json_string, output_filename=None):
    
    # Parse JSON data
    try:
        data = json.loads(json_string)
        validate_json_data(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")
    
    # Extract company name from Overview
    overview = data.get("Overview", "")
    company_name = "Company"
    if overview:
        first_sentence = overview.split('.')[0]
        words = first_sentence.split()
        if len(words) >= 2:
            company_name = words[0] + " " + words[1]
    
    # Set output filename if not provided
    if not output_filename:
        output_filename = f"{company_name.replace(' ', '_')}_Research_Report.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # MODIFY existing styles instead of adding new ones with the same name
    styles["Title"].fontSize = 20
    styles["Title"].alignment = TA_CENTER
    styles["Title"].spaceAfter = 20
    
    # Add new custom styles
    styles.add(ParagraphStyle(
        name='Section',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Subsection',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='NormalJustified',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='ResourceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        spaceBefore=6
    ))
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph(f"{company_name} Research Report", styles['Title']))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Overview Section
    elements.append(Paragraph("Overview", styles['Section']))
    elements.append(Paragraph(overview, styles['NormalJustified']))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Use Cases Section
    elements.append(Paragraph("AI/ML Use Cases", styles['Section']))
    
    if "Usecases" in data and "use_cases" in data["Usecases"]:
        for use_case in data["Usecases"]["use_cases"]:
            # Use case title
            title = use_case.get("title", "")
            elements.append(Paragraph(title, styles['Subsection']))
            
            # Explanation
            explanation = use_case.get("explanation", "")
            elements.append(Paragraph("<b>Explanation:</b>", styles['Normal']))
            elements.append(Paragraph(explanation, styles['NormalJustified']))
            
            # Practical applications
            if "practical_application" in use_case and use_case["practical_application"]:
                elements.append(Paragraph("<b>Practical Applications:</b>", styles['Normal']))
                applications = []
                for app in use_case["practical_application"]:
                    applications.append(ListItem(Paragraph(app, styles['Normal'])))
                elements.append(ListFlowable(applications, bulletType='bullet', leftIndent=20))
            
            elements.append(Spacer(1, 0.1 * inch))
    
    # Resources Section
    elements.append(Paragraph("Resources", styles['Section']))
    
    if "Resources" in data and "use_cases_resources" in data["Resources"]:
        for resource in data["Resources"]["use_cases_resources"]:
            # Resource category title
            title = resource.get("title", "")
            elements.append(Paragraph(title, styles['Subsection']))
            
            if "resources" in resource:
                res_data = resource["resources"]
                
                # HuggingFace Models
                if "huggingface_models" in res_data and res_data["huggingface_models"]:
                    elements.append(Paragraph("HuggingFace Models:", styles['ResourceTitle']))
                    models = []
                    for model in res_data["huggingface_models"]:
                        if "message" in model:
                            models.append(ListItem(Paragraph(model["message"], styles['Normal'])))
                        else:
                            model_text = f"<a href='{model.get('url', '')}'>{model.get('name', '')}</a>"
                            models.append(ListItem(Paragraph(model_text, styles['Normal'])))
                    elements.append(ListFlowable(models, bulletType='bullet', leftIndent=20))
                
                # Kaggle Datasets
                if "kaggle_datasets" in res_data and res_data["kaggle_datasets"]:
                    elements.append(Paragraph("Kaggle Datasets:", styles['ResourceTitle']))
                    datasets = []
                    for dataset in res_data["kaggle_datasets"]:
                        if "message" in dataset:
                            datasets.append(ListItem(Paragraph(dataset["message"], styles['Normal'])))
                        else:
                            dataset_text = f"<a href='{dataset.get('url', '')}'>{dataset.get('name', '')}</a>"
                            datasets.append(ListItem(Paragraph(dataset_text, styles['Normal'])))
                    elements.append(ListFlowable(datasets, bulletType='bullet', leftIndent=20))
                
                # Research Papers
                if "research_papers" in res_data and res_data["research_papers"]:
                    elements.append(Paragraph("Research Papers:", styles['ResourceTitle']))
                    papers = []
                    for paper in res_data["research_papers"]:
                        if "message" in paper:
                            papers.append(ListItem(Paragraph(paper["message"], styles['Normal'])))
                        else:
                            paper_text = f"<a href='{paper.get('url', '')}'>{paper.get('title', '')}</a>"
                            papers.append(ListItem(Paragraph(paper_text, styles['Normal'])))
                    elements.append(ListFlowable(papers, bulletType='bullet', leftIndent=20))
                
                # Handle other resource types similarly (GitHub repos, HuggingFace datasets)
                
            elements.append(Spacer(1, 0.2 * inch))
    
    # Build the PDF
    doc.build(elements)
    print(f"PDF created successfully: {output_filename}")
    return output_filename


def generate_pdf(json_file, output_filename):
    if not os.path.exists(json_file):
        # logger.error(f"JSON file '{json_file}' not found.")
        print(f"JSON file '{json_file}' not found.")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = f.read()
        
        # logger.info("Generating PDF from JSON data...")
        create_pdf_from_json(json_data, output_filename)
        # logger.info(f"PDF successfully created: {output_filename}")
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # logger.error(f"Error generating PDF: {e}")

