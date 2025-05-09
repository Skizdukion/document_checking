import streamlit as st
from datetime import datetime

def render_personal_form():
    """Render the personal information form and handle submission."""
    with st.form("personal_info_form"):
        # Two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", 
                                value=st.session_state.personal_data.get('name', ''),
                                help="Enter your full name as it appears on your documents")
            
            dob = st.date_input("Date of Birth", 
                              min_value=datetime(1940, 1, 1),
                              max_value=datetime.now(),
                              help="Select your date of birth")
            
            citizenship = st.text_input("Citizenship/Nationality", 
                                      value=st.session_state.personal_data.get('citizenship', ''),
                                      help="Enter your citizenship or nationality")
            
            language = st.selectbox("Preferred Language", 
                                  options=["English", "Spanish", "French", "German", "Chinese", "Arabic", "Other"],
                                  index=0,
                                  help="Select your preferred language")
        
        with col2:
            pronouns = st.selectbox("Pronouns", 
                                  options=["He/Him", "She/Her", "They/Them", "Prefer not to say", "Other"],
                                  index=3,
                                  help="Select your preferred pronouns")
            
            email = st.text_input("Email Address", 
                                value=st.session_state.personal_data.get('email', ''),
                                help="Enter your email address")
            
            phone = st.text_input("Phone Number", 
                                value=st.session_state.personal_data.get('phone', ''),
                                help="Enter your phone number")
            
            address = st.text_area("Current Address", 
                                 value=st.session_state.personal_data.get('address', ''),
                                 help="Enter your current address")
        
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
                    'pronouns': pronouns,
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
                                     value=st.session_state.academic_data.get('university', ''),
                                     help="Enter the name of your university or institution")
            
            degree_level = st.selectbox("Degree Level", 
                                      options=["Associate", "Bachelor", "Master", "Doctorate", "Certificate", "Diploma", "Other"],
                                      index=1,
                                      help="Select your degree level")
            
            major = st.text_input("Major/Field of Study", 
                                value=st.session_state.academic_data.get('major', ''),
                                help="Enter your major or field of study")
            
            student_id = st.text_input("Student ID/Reference Number", 
                                     value=st.session_state.academic_data.get('student_id', ''),
                                     help="Enter your student ID or reference number")
        
        with col2:
            study_mode = st.selectbox("Mode of Study", 
                                    options=["Full-time", "Part-time", "Distance Learning", "Exchange Program", "Other"],
                                    index=0,
                                    help="Select your mode of study")
            
            grade = st.text_input("Overall Grade/GPA", 
                                value=st.session_state.academic_data.get('grade', ''),
                                help="Enter your overall grade or GPA")
            
            enrollment_date = st.date_input("Enrollment Date", 
                                         value=datetime(2020, 9, 1),
                                         help="Select your enrollment date")
            
            graduation_date = st.date_input("Graduation Date (Expected)", 
                                         value=datetime(2024, 6, 1),
                                         help="Select your expected graduation date")
        
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
            elif not student_id:
                st.error("Please enter your student ID/reference number")
            else:
                # Store data in session state
                st.session_state.academic_data = {
                    'university': university,
                    'degree_level': degree_level,
                    'major': major,
                    'student_id': student_id,
                    'study_mode': study_mode,
                    'grade': grade,
                    'enrollment_date': enrollment_date.strftime('%Y-%m-%d'),
                    'graduation_date': graduation_date.strftime('%Y-%m-%d')
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
        student_id = st.file_uploader("Student ID Letter (Required)", 
                                    type=["pdf", "jpg", "jpeg", "png"],
                                    help="Upload your official student ID letter")
        
        student_record = st.file_uploader("Student Record (Required)", 
                                        type=["pdf", "jpg", "jpeg", "png"],
                                        help="Upload your official student record")
        
        transcript = st.file_uploader("Academic Transcript (Required)", 
                                    type=["pdf", "jpg", "jpeg", "png"],
                                    help="Upload your academic transcript")
        
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
            # Check required documents
            missing_docs = []
            if student_id is None:
                missing_docs.append("Student ID Letter")
            if student_record is None:
                missing_docs.append("Student Record")
            if transcript is None:
                missing_docs.append("Academic Transcript")
            
            if missing_docs:
                st.error(f"Please upload the following required documents: {', '.join(missing_docs)}")
            else:
                # Store uploaded documents in session state
                st.session_state.documents = {
                    'student_id': student_id,
                    'student_record': student_record,
                    'transcript': transcript,
                    'union_letter': union_letter
                }
                
                # Move to next step
                st.session_state.step = 4
                st.rerun()
