from config import initKey, initClients
initKey()
initClients()
from config import client

import os
import uuid
from flask_cors import CORS
from similarCars import callPinecone
from chromaDBCall import callChromaDB
from functionCalling import function_call
from langchainSearch import callTavilySearch
from flask import Flask, request, jsonify, send_from_directory
from audio import empty_audio, request_audio, folder, get_file_name_by_id

app = Flask(__name__)
CORS(app)
modelName = os.getenv("DEPLOYMENT_NAME")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        prompt_message_list = data.get("promptMessageList", "")
        isFunctionCall = data.get("isFunctionCall", False)
        isDatabaseQuery = data.get("isDatabaseQuery", False)
        isSimilarCarQuery = data.get("isSimilarCarQuery", False)
        isLangchainSearch = data.get("isLangchainSearch", False)

        # prompt_message_list[-1]["content"]+=". Câu trả lời thêm nhiều emoticon sinh động"

        if isLangchainSearch:
            response = callTavilySearch(prompt_message_list)
            id = uuid.uuid1()
            return jsonify({"response": { "message":response, "id":id}})

        elif isFunctionCall:
            function_call_response = function_call(prompt_message_list)
            # if (function_call_response["response"]):
            #     request_audio(function_call_response.response.message, function_call_response.response.message.id)
            return jsonify(function_call_response)
        
        elif isDatabaseQuery:
            response = callChromaDB(prompt_message_list)
            id = uuid.uuid1()
            # request_audio(llm_response, id)
            return jsonify({"response": { "message":response, "id":id}})
        
        elif isSimilarCarQuery:
            response = callPinecone(prompt_message_list)
            id = uuid.uuid1()
            # request_audio(llm_response, id)
            return jsonify({"response": { "message":response, "id":id}})

        # if not message_list:
        #     return jsonify({'error': 'Message is required'}), 400

        response = client.chat.completions.create(
            model=modelName, messages=prompt_message_list
        )

        assistant_message = response.choices[0].message.content
        # request_audio(assistant_message, response.id)
        return jsonify({
            'response': {
                "message": assistant_message,
                "id": response.id
            },
        })
        # use llama model to re write the response , but it is too slow, so comment it out
        # model_file_path = 'llama-2-7b-chat.Q4_K_M.gguf'
        # llama_model = LlamaModel(model_file_path)
        # rs_chatText = llama_model.re_write_response(assistant_message)
        # return jsonify({
        #     'response': rs_chatText
        # })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/getaudio', methods=['POST'])
def getaudio():
    try:
        data = request.get_json()
        audio_id = data.get('id', '')
        text = data.get('text', '')
        return send_from_directory(folder, get_file_name_by_id(audio_id), mimetype="audio/wav")

    except Exception as e:
        try:
            request_audio(text, audio_id)
            return send_from_directory(folder, get_file_name_by_id(audio_id), mimetype="audio/wav")
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

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

    empty_audio()
    if 'localhost' in frontend_values or '127.0.0.1' in frontend_values:
        app.run(host='localhost', port=3000, debug=True)
    else:
        # Do not explicitly set host/port so Flask uses defaults or values
        # provided through environment (FLASK_RUN_HOST/FLASK_RUN_PORT) or
        # deployment platform settings. This avoids attempting to bind to a
        # remote domain (e.g. somedomain.vercel.app).
        app.run(debug=True)
