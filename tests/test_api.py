from google import genai

#The client reads GEMINI_API_KEY from environment automatically
client = genai.Client(api_key="AIzaSyC0Mfv0AXRuPyzTteYhjuildYhZ8YJ4TEc")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is Irembo?"
)

print(response.text)