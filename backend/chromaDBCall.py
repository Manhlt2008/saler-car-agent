import os
import chromadb
from config import client, embedding_client
from databaseCars import database_cars

OPENAI_EMBEDDING_API_KEY = os.getenv("OPENAI_EMBEDDING_API_KEY")
OPENAI_EMBEDDING_ENDPOINT = os.getenv("OPENAI_EMBEDDING_ENDPOINT")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
# ---- LLM CONFIG ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

# ---- GET EMBEDDING ----
def get_embedding(text):
    response = embedding_client.embeddings.create(input=text, model=OPENAI_EMBEDDING_MODEL)
    return response.data[0].embedding

# ---- CALL LLM ----
def ask_llm(context, user_input):
    system_prompt = """Bạn là một chuyên gia sale trong lĩnh vực mua bán xe hơi.
        Nếu như câu hỏi là những thứ ngoài lĩnh vực này thì hãy trả lời là:
        Xin lỗi bạn đây là câu hỏi nằm ngoài lĩnh vực của tôi. Xin hãy đặt lại câu hỏi."""
    user_prompt = (
        f"Yêu cầu người dùng: {user_input}\n\n"
        f"Xe đề xuất:\n{context}\n\n"
        "Dựa vào yêu cầu bên trên và thông tin xe đã cho, hãy đề xuất chiếc xe phù hợp nhất với người dùng."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = client.chat.completions.create(model=DEPLOYMENT_NAME, messages=messages)
    return response.choices[0].message.content


# ---- CHROMADB ----
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="database_cars")

# ---- ADD CAR TO CHROMADB ----
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
    collection.add(
        embeddings=[embedding],
        documents=[car["features"]],
        ids=[car["id"]],
        metadatas=[{"name": car["name"], 
                    "brand": car["brand"], 
                    "image": car["image_url"], 
                    "segment": car["segment"], 
                    "seats": car["seats"], 
                    "transmission": car["transmission"] , 
                    "fuel_type": car["fuel_type"] ,
                    "engine_power": car["engine_power"] }],
    )


def build_context(results, n_context=3):
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    context_str = ""
    for doc, meta in zip(docs, metas):
        context_str += (
            f"Tên: {meta['name']}\n"
            f"Mô tả: {doc}\n"
            f"Hãng: {meta['brand']}\n"
            f"Loại: {meta['segment']}\n"
            f"Số ghế: {meta['seats']}\n"
            f"Nhiên liệu: {meta['fuel_type']}\n"
            f"Hộp số: {meta['transmission']}\n"
            f"Mã lực: {meta['engine_power']}\n"
            f"Hình ảnh: {meta['image']}\n\n"
        )
    return context_str.strip()


def callChromaDB(user_input):
    userInput = user_input[-1]["content"]
    query_embedding = get_embedding(userInput)
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    context = build_context(results)
    llm_output = ask_llm(context, user_input)
    return llm_output