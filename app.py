import os
import streamlit as st

# Try to import openai - use the same pattern as the working example
try:
    import openai
    from openai import OpenAI
except ImportError as e:
    st.error(f"""
    ❌ Failed to import OpenAI module.
    
    Error: {str(e)}
    
    Please ensure requirements.txt contains:
    ```
    streamlit
    openai
    ```
    """)
    st.stop()

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
    type="password", 
    help="Enter your OpenAI API key",
    value=os.environ.get("OPENAI_API_KEY", "")
)

# Main content
st.title("🔍 OpenAI URL Inspection Tool")

st.markdown("""
This app is a rough attempt to create URL inspection tool for OpenAI.
It checks whether a page URL is cached in OpenAI's index or requires grounding to synthesize an AI answer. 
The app relies on a fixed IP user location set in the UK (London) as it was found providing more granular and precise output.

More details – [OpenAI Web Search Documentation](https://platform.openai.com/docs/guides/tools-web-search#live-internet-access)
""")

st.markdown("---")

# URL input
url = st.text_input(
    "Enter URL to test:", 
    placeholder="https://example.com", 
    help="Paste the URL you want to check"
)

# Dropdown for check type
check_type = st.selectbox(
    "Select check type:",
    ["Check if cached", "Force ChatGPT Research"],
    help="Choose whether to check cached content or force live research"
)

# Run button
if st.button("Run Check", type="primary", disabled=not api_key or not url):
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar")
    elif not url:
        st.error("⚠️ Please enter a URL to test")
    else:
        try:
            with st.status("Checking URL...", expanded=True) as status_box:
                # Initialize OpenAI client (using the same pattern as working example)
                openai_client = openai.Client(api_key=api_key)
                
                # Set external_web_access based on check type
                external_web_access = check_type == "Force a Live search"
                
                # User location (fixed to London, UK)
                user_location = {
                    "type": "approximate",
                    "country": "GB",
                    "city": "London",
                    "region": "London",
                }
                
                status_box.update(label="Making API request...", state="running")
                
                # Make API call (user_location is defined but not used in the API call)
                # This matches the working Colab script pattern
                user_location = {
                    "type": "approximate",
                    "country": "GB",
                    "city": "London",
                    "region": "London",
                }
                
                response = openai_client.responses.create(
                    model="gpt-5",
                    tools=[{
                        "type": "web_search",
                        "external_web_access": external_web_access
                    }],
                    tool_choice="auto",
                    input=f"Read this page {url} and make a summary, on if you can access it."
                )
                
                status_box.update(label="Complete", state="complete")
                
                # Get response text
                output_text = response.output_text
                
                # Display raw response
                st.subheader("Response from OpenAI:")
                st.info(output_text)
                
                # Interpret results
                st.subheader("Interpretation:")
                
                if output_text.startswith("Yes—I can access it") or output_text.startswith("I can access the page"):
                    st.success("""
                    ✅ **ChatGPT-User was not prevented by JavaScript blockers and surfaced a cached raw HTML to synthesize a likely answer in the live chat.**
                    
                    ChatGPT is familiar with your page and there may be little to no optimisation efforts for you take on.
                    """)
                elif output_text.startswith("I can't access"):
                    st.warning("""
                    ⚠️ **ChatGPT-User may have been prevented by JavaScript blockers (CSR geo-location pop-ups e.g;) or the page simply couldn't be found in OpenAI's cached index.**
                    
                    Consider reviewing blocking CSR JavaScript and increase mentions and citations via targeted Digital PR efforts.
                    """)
                else:
                    st.info("The response doesn't match expected patterns. Please review the raw output above.")
                    
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please check your API key and try again. Make sure you have access to the GPT-5 model and the responses API.")

# Instructions
with st.expander("ℹ️ How to use this tool"):
    st.markdown("""
    1. **Enter your OpenAI API Key** in the sidebar (required)
       - Or set it as an environment variable: `OPENAI_API_KEY`
    2. **Paste the URL** you want to test in the input field
    3. **Select the check type:**
       - **Check if page is cached**: Tests if the URL is in OpenAI's cache (external_web_access: False) and provides interpretation
       - **Force a Live search**: Forces live web search (external_web_access: True) without interpretation
    4. **Click "Run Check"** to test the URL
    5. Review the results (and interpretation if checking cache)
    
    **Note:** This tool uses a fixed UK (London) location for more consistent results.
    """)

# Footer
st.markdown("---")
st.caption("Delivered by Simone De Palma for [SEODepths](https://seodepths.com)")
