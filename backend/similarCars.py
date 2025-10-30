import os
from config import embedding_client
from databaseCars import database_cars
from pinecone import Pinecone, ServerlessSpec

# Step 1:
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Step 2: Create or connect to an index
index_name = "product-similarity-index"
if index_name not in [index["name"] for index in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=1536,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    ) # dimension matches text-embedding-3-small output size
index = pc.Index(index_name)

# Step 3: Upsert sample product vectors into the index
def get_embedding(text):
    response = embedding_client.embeddings.create(
        input=text, model=os.getenv("OPENAI_EMBEDDING_MODEL")
    )
    return response.data[0].embedding
vectors = []
for car in database_cars:
    var_embedding = f"""name: {car['name']} 
                    brand: {car['brand']}
                    price_min: {car['price_min']}
                    price_max: {car['price_max']}
                    segment: {car['segment']}
                    seats: {car['seats']}
                    fuel_type: {car['fuel_type']}
                    transmission: {car['transmission']}
                    """
    embedding = get_embedding(var_embedding)
    vectors.append((car["id"], embedding))
index.upsert(vectors)

def callPinecone(user_input):
    prompt = user_input[-1]["content"]
    query_embedding = get_embedding(prompt)
    top_k = 5
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=False)
    response = "Top 5 xe phù hợp với yêu cầu của bạn là\n\n"
    for match in results.matches:
        product_id = match.id
        score = match.score
        car = next(car for car in database_cars if car["id"] == product_id)
        response += f"- {car['name']}:\n   {car['features']}\n\n"
    return response