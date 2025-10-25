import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import config
import json
import requests
from duckduckgo_search import DDGS
from llama_cpp import Llama
import chromadb

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url=os.getenv("OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

modelName = os.getenv("DEPLOYMENT_NAME")


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        prompt_message_list = data.get("promptMessageList", "")

        isFunctionCall = data.get("isFunctionCall", False)
        isDatabaseQuery = data.get("isDatabaseQuery", False)
        if isFunctionCall:
            function_call_response = function_call(prompt_message_list)
            return jsonify(function_call_response)
        elif isDatabaseQuery:
            print("Calling ChromaDB...")
            print("User Input:", prompt_message_list)
            llm_response = callChromaDB(prompt_message_list)
            return jsonify({"response": llm_response})
        # if not message_list:
        #     return jsonify({'error': 'Message is required'}), 400

        response = client.chat.completions.create(
            model=modelName, messages=prompt_message_list
        )

        assistant_message = response.choices[0].message.content
        return jsonify({"response": assistant_message})
        # use llama model to re write the response , but it is too slow, so comment it out
        # model_file_path = 'llama-2-7b-chat.Q4_K_M.gguf'
        # llama_model = LlamaModel(model_file_path)
        # rs_chatText = llama_model.re_write_response(assistant_message)
        # return jsonify({
        #     'response': rs_chatText
        # })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def function_call(messages):
    function_definition = [
        {
            "type": "function",
            "function": {
                "name": "get_car_details",
                "description": "Retrieve image url(s) for a specific car model. Call with {'query': 'make model year', 'imageCount': 1}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (car make/model) to find a real image",
                        },
                        "imageCount": {
                            "type": "integer",
                            "description": "Number of images to return",
                            "default": 1,
                        },
                    },
                    "required": ["query"],
                },
                "result": {
                    "type": "object",
                    "properties": {
                        "images": {"type": "array", "items": {"type": "string"}}
                    },
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=modelName,
        messages=messages,
        # Add the function definition
        tools=function_definition,
        # Specify the function to be called for the response
        tool_choice={"type": "function", "function": {"name": "get_car_details"}},
    )
    # return response.choices[0].message.tool_calls[0].function.arguments

    queryImageObjectResponse = (
        response.choices[0].message.tool_calls[0].function.arguments
    )
    queryImageObject = json.loads(queryImageObjectResponse)
    try:
        images = get_car_image(queryImageObject.get("query"))
        return {"images": images, "response": ""}
    except Exception as e:
        return {
            "error": str(e),
            "response": "",
            "images": "https://vinfastvietnam.net.vn/uploads/data/3097/files/files/vf6/z5399795928209_497b18168c84c3c6bd3d779b53eac21d.jpg",
        }


def get_car_image(query):
    """Get the first image URL for the given search text using DuckDuckGo."""
    with DDGS() as ddgs:
        results = ddgs.images(query, max_results=1)
        for r in results:
            return r["image"]  # The direct image URL
    return None


# function   re_write_response use llama model to re write the response
class LlamaModel:
    def __init__(self, model_path, n_ctx=512):
        """
        Initializes the Llama model.
        Args:
        model_path (str): The path to the LLaMA model file.
        n_ctx (int): The context size.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        try:
            self.llm = Llama(model_path=model_path, n_ctx=n_ctx)
            print(f"LLaMA model loaded successfully from {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load LLaMA model: {e}")

    def re_write_response(self, text):
        print("Rewriting response using LLaMA model...")
        try:
            # llama_model = LlamaModel(model_file_path)
            prompt_text = (
                "Rewrite the following text to be more engaging and informative: "
                + text
            )
            output = self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that rewrites text.",
                    },
                    {"role": "user", "content": prompt_text},
                ],
                # Specify output format to JSON
                response_format={
                    "type": "json_object",
                },
            )
            # print(f"Raw output from LLaMA model: {output}")
            return output["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {e}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


# use chromadb
OPENAI_EMBEDDING_API_KEY = os.getenv("OPENAI_EMBEDDING_API_KEY")
OPENAI_EMBEDDING_ENDPOINT = os.getenv("OPENAI_EMBEDDING_ENDPOINT")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL")
# ---- LLM CONFIG ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
# ---- CLIENTS ----
embedding_client = OpenAI(
    base_url=os.getenv("OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_EMBEDDING_API_KEY"),
)


# ---- GET EMBEDDING ----
def get_embedding(text):
    response = embedding_client.embeddings.create(input=text, model=OPENAI_EMBED_MODEL)
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

# --------- Add Sample data cars ---------
database_cars = [
    {
        "id": "1",
        "name": "Toyota Vios 1.5G CVT",
        "brand": "Toyota",
        "price_min": 520000000,
        "price_max": 620000000,
        "segment": "Sedan",
        "seats": 5,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "107 mã lực",
        "features": "Phanh ABS, cân bằng điện tử, camera lùi, điều hòa tự động",
        "image_url": "https://imgcdn.zigwheels.ph/large/gallery/exterior/30/1943/toyota-vios-front-angle-low-view-945824.jpg",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "2",
        "name": "Honda City RS",
        "brand": "Honda",
        "price_min": 580000000,
        "price_max": 680000000,
        "segment": "Sedan",
        "seats": 5,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "119 mã lực",
        "features": "Đèn LED, kiểm soát hành trình, cảm biến lùi, Apple CarPlay",
        "image_url": "https://hondaphuctho.vn/wp-content/uploads/2024/08/gioi-thieu-city-rs.jpg",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "3",
        "name": "Hyundai Tucson 2.0 Premium",
        "brand": "Hyundai",
        "price_min": 900000000,
        "price_max": 1000000000,
        "segment": "SUV",
        "seats": 5,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "154 mã lực",
        "features": "Ghế da, cửa sổ trời, hỗ trợ đổ đèo, phanh tay điện tử",
        "image_url": "https://www.topgear.com/sites/default/files/cars-road-test/carousel/2015/07/Large%20Image_0.jpg?w=1784&h=1004",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "4",
        "name": "Mazda CX-5 2.0 Luxury",
        "brand": "Mazda",
        "price_min": 850000000,
        "price_max": 990000000,
        "segment": "SUV",
        "seats": 5,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "154 mã lực",
        "features": "Cảnh báo điểm mù, giữ làn đường, i-Stop, khởi động nút bấm",
        "image_url": "https://hips.hearstapps.com/hmg-prod/images/2025-mazda-cx-5-front-three-quarters-2-67a23acb1d56f.jpg?crop=0.693xw:0.673xh;0.307xw,0.310xh",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "5",
        "name": "VinFast Lux A2.0",
        "brand": "VinFast",
        "price_min": 900000000,
        "price_max": 1100000000,
        "segment": "Sedan",
        "seats": 5,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "228 mã lực",
        "features": "Hệ thống giải trí 10 inch, 6 túi khí, cảm biến va chạm quanh xe",
        "image_url": "https://i1-vnexpress.vnecdn.net/2021/09/18/VinFastLuxA2020VnExpress3732854361601378665jpg-1631937165.jpg?w=750&h=450&q=100&dpr=1&fit=crop&s=yn4bLpjST_ByIUMMxbjrzA",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "6",
        "name": "Kia Morning GT-Line",
        "brand": "Kia",
        "price_min": 450000000,
        "price_max": 520000000,
        "segment": "Hatchback",
        "seats": 5,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "83 mã lực",
        "features": "Đèn pha LED, cảm biến đỗ xe, ghế da thể thao, camera lùi",
        "image_url": "https://imgcdn.zigwheels.vn/large/gallery/exterior/12/83/kia-morning-front-angle-low-view-953115.jpg",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "7",
        "name": "Ford Ranger Wildtrak 2.0 Bi-Turbo",
        "brand": "Ford",
        "price_min": 1100000000,
        "price_max": 1300000000,
        "segment": "Bán tải",
        "seats": 5,
        "fuel_type": "Dầu",
        "transmission": "Tự động",
        "engine_power": "210 mã lực",
        "features": "Dẫn động 4 bánh, khóa vi sai, cảnh báo lệch làn, kiểm soát đổ đèo",
        "image_url": "https://media.drive.com.au/obj/tx_q:70,rs:auto:1600:900:1/driveau/upload/cms/uploads/HErmomORtWMsWUXHjGLA",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "8",
        "name": "Mitsubishi Xpander Cross",
        "brand": "Mitsubishi",
        "price_min": 700000000,
        "price_max": 800000000,
        "segment": "MPV",
        "seats": 7,
        "fuel_type": "Xăng",
        "transmission": "Tự động",
        "engine_power": "104 mã lực",
        "features": "Cân bằng điện tử, hỗ trợ khởi hành ngang dốc, đèn LED ban ngày",
        "image_url": "https://img.autocarindia.com/ExtraImages/20191112043723_xpand2.jpg?w=700&c=1",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "9",
        "name": "Tesla Model 3 Standard Range Plus",
        "brand": "Tesla",
        "price_min": 1600000000,
        "price_max": 1900000000,
        "segment": "Sedan",
        "seats": 5,
        "fuel_type": "Điện",
        "transmission": "Tự động",
        "engine_power": "283 mã lực",
        "features": "Tự lái Autopilot, màn hình 15 inch, không cần chìa khóa vật lý",
        "image_url": "https://cimg1.ibsrv.net/ibimg/hgm/300x169-1/100/689/2019-tesla-model-3_100689077.jpg",
        "created_at": "2025-10-25T10:00:00",
    },
    {
        "id": "10",
        "name": "Toyota Corolla Cross Hybrid",
        "brand": "Toyota",
        "price_min": 930000000,
        "price_max": 1050000000,
        "segment": "SUV",
        "seats": 5,
        "fuel_type": "Hybrid",
        "transmission": "Tự động",
        "engine_power": "138 mã lực",
        "features": "Động cơ hybrid tiết kiệm, ga tự động thích ứng, cảnh báo va chạm",
        "image_url": "https://images.hgmsites.net/hug/2023-toyota-corolla-cross-hybrid_100880816_h.jpg",
        "created_at": "2025-10-25T10:00:00",
    },
]
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
        metadatas=[{"name": car["name"], "brand": car["brand"], "image": car["image_url"]}],
    )


def build_context(results, n_context=3):
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    context_str = ""
    for doc, meta in zip(docs, metas):
        context_str += (
            f"Name: {meta['name']}\n"
            f"Description: {doc}\n"
            f"Brand: {meta['brand']}\n"
            f"Image: {meta['image']}\n\n"
        )
    return context_str.strip()


def callChromaDB(user_input):
    userInput = user_input[-1]["content"]
    query_embedding = get_embedding(userInput)
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    # Step 2: Build context for LLM
    context = build_context(results)
    # Step 3: Get recommendation from LLM
    llm_output = ask_llm(context, user_input)
    return llm_output


if __name__ == "__main__":
    # If any frontend env value contains 'localhost' (or 127.0.0.1), bind to
    # localhost:3000 so the backend runs on the same local host/port as the FE dev server.
    frontend_values = " ".join(
        filter(
            None,
            [
                os.getenv("FRONTEND_HOST") or "",
                os.getenv("FRONTEND_URL") or "",
                os.getenv("REACT_APP_FRONTEND_URL") or "",
                os.getenv("VITE_APP_BASE_URL") or "",
            ],
        )
    ).lower()

    if "localhost" in frontend_values or "127.0.0.1" in frontend_values:
        app.run(host="localhost", port=3000, debug=True)
    else:
        # Do not explicitly set host/port so Flask uses defaults or values
        # provided through environment (FLASK_RUN_HOST/FLASK_RUN_PORT) or
        # deployment platform settings. This avoids attempting to bind to a
        # remote domain (e.g. somedomain.vercel.app).
        app.run(debug=True)
