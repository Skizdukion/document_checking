import difflib
import re
from datetime import datetime


def validate_documents(processed_docs, personal_data, academic_data):
    """
    Validate documents by cross-referencing information.

    Args:
        processed_docs (dict): Dictionary containing processed documents
        personal_data (dict): Dictionary containing personal information
        academic_data (dict): Dictionary containing academic information

    Returns:
        dict: Validation results with issues and overall status
    """
    results = {
        'personal_validation': validate_personal_info(processed_docs, personal_data),
        'academic_validation': validate_academic_info(processed_docs, academic_data),
        'document_authenticity': validate_document_authenticity(processed_docs),
        'cross_document_consistency': validate_cross_document_consistency(processed_docs),
        'overall_status': 'Processing'
    }

    # Calculate overall status based on validation results
    critical_issues = 0
    warning_issues = 0

    for category in ['personal_validation', 'academic_validation', 'document_authenticity', 'cross_document_consistency']:
        for issue in results[category]['issues']:
            if issue['severity'] == 'critical':
                critical_issues += 1
            elif issue['severity'] == 'warning':
                warning_issues += 1

    if critical_issues > 0:
        results['overall_status'] = 'Failed'
    elif warning_issues > 0:
        results['overall_status'] = 'Warning'
    else:
        results['overall_status'] = 'Passed'

    return results


def validate_personal_info(processed_docs, personal_data):
    """
    Validate personal information across documents.

    Args:
        processed_docs (dict): Dictionary containing processed documents
        personal_data (dict): Dictionary containing personal information

    Returns:
        dict: Validation results for personal information
    """
    validation_result = {
        'issues': [],
        'status': 'Processing'
    }

    # Get name from personal data
    full_name = personal_data.get('name', '').lower()
    dob = personal_data.get('dob', '')

    # Prepare name parts for flexible matching
    name_parts = full_name.split()

    # Validate name across documents
    name_found = False

    for doc_type, doc_data in processed_docs.items():
        text = doc_data.get('text', '').lower()

        # Check if name parts appear in document
        name_matches = 0
        for part in name_parts:
            # Only check parts with length > 2 (skip "de", "la", etc.)
            if len(part) > 2 and part in text:
                name_matches += 1

        # If more than half of name parts are found, consider it a match
        if name_matches >= len(name_parts) / 2:
            name_found = True
        else:
            validation_result['issues'].append({
                'type': 'name_mismatch',
                'document': doc_type,
                'description': f'Name "{full_name}" not clearly found in {doc_type}',
                'severity': 'warning'
            })

    # Validate date of birth if provided
    if dob:
        dob_found = False

        # Try different date formats
        dob_obj = None
        try:
            dob_obj = datetime.strptime(dob, '%Y-%m-%d')
        except:
            try:
                dob_obj = datetime.strptime(dob, '%d/%m/%Y')
            except:
                pass

        if dob_obj:
            # Generate different DOB formats to search for
            dob_formats = [
                dob_obj.strftime('%d/%m/%Y'),
                dob_obj.strftime('%d-%m-%Y'),
                dob_obj.strftime('%Y-%m-%d'),
                dob_obj.strftime('%Y/%m/%d'),
                dob_obj.strftime('%d %B %Y'),
                dob_obj.strftime('%B %d, %Y')
            ]

            for doc_type, doc_data in processed_docs.items():
                text = doc_data.get('text', '')

                for dob_format in dob_formats:
                    if dob_format in text:
                        dob_found = True
                        break

            if not dob_found:
                validation_result['issues'].append({
                    'type': 'dob_mismatch',
                    'description': 'Date of birth not found in any document',
                    'severity': 'warning'
                })

    # Validate other personal info (citizenship, address, etc.)
    for field in ['citizenship', 'address', 'gender']:
        if personal_data.get(field):
            field_value = personal_data[field].lower()
            field_found = False

            for doc_type, doc_data in processed_docs.items():
                text = doc_data.get('text', '').lower()

                # For address, check if key parts are present
                if field == 'address':
                    address_parts = re.split(r'[,\n]', field_value)
                    address_matches = 0
                    for part in address_parts:
                        part = part.strip()
                        if len(part) > 3 and part in text:
                            address_matches += 1

                    if address_matches >= len(address_parts) / 2:
                        field_found = True
                elif field_value in text:
                    field_found = True

            if not field_found:
                validation_result['issues'].append({
                    'type': f'{field}_mismatch',
                    'description': f'{field.capitalize()} information not found in documents',
                    'severity': 'warning'
                })

    # Set status based on issues
    critical_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'critical')
    warning_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'warning')

    if critical_issues > 0:
        validation_result['status'] = 'Failed'
    elif warning_issues > 0:
        validation_result['status'] = 'Warning'
    else:
        validation_result['status'] = 'Passed'

    return validation_result


