from openai import OpenAI

# Initialize client
client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://genailab.tcs.in/"
)

# Choose model
MODEL = "genailab-maas-gpt-4o"  # you can swap this

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Explain why high CPU usage can slow down an application."}
    ],
    temperature=0.7
    """
    0.0 → very deterministic
    0.3 → focused
    0.7 → balanced (default-ish)
    1.0+ → creative / chaotic
    """

)

print(response.choices[0].message.content)