import os
import google.generativeai as genai
from typing import Dict, Any, List, Optional

# Initialize the Gemini API with the provided key
api_key = os.environ.get("GOOGLE_API_KEY")

# Configure the API
if api_key:
    genai.configure(api_key=api_key)
    # Select the model
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None
    print("Warning: GOOGLE_API_KEY not found. AI validation will be limited.")

def validate_with_ai(processed_docs: Dict[str, Any], personal_data: Dict[str, Any], academic_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini AI to validate documents by cross-referencing information.
    
    Args:
        processed_docs (dict): Dictionary containing processed documents
        personal_data (dict): Dictionary containing personal information
        academic_data (dict): Dictionary containing academic information
        
    Returns:
        dict: Validation results with issues and overall status
    """
    # Create a context dictionary with all data to send to Gemini
    validation_context = {
        "personal_data": personal_data,
        "academic_data": academic_data,
        "documents": {}
    }
    
    # Add document text to context
    for doc_type, doc_data in processed_docs.items():
        if doc_data.get('text'):
            validation_context["documents"][doc_type] = {
                "text": doc_data.get('text', ''),
                "metadata": doc_data.get('metadata', {})
            }
    
    # Generate system prompt for Gemini
    system_prompt = """
    You are an expert academic document validator. Your task is to analyze academic documents and verify their authenticity
    by cross-referencing information between different documents and user-provided personal/academic data.
    
    Analyze the following:
    1. Personal information consistency across documents (name, gender, address, etc.)
    2. Academic information consistency (university, major, graduation info, etc.)
    3. Document authenticity markers (proper formatting, letterheads, etc.)
    4. Cross-document consistency of all information
    
    For each area of validation, identify:
    - Whether it passes, has warnings, or fails
    - Specific issues found with detailed descriptions
    - Severity of each issue (warning or critical)
    
    Return your analysis as a structured assessment.
    """
    
    # Prepare prompt for document validation
    # Build document examples separately to avoid nested f-strings with backslashes
    doc_examples = ""
    for doc_type, doc_data in validation_context['documents'].items():
        doc_text = doc_data.get('text', 'No text extracted')
        # Truncate text to first 1000 chars
        truncated_text = doc_text[:1000] + "..." if len(doc_text) > 1000 else doc_text
        doc_examples += f"--- {doc_type.upper()} DOCUMENT ---\n{truncated_text}\n\n"
    
    # First part of the prompt with user data
    validation_prompt_part1 = f"""
    Here is the personal information provided by the user:
    {personal_data}
    
    Here is the academic information provided by the user:
    {academic_data}
    
    Here are the documents submitted for validation (extracted text):
    
    {doc_examples}
    
    Analyze these documents and validate them against the provided personal and academic information.
    Determine if there are any inconsistencies, missing information, or potential issues.
    
    Return your analysis in the following JSON format:
    """
    
    # Second part with JSON template (avoiding f-string for this part)
    validation_prompt_part2 = """
    {
        "personal_validation": {
            "status": "Passed|Warning|Failed",
            "issues": [
                {
                    "type": "issue_type",
                    "description": "Detailed description",
                    "severity": "warning|critical",
                    "document": "document_type"
                }
            ]
        },
        "academic_validation": {
            "status": "Passed|Warning|Failed",
            "issues": []
        },
        "document_authenticity": {
            "status": "Passed|Warning|Failed",
            "issues": []
        },
        "cross_document_consistency": {
            "status": "Passed|Warning|Failed",
            "issues": []
        },
        "overall_status": "Passed|Warning|Failed"
    }
    """
    
    # Combine the two parts
    validation_prompt = validation_prompt_part1 + validation_prompt_part2
    
    # Check if we have a model available
    if model is None:
        # If no API key or model, return a fallback validation
        fallback_result = generate_fallback_validation()
        fallback_result["personal_validation"]["issues"].append({
            "type": "api_key_missing",
            "description": "Google API Key for Gemini model is missing. Using basic validation instead.",
            "severity": "warning",
            "document": "all"
        })
        return fallback_result
        
    try:
        # Generate validation response from Gemini
        response = model.generate_content(
            [system_prompt, validation_prompt],
            generation_config={"temperature": 0.2}
        )
        
        # Extract and parse the response
        validation_result = parse_ai_response(response.text)
        
        # If we couldn't parse the response, create a fallback result
        if not validation_result:
            validation_result = generate_fallback_validation()
            validation_result["personal_validation"]["issues"].append({
                "type": "ai_parsing_error",
                "description": "Could not parse AI validation response. Using basic validation instead.",
                "severity": "warning",
                "document": "all"
            })
        
        return validation_result
    
    except Exception as e:
        # Handle errors by returning a fallback validation result
        fallback_result = generate_fallback_validation()
        fallback_result["personal_validation"]["issues"].append({
            "type": "ai_validation_error",
            "description": f"Error during AI validation: {str(e)}",
            "severity": "warning",
            "document": "all"
        })
        return fallback_result

def parse_ai_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse the AI response into a structured validation result.
    
    Args:
        response_text (str): The response text from the AI
        
    Returns:
        Optional[dict]: Structured validation result or None if parsing fails
    """
    import json
    import re
    
    # Try to extract JSON from the response
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if json_match:
        try:
            # Parse the JSON response
            validation_result = json.loads(json_match.group(0))
            
            # Calculate overall status if not provided
            if "overall_status" not in validation_result:
                # Check for critical issues
                critical_issues = 0
                warning_issues = 0
                
                for category in ['personal_validation', 'academic_validation', 'document_authenticity', 'cross_document_consistency']:
                    if category in validation_result:
                        for issue in validation_result[category].get('issues', []):
                            if issue.get('severity') == 'critical':
                                critical_issues += 1
                            elif issue.get('severity') == 'warning':
                                warning_issues += 1
                
                if critical_issues > 0:
                    validation_result['overall_status'] = 'Failed'
                elif warning_issues > 0:
                    validation_result['overall_status'] = 'Warning'
                else:
                    validation_result['overall_status'] = 'Passed'
            
            return validation_result
        
        except json.JSONDecodeError:
            return None
    
    return None

def generate_fallback_validation() -> Dict[str, Any]:
    """
    Generate a fallback validation result when AI validation fails.
    
    Returns:
        dict: Basic validation result structure
    """
    return {
        'personal_validation': {
            'status': 'Warning',
            'issues': [{
                'type': 'ai_validation_failed',
                'description': 'AI validation could not be completed. Please try again or use manual validation.',
                'severity': 'warning',
                'document': 'all'
            }]
        },
        'academic_validation': {
            'status': 'Warning',
            'issues': []
        },
        'document_authenticity': {
            'status': 'Warning',
            'issues': []
        },
        'cross_document_consistency': {
            'status': 'Warning',
            'issues': []
        },
        'overall_status': 'Warning'
    }