def validate_academic_info(processed_docs, academic_data):
    """
    Validate academic information across documents.

    Args:
        processed_docs (dict): Dictionary containing processed documents
        academic_data (dict): Dictionary containing academic information

    Returns:
        dict: Validation results for academic information
    """
    validation_result = {
        'issues': [],
        'status': 'Processing'
    }

    # Get academic info from form data
    major = academic_data.get('major', '').lower()
    degree_level = academic_data.get('degree_level', '').lower()
    university = academic_data.get('university', '').lower()
    study_mode = academic_data.get('study_mode', '').lower()
    grade = academic_data.get('grade', '').lower()
    graduation_year = academic_data.get('graduation_year', '')
    graduation_season = academic_data.get('graduation_season', '').lower()

    # Check for major in documents
    if major:
        major_found = False
        for doc_type, doc_data in processed_docs.items():
            text = doc_data.get('text', '').lower()
            if major in text:
                major_found = True
                break

        if not major_found:
            validation_result['issues'].append({
                'type': 'major_mismatch',
                'description': f'Major "{major}" not found in documents',
                'severity': 'warning'
            })

    # Check for university in documents
    if university:
        university_found = False

        # Break university name into parts for flexible matching
        university_parts = university.split()

        for doc_type, doc_data in processed_docs.items():
            text = doc_data.get('text', '').lower()

            # Check for full university name
            if university in text:
                university_found = True
                break

            # Check for partial matches (e.g., "MIT" instead of "Massachusetts Institute of Technology")
            matches = 0
            for part in university_parts:
                if len(part) > 2 and part in text:
                    matches += 1

            if matches >= len(university_parts) / 2:
                university_found = True
                break

        if not university_found:
            validation_result['issues'].append({
                'type': 'university_mismatch',
                'description': f'University "{university}" not found in documents',
                'severity': 'critical'
            })

    # Check for degree level in documents
    if degree_level:
        degree_found = False

        # Common abbreviations for degree levels
        degree_variants = {
            'bachelor': ['bachelor', 'bachelor\'s', 'bachelors', 'b.a.', 'b.s.', 'b.sc', 'bs', 'ba'],
            'master': ['master', 'master\'s', 'masters', 'm.a.', 'm.s.', 'm.sc', 'ms', 'ma'],
            'doctorate': ['doctorate', 'doctoral', 'ph.d.', 'phd', 'doctor of philosophy'],
            'associate': ['associate', 'a.a.', 'a.s.', 'associate\'s']
        }

        # Find which variants apply to the provided degree level
        applicable_variants = []
        for key, variants in degree_variants.items():
            if key in degree_level:
                applicable_variants.extend(variants)

        for doc_type, doc_data in processed_docs.items():
            text = doc_data.get('text', '').lower()

            for variant in applicable_variants:
                if variant in text:
                    degree_found = True
                    break

        if not degree_found:
            validation_result['issues'].append({
                'type': 'degree_level_mismatch',
                'description': f'Degree level "{degree_level}" not found in documents',
                'severity': 'warning'
            })

    # Check for grade in transcript if provided
    if grade and 'transcript' in processed_docs:
        transcript_text = processed_docs['transcript'].get('text', '').lower()

        # Check for different grade formats
        grade_pattern = r"(([A-D][+-]?|F)|pass|fail)"
        grades_in_transcript = re.findall(
            grade_pattern, transcript_text, re.IGNORECASE)

        # Extract actual grades (first element of each tuple)
        grades_in_transcript = [g[0] for g in grades_in_transcript if g[0]]

        if not grades_in_transcript:
            validation_result['issues'].append({
                'type': 'grade_not_found',
                'description': 'No grades found in transcript',
                'severity': 'warning'
            })

    # Check for graduation year and season if provided
    if graduation_year and 'student_record' in processed_docs:
        student_record = processed_docs['student_record']
        metadata = student_record.get('metadata', {})
        record_graduation_year = metadata.get('graduation_year')

        if not record_graduation_year:
            validation_result['issues'].append({
                'type': 'graduation_year_not_found',
                'description': 'Graduation year not found in student record',
                'severity': 'warning'
            })
        elif graduation_year != record_graduation_year:
            validation_result['issues'].append({
                'type': 'graduation_year_mismatch',
                'description': f'Graduation year in form ({graduation_year}) does not match record ({record_graduation_year})',
                'severity': 'warning'
            })

    if graduation_season and 'student_record' in processed_docs:
        student_record = processed_docs['student_record']
        metadata = student_record.get('metadata', {})
        record_graduation_season = metadata.get(
            'graduation_season', '').lower()

        if not record_graduation_season:
            validation_result['issues'].append({
                'type': 'graduation_season_not_found',
                'description': 'Graduation season not found in student record',
                'severity': 'warning'
            })
        elif graduation_season != record_graduation_season.lower():
            validation_result['issues'].append({
                'type': 'graduation_season_mismatch',
                'description': f'Graduation season in form ({graduation_season}) does not match record ({record_graduation_season})',
                'severity': 'warning'
            })

    # Set status based on issues
    critical_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'critical')
    warning_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'warning')

    if critical_issues > 0:
        validation_result['status'] = 'Failed'
    elif warning_issues > 0:
        validation_result['status'] = 'Warning'
    else:
        validation_result['status'] = 'Passed'

    return validation_result


