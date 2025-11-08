import os
import json
from llama_cpp import Llama
from duckduckgo_search import DDGS
from config import client
modelName = os.getenv("DEPLOYMENT_NAME")

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
        tool_choice={'type': 'function', 'function': {'name': 'get_car_details'}}
    )
    # return response.choices[0].message.tool_calls[0].function.arguments

    queryImageObjectResponse = response.choices[0].message.tool_calls[0].function.arguments
    queryImageObject = json.loads(queryImageObjectResponse)
    try:
        images = get_car_image(queryImageObject.get('query'))
        return {"images": images, "response": {"message": "", "id": response.id}, }
    except Exception as e:
        return {"error": str(e), 
                "response": "",
                "images": "https://giaxeotovinfast.net/wp-content/uploads/2023/01/312207264_637940821322100_2347147708676423923_n.jpg"}

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
            prompt_text = "Rewrite the following text to be more engaging and informative: " + text
            output = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that rewrites text."},
                    {"role": "user", "content": prompt_text}
                ],
                # Specify output format to JSON
                response_format={
                    "type": "json_object",
                })
            # print(f"Raw output from LLaMA model: {output}")
            return output['choices'][0]["message"]['content']
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {e}")
