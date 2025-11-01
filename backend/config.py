import os
from openai import OpenAI

def initKey():
    os.environ["OPENAI_ENDPOINT"] = "https://aiportalapi.stu-platform.live/jpe"
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["DEPLOYMENT_NAME"] = "GPT-4o-mini"

    os.environ["OPENAI_EMBEDDING_ENDPOINT"] = "https://aiportalapi.stu-platform.live/jpe"
    os.environ["OPENAI_EMBEDDING_API_KEY"] = ""
    os.environ["OPENAI_EMBEDDING_MODEL"] = "text-embedding-3-small"

    os.environ["PINECONE_API_KEY"] = ""
    os.environ["TAVILY_API_KEY"] = ""

client = None
embedding_client = None
def initClients():
    global client
    client = OpenAI(
        base_url=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    global embedding_client
    embedding_client = OpenAI(
        base_url=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_EMBEDDING_API_KEY"),
    )
    print("Clients initialized successfully")
