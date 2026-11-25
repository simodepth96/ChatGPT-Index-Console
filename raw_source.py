import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


test_1 = client.responses.create(
    model="gpt-6-luna",
    reasoning={"effort": "low"},
    tools=[{
        "type": "web_search",
        "external_web_access": False,  # cached/indexed only, no live fetch
        "user_location": {
            "type": "approximate",
            "country": "GB",
            "city": "London",
            "region": "London",
        },
    }],
    tool_choice="auto",
    include=["web_search_call.action.sources"],
    input=f"Can you access this page? {url} If you can, make a summary.",
)

print(test_1.output_text)

# Raw sources, to confirm what came from the cached index
for item in test_1.output:
    if item.type == "web_search_call":
        for s in getattr(item.action, "sources", []) or []:
            print(s.url)
