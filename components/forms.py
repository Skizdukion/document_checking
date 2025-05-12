import streamlit as st
from datetime import datetime


def render_personal_form():
    """Render the personal information form and handle submission."""
    with st.form("personal_info_form"):
        # Two columns for better layout
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name",
                                 value=st.session_state.personal_data.get(
                                     'name'),
                                 help="Enter your full name as it appears on your documents")

            dob = st.date_input("Date of Birth",
                                value=datetime(1998, 8, 11),
                                min_value=datetime(1940, 1, 1),
                                max_value=datetime.now(),
                                help="Select your date of birth")

            citizenship = st.text_input("Citizenship/Nationality",
                                        value=st.session_state.personal_data.get(
                                            'citizenship'),
                                        help="Enter your citizenship or nationality")

            language = st.selectbox("Preferred Language",
                                    options=["English", "Spanish", "French",
                                             "German", "Chinese", "Arabic", "Other"],
                                    index=0,  # Arabic
                                    help="Select your preferred language")

        with col2:
            gender = st.selectbox("Gender",
                                  options=["Male", "Female", "Non-binary",
                                           "Prefer not to say", "Other"],
                                  index=0,  # Male
                                  help="Select your gender")

            email = st.text_input("Email Address",
                                  value=st.session_state.personal_data.get(
                                      'email'),
                                  help="Enter your email address")

            phone = st.text_input("Phone Number",
                                  value=st.session_state.personal_data.get(
                                      'phone'),
                                  help="Enter your phone number")

            address = st.text_area("Transcripts Address During your period of study",
                                   value=st.session_state.personal_data.get(
                                       'address'),
                                   help="Enter the address that appears on your transcripts during your study period")

        # Form submission
        submitted = st.form_submit_button("Save & Continue")

        if submitted:
            # Validate inputs
            if not name:
                st.error("Please enter your full name")
            elif not email:
                st.error("Please enter your email address")
            else:
                # Store data in session state
                st.session_state.personal_data = {
                    'name': name,
                    'dob': dob.strftime('%Y-%m-%d'),
                    'citizenship': citizenship,
                    'language': language,
                    'gender': gender,
                    'email': email,
                    'phone': phone,
                    'address': address
                }

                # Move to next step
                st.session_state.step = 2
                st.rerun()


def render_academic_form():
    """Render the academic information form and handle submission."""
    with st.form("academic_info_form"):
        # Two columns for better layout
        col1, col2 = st.columns(2)

        with col1:
            university = st.text_input("University/Institution",
                                       value=st.session_state.academic_data.get(
                                           'university'),
                                       help="Enter the name of your university or institution")

            degree_level = st.selectbox("Degree Level",
                                        options=[
                                            "Associate", "Bachelor", "Master", "Doctorate", "Certificate", "Diploma", "Other"],
                                        index=1,  # Bachelor
                                        help="Select your degree level")

            major = st.text_input("Major/Field of Study",
                                  value=st.session_state.academic_data.get(
                                      'major'),
                                  help="Enter your major or field of study")

        with col2:
            study_mode = st.selectbox("Mode of Study",
                                      options=[
                                          "Full-time", "Part-time", "Mixed Mode (Part Time and Online Study)", "Distance Learning", "Exchange Program", "Other"],
                                      index=0,  # Mixed Mode
                                      help="Select your mode of study")

            grade = st.selectbox("Grade for Transcripts",
                                 options=["A", "A-", "B+", "B", "B-", "C+", "C",
                                          "C-", "D+", "D", "D-", "F", "Pass", "Fail"],
                                 index=0,  # A
                                 help="Select your grade for transcripts")

            graduation_year = st.selectbox("Year of Graduation",
                                           options=[str(year) for year in range(
                                               datetime.now().year - 10, datetime.now().year + 10)],
                                           index=list(str(year) for year in range(
                                               datetime.now().year - 10, datetime.now().year + 10)).index('2024'),
                                           help="Select your graduation year")

            graduation_season = st.selectbox("Graduation Season",
                                             options=[
                                                 "Spring", "Summer", "Autumn", "Winter"],
                                             index=0,  # Autumn
                                             help="Select your graduation season")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back to Personal Info")

        with col2:
            continue_button = st.form_submit_button("Save & Continue")

        if back_button:
            st.session_state.step = 1
            st.rerun()

        if continue_button:
            # Validate inputs
            if not university:
                st.error("Please enter your university/institution name")
            elif not major:
                st.error("Please enter your major/field of study")
            else:
                # Store data in session state
                st.session_state.academic_data = {
                    'university': university,
                    'degree_level': degree_level,
                    'major': major,
                    'study_mode': study_mode,
                    'grade': grade,
                    'graduation_year': graduation_year,
                    'graduation_season': graduation_season
                }

                # Move to next step
                st.session_state.step = 3
                st.rerun()


def render_document_upload():
    """Render the document upload form and handle submission."""
    st.write("Please upload the following required documents for validation:")
    st.write("Supported formats: PDF, JPG, JPEG, PNG")

    # Explanation of document types
    with st.expander("What documents do I need to upload?"):
        st.markdown("""
        - **Student ID Letter**: An official letter confirming your student status and ID number
        - **Student Record**: Your official student record showing enrollment details
        - **Transcripts**: Your academic transcript showing courses and grades
        - **Union Letter**: A letter from your student union or similar body confirming membership
        """)

    with st.form("document_upload_form"):
        # Document uploads
        student_id = st.file_uploader("Student ID Letter (Optional)",
                                      type=["pdf", "jpg", "jpeg", "png"],
                                      help="Upload your official student ID letter")

        student_record = st.file_uploader("Student Record (Optional)",
                                          type=["pdf", "jpg", "jpeg", "png"],
                                          help="Upload your official student record")

        transcript = st.file_uploader("Academic Transcript (Optional)",
                                      type=["pdf", "jpg", "jpeg", "png"],
                                      help="Upload your academic transcript")

        diploma = st.file_uploader("Diploma (Optional)",
                                   type=["pdf", "jpg", "jpeg", "png"],
                                   help="Upload your diploma certificate if available")

        graduation_letter = st.file_uploader("Graduation Letter (Optional)",
                                             type=["pdf", "jpg",
                                                   "jpeg", "png"],
                                             help="Upload your graduation confirmation letter if available")

        union_letter = st.file_uploader("Student Union Letter (Optional)",
                                        type=["pdf", "jpg", "jpeg", "png"],
                                        help="Upload your student union letter if available")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back to Academic Info")

        with col2:
            validate_button = st.form_submit_button("Upload & Validate")

        if back_button:
            st.session_state.step = 2
            st.rerun()

        if validate_button:
            # All documents are optional, proceed if at least one document is uploaded
            if not any([student_id, student_record, transcript, diploma, graduation_letter, union_letter]):
                st.warning(
                    "Please upload at least one document for validation")
                return

            # Store uploaded documents in session state
            st.session_state.documents = {
                'student_id': student_id,
                'student_record': student_record,
                'transcript': transcript,
                'diploma': diploma,
                'graduation_letter': graduation_letter,
                'union_letter': union_letter
            }

            # Move to next step
            st.session_state.step = 4
            st.rerun()
