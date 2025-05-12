import io
import pytesseract
from PIL import Image
import pdf2image
import spacy
import cv2
import numpy as np

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If model isn't available, use a simple pipeline instead
    nlp = spacy.blank("en")
    # Create a simple pipeline that will recognize entities
    nlp.add_pipe("ner")
    print("Using blank English model as fallback")

def process_documents(uploaded_documents):
    """
    Process uploaded documents to extract text and perform OCR.
    
    Args:
        uploaded_documents (dict): Dictionary containing uploaded document files
        
    Returns:
        dict: Processed document data with extracted text and metadata
    """
    processed_docs = {}
    
    for doc_type, file in uploaded_documents.items():
        if file is None:
            continue
            
        # Read file content
        file_content = file.getvalue()
        file_extension = file.name.split('.')[-1].lower()
        
        # Process based on file type
        if file_extension in ['pdf']:
            processed_docs[doc_type] = process_pdf(file_content, doc_type)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            processed_docs[doc_type] = process_image(file_content, doc_type)
        else:
            # For other file types, store as is
            processed_docs[doc_type] = {
                'raw_content': file_content,
                'text': None,
                'metadata': {
                    'type': file_extension,
                    'name': file.name
                }
            }
    
    return processed_docs

def process_pdf(file_content, doc_type):
    """
    Process PDF documents using OCR to extract text.
    
    Args:
        file_content (bytes): PDF file content
        doc_type (str): Type of document
        
    Returns:
        dict: Processed document data
    """
    # Convert PDF to images
    images = pdf2image.convert_from_bytes(file_content)
    extracted_text = ""
    
    # Perform OCR on each page
    for img in images:
        # Convert PIL image to numpy array for OpenCV
        img_np = np.array(img)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Preprocessing to improve OCR quality
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Perform OCR
        text = pytesseract.image_to_string(gray)
        extracted_text += text + "\n"
    
    # Analyze text with NLP
    doc = nlp(extracted_text)
    
    # Extract entities
    entities = {}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
        else:
            entities[ent.label_] = [ent.text]
    
    # Document metadata extraction
    metadata = extract_document_metadata(doc, doc_type)
    
    return {
        'raw_content': file_content,
        'text': extracted_text,
        'entities': entities,
        'metadata': metadata
    }

def process_image(file_content, doc_type):
    """
    Process image documents using OCR to extract text.
    
    Args:
        file_content (bytes): Image file content
        doc_type (str): Type of document
        
    Returns:
        dict: Processed document data
    """
    # Open image
    image = Image.open(io.BytesIO(file_content))
    
    # Convert PIL image to numpy array for OpenCV
    img_np = np.array(image)
    
    # Convert to grayscale
    if len(img_np.shape) == 3:  # Check if the image is colored
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np
    
    # Apply threshold to get a binary image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Perform OCR
    extracted_text = pytesseract.image_to_string(gray)
    
    # Analyze text with NLP
    doc = nlp(extracted_text)
    
    # Extract entities
    entities = {}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
        else:
            entities[ent.label_] = [ent.text]
    
    # Document metadata extraction
    metadata = extract_document_metadata(doc, doc_type)
    
    return {
        'raw_content': file_content,
        'text': extracted_text,
        'entities': entities,
        'metadata': metadata
    }

def extract_document_metadata(doc, doc_type):
    """
    Extract metadata from document based on its type.
    
    Args:
        doc (spacy.tokens.Doc): Processed NLP document
        doc_type (str): Type of document
        
    Returns:
        dict: Document metadata
    """
    metadata = {
        'type': doc_type,
        'format_markers': detect_format_markers(doc),
    }
    
    # Document-specific metadata extraction
    if doc_type == 'student_id':
        metadata.update(extract_student_id_metadata(doc))
    elif doc_type == 'transcript':
        metadata.update(extract_transcript_metadata(doc))
    elif doc_type == 'student_record':
        metadata.update(extract_student_record_metadata(doc))
    elif doc_type == 'union_letter':
        metadata.update(extract_union_letter_metadata(doc))
    
    return metadata

