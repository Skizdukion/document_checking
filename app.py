import streamlit as st
from components.forms import render_personal_form, render_academic_form, render_document_upload
from components.results import display_validation_results
from components.history import render_validation_history
from utils.document_processor import process_documents
from utils.ai_validator import validate_with_ai
from utils.database import save_validation_data, get_user_validation_history


def main():
    # Configure page
    st.set_page_config(
        page_title="Academic Document Validation System",
        page_icon="📚",
        layout="wide"
    )

    # App title
    st.title("Academic Document Validation System")
    st.markdown("Verify the authenticity of academic credentials and documents")

    # Initialize session state for multi-step process
    if 'step' not in st.session_state:
        st.session_state.step = 1

    if 'personal_data' not in st.session_state:
        st.session_state.personal_data = {}

    if 'academic_data' not in st.session_state:
        st.session_state.academic_data = {}

    if 'documents' not in st.session_state:
        st.session_state.documents = {}

    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None

    # Progress bar for steps
    progress_text = f"Step {st.session_state.step} of 4"
    progress_value = st.session_state.step / 4
    st.progress(progress_value, text=progress_text)

    # Display different forms based on current step
    if st.session_state.step == 1:
        st.subheader("Step 1: Personal Information")
        render_personal_form()

    elif st.session_state.step == 2:
        st.subheader("Step 2: Academic Information")
        render_academic_form()

    elif st.session_state.step == 3:
        st.subheader("Step 3: Document Upload")
        render_document_upload()

    elif st.session_state.step == 4:
        st.subheader("Step 4: AI-Powered Validation Results")
        st.markdown("_Documents are being analyzed by our AI system using Google's Gemini model_")

        # Process and validate documents if not already done
        if st.session_state.validation_results is None:
            with st.spinner("Processing and validating documents..."):
                processed_docs = process_documents(st.session_state.documents)
                validation_results = validate_with_ai(
                    processed_docs,
                    st.session_state.personal_data,
                    st.session_state.academic_data
                )
                st.session_state.validation_results = validation_results
                
                # Save validation data to the database
                with st.spinner("Saving validation data to database..."):
                    saved = save_validation_data(
                        st.session_state.personal_data,
                        st.session_state.academic_data,
                        validation_results
                    )
                    if saved:
                        st.success("Validation data saved successfully")
                    else:
                        st.warning("Could not save validation data to database")

        # Display validation results
        display_validation_results(st.session_state.validation_results)

        # Reset button
        if st.button("Start New Validation"):
            # Reset all session state
            for key in ['step', 'personal_data', 'academic_data', 'documents', 'validation_results']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