def validate_document_authenticity(processed_docs):
    """
    Validate document authenticity by checking for expected formatting elements.

    Args:
        processed_docs (dict): Dictionary containing processed documents

    Returns:
        dict: Validation results for document authenticity
    """
    validation_result = {
        'issues': [],
        'status': 'Processing'
    }

    # Check each document for expected formatting markers
    for doc_type, doc_data in processed_docs.items():
        # Get format markers
        metadata = doc_data.get('metadata', {})
        format_markers = metadata.get('format_markers', {})

        # Document specific checks
        if doc_type == 'student_id':
            # Student ID should have header, ID number, and name
            if not format_markers.get('has_header', False):
                validation_result['issues'].append({
                    'type': 'missing_header',
                    'document': doc_type,
                    'description': 'Student ID letter lacks proper header',
                    'severity': 'warning'
                })

            # Check for ID number
            if not metadata.get('id_number'):
                validation_result['issues'].append({
                    'type': 'missing_id_number',
                    'document': doc_type,
                    'description': 'No student ID number found in ID letter',
                    'severity': 'critical'
                })

        elif doc_type == 'transcript':
            # Transcripts should have header, footer, and course information
            if not format_markers.get('has_header', False):
                validation_result['issues'].append({
                    'type': 'missing_header',
                    'document': doc_type,
                    'description': 'Transcript lacks proper university header',
                    'severity': 'warning'
                })

            # Check for courses and grades
            courses = metadata.get('courses', [])
            grades = metadata.get('grades', [])

            if not courses:
                validation_result['issues'].append({
                    'type': 'missing_courses',
                    'document': doc_type,
                    'description': 'No course codes found in transcript',
                    'severity': 'critical'
                })

            if not grades:
                validation_result['issues'].append({
                    'type': 'missing_grades',
                    'document': doc_type,
                    'description': 'No grades found in transcript',
                    'severity': 'critical'
                })

        elif doc_type == 'student_record':
            # Student records should have letterhead, student status, and enrollment info
            if not format_markers.get('has_letterhead', False):
                validation_result['issues'].append({
                    'type': 'missing_letterhead',
                    'document': doc_type,
                    'description': 'Student record lacks official letterhead',
                    'severity': 'warning'
                })

            # Check for student status instead of enrollment date
            if not metadata.get('status'):
                validation_result['issues'].append({
                    'type': 'missing_status',
                    'document': doc_type,
                    'description': 'No student status found in student record',
                    'severity': 'warning'
                })

        elif doc_type == 'union_letter':
            # Union letters should have date, signature, and formal letter structure
            if not format_markers.get('has_header', False):
                validation_result['issues'].append({
                    'type': 'missing_header',
                    'document': doc_type,
                    'description': 'Union letter lacks organizational header',
                    'severity': 'warning'
                })

            if not metadata.get('has_signature', False):
                validation_result['issues'].append({
                    'type': 'missing_signature',
                    'document': doc_type,
                    'description': 'No signature found in union letter',
                    'severity': 'warning'
                })

        # Check all documents for common authenticity markers
        if not format_markers.get('has_date', False):
            validation_result['issues'].append({
                'type': 'missing_date',
                'document': doc_type,
                'description': f'No date found in {doc_type}',
                'severity': 'warning'
            })

    # Set status based on issues
    critical_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'critical')
    warning_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'warning')

    if critical_issues > 0:
        validation_result['status'] = 'Failed'
    elif warning_issues > 0:
        validation_result['status'] = 'Warning'
    else:
        validation_result['status'] = 'Passed'

    return validation_result


