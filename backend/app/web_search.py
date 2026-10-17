import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv(override=True)

TRUSTED_DOMAINS = [
    "medlineplus.gov",
    "nhs.uk",
    "ncbi.nlm.nih.gov",
    "mayoclinic.org",
]

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query):
    response = client.search(
        query=query,
        max_results=3,
        include_domains=TRUSTED_DOMAINS,)
    return response["results"]


if __name__ == "__main__":
    for r in web_search("knee pain after running causes"):
        print(r["title"])
        print(r["url"])
        print(r["content"][:200])
        print()