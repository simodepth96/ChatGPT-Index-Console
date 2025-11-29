import streamlit as st
import sys
import subprocess

# Show diagnostic information
st.sidebar.header("🔍 Diagnostics")
st.sidebar.write("**Python Version:**", sys.version)
st.sidebar.write("**Python Path:**", sys.executable)

# Show installed packages
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True, timeout=10)
    st.sidebar.text_area("Installed Packages", result.stdout, height=200)
except Exception as e:
    st.sidebar.error(f"Could not list packages: {e}")

# Try to import OpenAI with error handling
try:
    from openai import OpenAI
    st.sidebar.success("✅ OpenAI imported successfully!")
except ImportError as e:
    st.error(f"""
    ❌ Failed to import OpenAI module.
    
    Error: {str(e)}
    
    **Check the diagnostics in the sidebar to see if openai is installed.**
    
    If openai is NOT in the package list, your requirements.txt is not being read.
    """)
    
    # Try to install it on the fly (won't persist, but helps diagnose)
    if st.button("🔧 Try Installing OpenAI Now"):
        with st.spinner("Installing openai..."):
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "openai==1.54.4"],
                    capture_output=True, text=True, timeout=60
                )
                st.code(result.stdout)
                if result.returncode == 0:
                    st.success("Installation completed! Refresh the page.")
                else:
                    st.error(result.stderr)
            except Exception as install_error:
                st.error(f"Installation failed: {install_error}")
    
    st.stop()

# Page configuration
st.set_page_config(
    page_title="OpenAI URL Inspection Tool",
    page_icon="🔍",
    layout="wide"
)

# Sidebar for API key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")

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
url = st.text_input("Enter URL to test:", placeholder="https://example.com", help="Paste the URL you want to check")

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
            with st.spinner("Checking URL..."):
                # Initialize OpenAI client
                client = OpenAI(api_key=api_key)
                
                # Set external_web_access based on check type
                external_web_access = check_type == "Force ChatGPT Research"
                
                # User location (fixed to London, UK)
                user_location = {
                    "type": "approximate",
                    "country": "GB",
                    "city": "London",
                    "region": "London",
                }
                
                # Make API call
                response = client.responses.create(
                    model="gpt-5",
                    tools=[{
                        "type": "web_search",
                        "external_web_access": external_web_access
                    }],
                    tool_choice="auto",
                    input=f"Read this page {url} and make a summary, on if you can access it.",
                    user_location=user_location
                )
                
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
    2. **Paste the URL** you want to test in the input field
    3. **Select the check type:**
       - **Check if cached**: Tests if the URL is in OpenAI's cache (external_web_access: False)
       - **Force ChatGPT Research**: Forces live web search (external_web_access: True)
    4. **Click "Run Check"** to test the URL
    5. Review the results and interpretation
    
    **Note:** This tool uses a fixed UK (London) location for more consistent results.
    """)

# Footer
st.markdown("---")
st.caption("OpenAI URL Inspection Tool | For SEO and content optimization research")