def detect_format_markers(doc):
    """
    Detect formatting markers in document.
    
    Args:
        doc (spacy.tokens.Doc): Processed NLP document
        
    Returns:
        dict: Detected format markers
    """
    text = doc.text.lower()
    
    # Look for common markers in academic documents
    markers = {
        'has_header': any(marker in text for marker in ['university', 'college', 'school', 'institute']),
        'has_footer': any(marker in text for marker in ['page', 'confidential', 'official', 'copyright']),
        'has_date': any(marker in text for marker in ['date:', 'dated:', 'issued on:']),
        'has_signature': any(marker in text for marker in ['signature', 'signed', 'authorized']),
        'has_letterhead': any(marker in text for marker in ['department', 'faculty', 'office of', 'division']),
    }
    
    return markers

def extract_student_id_metadata(doc):
    """Extract metadata specific to student ID documents"""
    text = doc.text
    
    # Look for student ID number
    id_number = None
    id_patterns = [
        r"ID\s*:\s*([A-Za-z0-9]+)",
        r"Student\s*ID\s*:\s*([A-Za-z0-9]+)",
        r"Identification\s*Number\s*:\s*([A-Za-z0-9]+)"
    ]
    
    for pattern in id_patterns:
        import re
        match = re.search(pattern, text)
        if match:
            id_number = match.group(1)
            break
    
    return {
        'id_number': id_number,
        'document_type': 'Student Identification',
    }

def extract_transcript_metadata(doc):
    """Extract metadata specific to transcript documents"""
    text = doc.text
    
    # Extract course codes and grades
    import re
    course_pattern = r"([A-Z]{2,4}\s*\d{3,4})"
    grade_pattern = r"([ABCDF][+-]?|Pass|Fail|Incomplete)"
    
    courses = re.findall(course_pattern, text)
    grades = re.findall(grade_pattern, text)
    
    # Look for GPA
    gpa = None
    gpa_patterns = [
        r"GPA\s*:\s*(\d\.\d+)",
        r"Grade Point Average\s*:\s*(\d\.\d+)"
    ]
    
    for pattern in gpa_patterns:
        match = re.search(pattern, text)
        if match:
            gpa = match.group(1)
            break
    
    return {
        'courses': courses,
        'grades': grades,
        'gpa': gpa,
        'document_type': 'Academic Transcript',
    }

def extract_student_record_metadata(doc):
    """Extract metadata specific to student record documents"""
    text = doc.text
    
    # Extract graduation year and season
    import re
    graduation_year = None
    graduation_season = None
    
    # Look for graduation year
    year_patterns = [
        r"Graduation Year\s*:\s*(\d{4})",
        r"Year of Graduation\s*:\s*(\d{4})",
        r"Class of\s*(\d{4})"
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, text)
        if match:
            graduation_year = match.group(1)
            break
            
    # Look for graduation season
    season_patterns = [
        r"Graduation Season\s*:\s*(Spring|Summer|Autumn|Winter)",
        r"(Spring|Summer|Autumn|Winter)\s+Graduation",
        r"Graduating in\s+(Spring|Summer|Autumn|Winter)"
    ]
    
    for pattern in season_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            graduation_season = match.group(1)
            break
    
    # Extract student status
    status = None
    status_patterns = [
        r"Status\s*:\s*(\w+)",
        r"Student Status\s*:\s*(\w+)",
        r"Academic Standing\s*:\s*(\w+)"
    ]
    
    for pattern in status_patterns:
        match = re.search(pattern, text)
        if match:
            status = match.group(1)
            break
    
    return {
        'graduation_year': graduation_year,
        'graduation_season': graduation_season,
        'status': status,
        'document_type': 'Student Record',
    }

def extract_union_letter_metadata(doc):
    """Extract metadata specific to union letter documents"""
    text = doc.text
    
    # Extract letter date
    import re
    letter_date = None
    date_patterns = [
        r"Date\s*:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            letter_date = match.group(1)
            break
    
    # Check for signature
    has_signature = any(sig_word in text.lower() for sig_word in ['sincerely', 'regards', 'signature', 'signed'])
    
    return {
        'letter_date': letter_date,
        'has_signature': has_signature,
        'document_type': 'Union Letter',
    }
