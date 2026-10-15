import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"

def ask_llm(question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(ask_llm("In one sentence, what is plantar fasciitis?"))