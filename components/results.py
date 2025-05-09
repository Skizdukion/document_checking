import streamlit as st

def display_validation_results(validation_results):
    """
    Display the validation results with detailed feedback.
    
    Args:
        validation_results (dict): Validation results from the validator
    """
    # Display overall status with appropriate styling
    overall_status = validation_results['overall_status']
    
    if overall_status == 'Passed':
        st.success("✅ Document Validation Passed")
    elif overall_status == 'Warning':
        st.warning("⚠️ Document Validation Passed with Warnings")
    else:
        st.error("❌ Document Validation Failed")
    
    # Summary section
    st.subheader("Validation Summary")
    
    # Use columns for the summary boxes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_category_result("Personal Information", validation_results['personal_validation']['status'])
    
    with col2:
        display_category_result("Academic Information", validation_results['academic_validation']['status'])
    
    with col3:
        display_category_result("Document Authenticity", validation_results['document_authenticity']['status'])
    
    with col4:
        display_category_result("Cross-Document Consistency", validation_results['cross_document_consistency']['status'])
    
    # Detailed results section
    st.subheader("Detailed Validation Results")
    
    # Personal validation details
    with st.expander("Personal Information Validation", expanded=overall_status != 'Passed'):
        display_category_details(validation_results['personal_validation'])
    
    # Academic validation details
    with st.expander("Academic Information Validation", expanded=overall_status != 'Passed'):
        display_category_details(validation_results['academic_validation'])
    
    # Document authenticity details
    with st.expander("Document Authenticity Validation", expanded=overall_status != 'Passed'):
        display_category_details(validation_results['document_authenticity'])
    
    # Cross-document consistency details
    with st.expander("Cross-Document Consistency Validation", expanded=overall_status != 'Passed'):
        display_category_details(validation_results['cross_document_consistency'])
    
    # Display recommendations based on validation results
    st.subheader("Recommendations")
    
    if overall_status == 'Passed':
        st.write("✅ All documents have been successfully validated. No issues found.")
    else:
        st.write("Based on the validation results, we recommend the following actions:")
        
        # Generate recommendations based on issues found
        all_issues = []
        for category in ['personal_validation', 'academic_validation', 'document_authenticity', 'cross_document_consistency']:
            all_issues.extend(validation_results[category]['issues'])
        
        if all_issues:
            for issue in all_issues:
                severity = issue['severity']
                if severity == 'critical':
                    st.error(f"❌ **Critical Issue**: {issue['description']}")
                else:
                    st.warning(f"⚠️ **Warning**: {issue['description']}")
        else:
            st.write("No specific issues found, but some validation checks didn't pass completely.")

def display_category_result(category_name, status):
    """
    Display a category result in a colored box.
    
    Args:
        category_name (str): Name of the validation category
        status (str): Status of the validation (Passed, Warning, Failed)
    """
    if status == 'Passed':
        st.success(f"{category_name}: Passed")
    elif status == 'Warning':
        st.warning(f"{category_name}: Warning")
    else:
        st.error(f"{category_name}: Failed")

def display_category_details(category_results):
    """
    Display detailed results for a validation category.
    
    Args:
        category_results (dict): Results for a specific validation category
    """
    status = category_results['status']
    issues = category_results['issues']
    
    if status == 'Passed':
        st.write("✅ All checks passed successfully.")
    else:
        if issues:
            for issue in issues:
                issue_type = issue['type']
                description = issue['description']
                severity = issue['severity']
                document = issue.get('document', 'Multiple documents')
                
                if severity == 'critical':
                    st.error(f"❌ **{issue_type}** in {document}: {description}")
                else:
                    st.warning(f"⚠️ **{issue_type}** in {document}: {description}")
        else:
            st.write("No specific issues identified.")
