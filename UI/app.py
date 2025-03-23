import streamlit as st
import requests

# Django API endpoint
BACKEND_URL = "https://ai-research-agent-wn06.onrender.com"
# BACKEND_URL = "http://localhost:8000/"

st.set_page_config(page_title="Research Agent", layout="wide")

# UI Layout
st.title("Research Agent")

# Text input at the bottom
user_input = st.text_input("Enter your query:", "")

# Send button
if st.button("Send"):
    with st.spinner("Processing..."):
        response = requests.post(f"{BACKEND_URL}/api/main/", json={"query": user_input})

        if response.status_code == 200:
            data = response.json()
            
            # Display dropdowns
            with st.expander("Overview"):
                st.write(data["Overview"])
            
            with st.expander("Usecases"):
                for usecase in data["Usecases"]["use_cases"]:
                    st.subheader(usecase["title"])
                    st.write(usecase["explanation"])
                    applications = usecase["practical_application"]
                    for app in applications:
                        st.write(f"- {app}")

            # Resources Section
            st.header("📚 Resources")

            for resource in data["Resources"]["use_cases_resources"]:
                st.subheader(resource["title"])
                resources = resource.get("resources", {})

                # Hugging Face Models
                st.subheader("🤖 Hugging Face Models")
                for model in resources.get("huggingface_models", []):
                    st.write(f"🔗 {model}")

                # Hugging Face Datasets
                st.subheader("📂 Hugging Face Datasets")
                for dataset in resources.get("huggingface_datasets", []):
                    st.write(f"🔗 {dataset}")

                # Kaggle Datasets
                st.subheader("📊 Kaggle Datasets")
                for kaggle in resources.get("kaggle_datasets", []):
                    st.write(f"🔗 {kaggle}")

                # GitHub Repositories
                st.subheader("💻 GitHub Repositories")
                for repo in resources.get("github_repositories", []):
                    st.write(f"🔗 {repo}")

                # Research Papers
                st.subheader("📜 Research Papers")
                for paper in resources.get("research_papers", []):
                    st.write(f"📄 {paper}")
        else:
            st.error("Error fetching data. Try again.")

# Download button
if st.button("Download PDF"):
    pdf_url = f"{BACKEND_URL}api/download_pdf/"
    response = requests.get(pdf_url)

    if response.status_code == 200:
        st.download_button(
        label="Download PDF",
        data=response.content,  # File content
        file_name="Research_Report.pdf",
        mime="application/pdf"
    )
    else:
        st.error("Error downloading the file.")
