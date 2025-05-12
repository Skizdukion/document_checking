import streamlit as st
from utils.database import get_user_validation_history
from datetime import datetime


def render_validation_history():
    """Render the validation history page."""
    st.subheader("Your Validation History")

    # Get email from session state
    email = st.session_state.personal_data.get('email', '')

    if not email:
        st.warning(
            "Please enter your email in the Personal Information step to view your validation history.")
        return

    # Get validation history
    history = get_user_validation_history(email)

    if not history:
        st.info(f"No validation history found for {email}.")
        return

    # Display validation history
    st.write(f"Found {len(history)} validation records for {email}.")

    # Display each record in an expander
    for i, record in enumerate(history):
        # Format date for display
        created_at = record.get('created_at', '')
        if created_at:
            try:
                created_at_dt = datetime.fromisoformat(created_at)
                formatted_date = created_at_dt.strftime(
                    "%B %d, %Y at %I:%M %p")
            except:
                formatted_date = created_at
        else:
            formatted_date = "Unknown date"

        # Get status for display
        status = record.get('status', 'Unknown')
        status_icon = "✅" if status == "Passed" else "⚠️" if status == "Warning" else "❌" if status == "Failed" else "❓"

        # Create expander
        with st.expander(f"{status_icon} Validation #{i+1} - {formatted_date}"):
            # Basic info
            st.write(f"**Name:** {record.get('name', 'Unknown')}")
            st.write(f"**Status:** {status}")

            # Create tabs for different sections of data
            tabs = st.tabs(["Results", "Personal Info", "Academic Info"])

            # Results tab
            with tabs[0]:
                validation_results = record.get('validation_results', {})
                if validation_results:
                    # Display personal validation
                    personal_validation = validation_results.get(
                        'personal_validation', {})
                    st.subheader("Personal Information Validation")
                    st.write(
                        f"Status: {personal_validation.get('status', 'Unknown')}")

                    issues = personal_validation.get('issues', [])
                    if issues:
                        st.write("Issues:")
                        for issue in issues:
                            severity = issue.get('severity', 'unknown')
                            icon = "❌" if severity == "critical" else "⚠️"
                            st.write(
                                f"{icon} {issue.get('description', 'Unknown issue')}")
                    else:
                        st.write("No issues found.")

                    # Display academic validation
                    academic_validation = validation_results.get(
                        'academic_validation', {})
                    st.subheader("Academic Information Validation")
                    st.write(
                        f"Status: {academic_validation.get('status', 'Unknown')}")

                    issues = academic_validation.get('issues', [])
                    if issues:
                        st.write("Issues:")
                        for issue in issues:
                            severity = issue.get('severity', 'unknown')
                            icon = "❌" if severity == "critical" else "⚠️"
                            st.write(
                                f"{icon} {issue.get('description', 'Unknown issue')}")
                    else:
                        st.write("No issues found.")
                else:
                    st.write("No validation results available.")

            # Personal info tab
            with tabs[1]:
                personal_data = record.get('personal_data', {})
                if personal_data:
                    for key, value in personal_data.items():
                        if key != 'password' and key != 'dob':  # Hide sensitive info
                            st.write(f"**{key.title()}:** {value}")
                else:
                    st.write("No personal information available.")

            # Academic info tab
            with tabs[2]:
                academic_data = record.get('academic_data', {})
                if academic_data:
                    for key, value in academic_data.items():
                        st.write(f"**{key.title()}:** {value}")
                else:
                    st.write("No academic information available.")
