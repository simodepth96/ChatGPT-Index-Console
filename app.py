import streamlit as st

try:
    from openai import OpenAI
    USE_NEW_IMPORT = True
except ImportError:
    import openai
    USE_NEW_IMPORT = False

# Page configuration
st.set_page_config(
    page_title="OpenAI URL Inspection Tool",
    page_icon="🔍",
    layout="wide"
)

# Sidebar for API key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password"
)

st.title("🔍 OpenAI URL Inspection Tool")

url = st.text_input("Enter URL to test:", placeholder="https://example.com")

check_type = st.selectbox(
    "Select check type:",
    ["Check if cached", "Force ChatGPT Research"]
)

if st.button("Run Check", disabled=not api_key or not url):
    try:
        if USE_NEW_IMPORT:
            client = OpenAI(api_key=api_key)
        else:
            client = openai.OpenAI(api_key=api_key)

        external_web_access = check_type == "Force ChatGPT Research"

        user_location = {
            "type": "approximate",
            "country": "GB",
            "city": "London",
            "region": "London",
        }

        with st.spinner("Checking URL..."):
            response = client.responses.create(
                model="gpt-5",
                tools=[{
                    "type": "web_search",
                    "external_web_access": external_web_access
                }],
                tool_choice="auto",
                input=f"Read this page {url} and summarise whether you can access it.",
                user_location=user_location
            )

        output_text = response.output_text

        st.subheader("Response from OpenAI")
        st.info(output_text)

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.info("Check API key or model access.")
