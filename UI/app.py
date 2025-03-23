import streamlit as st
import requests

# Django API endpoint
# BACKEND_URL = "https://ai-research-agent-wn06.onrender.com"
BACKEND_URL = "http://localhost:8000/"


st.set_page_config(page_title="Research Agent", layout="wide")

# Initialize session state for storing selected resources
if "selected_resources" not in st.session_state:
    st.session_state.selected_resources = {}

# UI Layout
st.title("Research Agent")

# Text input at the bottom
user_input = st.text_input("Enter your query:", "")

# Send button
if st.button("Send"):
    with st.spinner("Processing..."):
        try:
            response = requests.post(f"{BACKEND_URL}/api/main/", json={"query": user_input})
            response.raise_for_status()
            data = response.json()

            # Store API response in session state
            st.session_state.selected_resources = data.get("Resources", {}).get("use_cases_resources", [])

            # Display Overview
            with st.expander("📌 Overview", expanded=True):
                st.write(data.get("Overview", "No overview available."))

            # Display Use Cases
            with st.expander("💡 Use Cases"):
                for usecase in data.get("Usecases", {}).get("use_cases", []):
                    st.subheader(usecase["title"])
                    st.write(usecase["explanation"])
                    applications = usecase.get("practical_application", [])
                    if applications:
                        st.markdown("**Practical Applications:**")
                        for app in applications:
                            st.write(f"- {app}")

        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Error fetching data: {e}")

# Resources Section
st.header("📚 Resources")

# Get available categories
resource_titles = [res["title"] for res in st.session_state.selected_resources]

# Selection box for choosing resource category
selected_title = st.selectbox("Select a resource category", resource_titles)

# Retrieve selected resource details from session state
selected_resource = next(
    (r for r in st.session_state.selected_resources if r["title"] == selected_title),
    None
)

if selected_resource:
    resources = selected_resource.get("resources", {})
    
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            if "huggingface_models" in resources:
                with st.expander("🤖 Hugging Face Models"):
                    for model in resources["huggingface_models"]:
                        st.write(f"🔗 {model.get('message', model)}")

            if "huggingface_datasets" in resources:
                with st.expander("📂 Hugging Face Datasets"):
                    for dataset in resources["huggingface_datasets"]:
                        st.markdown(f"🔗 [{dataset.get('name', 'Dataset')}]({dataset.get('url', '#')})")

        with col2:
            if "kaggle_datasets" in resources:
                with st.expander("📊 Kaggle Datasets"):
                    for kaggle in resources["kaggle_datasets"]:
                        st.markdown(f"🔗 [{kaggle['name']}]({kaggle['url']})")

            if "github_repositories" in resources:
                with st.expander("💻 GitHub Repositories"):
                    for repo in resources["github_repositories"]:
                        st.write(f"🔗 {repo}")

            if "research_papers" in resources:
                with st.expander("📜 Research Papers"):
                    for paper in resources["research_papers"]:
                        st.markdown(f"📄 [{paper['title']}]({paper['url']})")

# Download PDF Button
if st.button("Download PDF"):
    pdf_url = f"{BACKEND_URL}/api/download_pdf/"
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        st.download_button(
            label="📥 Download PDF",
            data=response.content,
            file_name="Research_Report.pdf",
            mime="application/pdf"
        )
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error downloading the file: {e}")
