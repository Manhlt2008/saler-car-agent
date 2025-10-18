import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import config
import json
import requests
from duckduckgo_search import DDGS

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

modelName = os.getenv("AZURE_DEPLOYMENT_NAME")


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        prompt_message_list = data.get('promptMessageList', '')
        
        isFunctionCall = data.get('isFunctionCall', False)
        if isFunctionCall:
            function_call_response = function_call(prompt_message_list)
            return jsonify(function_call_response)
        
        # if not message_list:
        #     return jsonify({'error': 'Message is required'}), 400

        response = client.chat.completions.create(
            model=modelName,
            messages=prompt_message_list
        )

        assistant_message = response.choices[0].message.content

        return jsonify({
            'response': assistant_message
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def function_call(messages):
    function_definition = [{
        "type": "function",
        "function": {
            "name": "get_car_details",
            "description": "Retrieve image url(s) for a specific car model. Call with {'query': 'make model year', 'imageCount': 1}.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type":"string","description":"Search query (car make/model) to find a real image"},
                    "imageCount": {"type":"integer","description":"Number of images to return", "default": 1}
                },
                "required": ["query"]
            },
            "result": {"type":"object","properties":{"images":{"type":"array","items":{"type":"string"}}}}
        }
    }]
    response= client.chat.completions.create(
        model=modelName,
        messages=messages,
        # Add the function definition
        tools=function_definition,
        # Specify the function to be called for the response
        tool_choice={'type':'function','function':{'name':'get_car_details'}}
    )
    #return response.choices[0].message.tool_calls[0].function.arguments

    queryImageObjectResponse = response.choices[0].message.tool_calls[0].function.arguments
    queryImageObject =json.loads(queryImageObjectResponse)
    try:
        images = get_car_image(queryImageObject.get('query'))
        return {"images": images}
    except Exception as e:
        return {"error": str(e),"images": "https://vinfastvietnam.net.vn/uploads/data/3097/files/files/vf6/z5399795928209_497b18168c84c3c6bd3d779b53eac21d.jpg"}

def get_car_image(query):
    """Get the first image URL for the given search text using DuckDuckGo."""
    with DDGS() as ddgs:
        results = ddgs.images(query, max_results=1)
        for r in results:
            return r["image"]  # The direct image URL
    return None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3004, debug=True)