def validate_cross_document_consistency(processed_docs):
    """
    Validate consistency of information across multiple documents.

    Args:
        processed_docs (dict): Dictionary containing processed documents

    Returns:
        dict: Validation results for cross-document consistency
    """
    validation_result = {
        'issues': [],
        'status': 'Processing'
    }

    # Check if we have multiple documents to compare
    if len(processed_docs) < 2:
        validation_result['status'] = 'Passed'
        return validation_result

    # Extract names from different documents
    names_by_doc = {}
    for doc_type, doc_data in processed_docs.items():
        text = doc_data.get('text', '')
        entities = doc_data.get('entities', {})

        # Try to extract names from entities if available
        person_entities = entities.get('PERSON', [])
        if person_entities:
            # Use the first person entity
            names_by_doc[doc_type] = person_entities[0]
        else:
            # Try simple name extraction with regex
            name_patterns = [
                r"name\s*:\s*([A-Za-z\s]+)",
                r"([A-Za-z]+\s+[A-Za-z]+)",  # Simple two-word name
            ]

            for pattern in name_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    names_by_doc[doc_type] = match.group(1).strip()
                    break

    # Compare names across documents
    if len(names_by_doc) >= 2:
        names = list(names_by_doc.values())
        reference_name = names[0]

        for doc_type, name in list(names_by_doc.items())[1:]:
            # Calculate string similarity
            similarity = difflib.SequenceMatcher(
                None, reference_name.lower(), name.lower()).ratio()

            if similarity < 0.7:  # Names are too different
                validation_result['issues'].append({
                    'type': 'name_inconsistency',
                    'documents': [list(names_by_doc.keys())[0], doc_type],
                    'description': f'Name inconsistency between documents: "{reference_name}" vs "{name}"',
                    'severity': 'critical'
                })

    # Extract dates from different documents
    dates_by_doc = {}
    for doc_type, doc_data in processed_docs.items():
        text = doc_data.get('text', '')

        # Try to extract dates with regex
        date_patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # DD/MM/YYYY or MM/DD/YYYY
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",    # YYYY/MM/DD
            # DD Month YYYY
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                dates_by_doc[doc_type] = matches
                break

    # Check for document issuance timeline consistency
    if len(dates_by_doc) >= 2:
        # Check if any document has a future date
        for doc_type, dates in dates_by_doc.items():
            for date_str in dates:
                try:
                    # Try to parse the date in different formats
                    date_obj = None
                    for fmt in ('%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d'):
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue

                    if date_obj and date_obj > datetime.now():
                        validation_result['issues'].append({
                            'type': 'future_date',
                            'document': doc_type,
                            'description': f'Document contains a future date: {date_str}',
                            'severity': 'critical'
                        })
                except:
                    # If date parsing fails, just continue
                    pass

    # Set status based on issues
    critical_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'critical')
    warning_issues = sum(
        1 for issue in validation_result['issues'] if issue['severity'] == 'warning')

    if critical_issues > 0:
        validation_result['status'] = 'Failed'
    elif warning_issues > 0:
        validation_result['status'] = 'Warning'
    else:
        validation_result['status'] = 'Passed'

    return validation_result
