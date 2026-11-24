from openai import OpenAI

OPENAI_API_KEY = 'your_openai_key'
client = OpenAI(api_key=OPENAI_API_KEY)

test_1 = client.responses.create(
    model="gpt-6-luna",
    tools=[{ "type": "web_search", "external_web_access": False }],

    tool_choice="auto",
    input="Can you access this page? {url}  If you can, make a summary."
)

# Declare your IP location for more concise output
user_location={
        "type": "approximate",
        "country": "GB",
        "city": "London",
        "region": "London",
    }
print(test_1.output_text)
